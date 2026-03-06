"""PROC-1 deterministic process-run execution helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Set

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.chem.process_run_engine import build_batch_quality_row
from src.models.model_engine import (
    cache_policy_rows_by_id,
    constitutive_model_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
)
from src.process.maturity import (
    build_process_certificate_artifact_row,
    build_process_certificate_revocation_row,
    evaluate_process_maturity,
    process_capsule_eligibility_status,
    process_lifecycle_policy_rows_by_id,
    process_metrics_rows_by_key,
    stabilization_policy_rows_by_id,
    update_process_metrics_for_run,
)
from src.process.drift import (
    apply_revalidation_trial_result,
    build_drift_event_record_row,
    build_process_drift_state_row,
    drift_policy_rows_by_id,
    evaluate_process_drift,
    normalize_drift_event_record_rows,
    process_drift_rows_by_key,
    schedule_revalidation_trials,
)
from src.process.qc.qc_engine import evaluate_qc_for_run
from src.process.process_definition_validator import (
    REFUSAL_PROCESS_INVALID_DEFINITION,
    build_process_definition_row,
    process_step_rows_by_id,
    validate_process_definition,
)


REFUSAL_PROCESS_RUN_NOT_FOUND = "refusal.process.run_not_found"
REFUSAL_PROCESS_LEDGER_REQUIRED = "refusal.process.ledger_required"
REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION = "refusal.process.direct_mass_energy_mutation"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_process_quality_record_row(
    *,
    run_id: str,
    yield_factor: int,
    defect_flags: object,
    quality_grade: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "yield_factor": int(max(0, min(1000, _as_int(yield_factor, 0)))),
        "defect_flags": _tokens(defect_flags),
        "quality_grade": str(quality_grade or "").strip() or "grade.C",
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["run_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_process_run_record_row(*, run_id: str, process_id: str, version: str, start_tick: int, end_tick: int | None, status: str, input_refs: object, output_refs: object, deterministic_fingerprint: str = "", extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "process_id": str(process_id or "").strip(),
        "version": str(version or "").strip() or "1.0.0",
        "start_tick": int(max(0, _as_int(start_tick, 0))),
        "end_tick": (None if end_tick is None else int(max(0, _as_int(end_tick, 0)))),
        "status": str(status or "").strip().lower() or "running",
        "input_refs": [dict(row) for row in _as_list(input_refs) if isinstance(row, Mapping)],
        "output_refs": [dict(row) for row in _as_list(output_refs) if isinstance(row, Mapping)],
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["process_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_process_step_record_row(*, run_id: str, step_id: str, tick: int, status: str, deterministic_fingerprint: str = "", extensions: Mapping[str, object] | None = None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "run_id": str(run_id or "").strip(),
        "step_id": str(step_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "status": str(status or "").strip().lower() or "started",
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["run_id"]) or (not payload["step_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _deps(process_definition_row: Mapping[str, object]) -> Dict[str, List[str]]:
    graph = _as_map(_as_map(process_definition_row).get("step_graph"))
    steps = process_step_rows_by_id(_as_list(graph.get("steps")))
    out = dict((step_id, []) for step_id in sorted(steps.keys()))
    for edge in sorted((_as_map(row) for row in _as_list(graph.get("edges"))), key=lambda row: (str(row.get("to_step_id", "")), str(row.get("from_step_id", "")))):
        src = str(edge.get("from_step_id", "")).strip()
        dst = str(edge.get("to_step_id", "")).strip()
        if (src in out) and (dst in out):
            out[dst].append(src)
    return dict((key, sorted(set(value))) for key, value in out.items())


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(row) for row in _as_list(body.get(key)) if isinstance(row, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(row) for row in _as_list(record.get(key)) if isinstance(row, Mapping)]
    return []


def _yield_model_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, "yield_models")
    out: Dict[str, dict] = {}
    for row in rows:
        token = str(row.get("yield_model_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _defect_model_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, "defect_models")
    out: Dict[str, dict] = {}
    for row in rows:
        token = str(row.get("defect_model_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _qc_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(payload, "qc_policies")
    out: Dict[str, dict] = {}
    for row in rows:
        token = str(row.get("qc_policy_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _batch_ids_from_refs(ref_rows: object) -> List[str]:
    out: List[str] = []
    for row in [dict(item) for item in _as_list(ref_rows) if isinstance(item, Mapping)]:
        ref_type = str(row.get("ref_type", "")).strip().lower()
        ref_id = str(row.get("ref_id", "")).strip()
        if not ref_id:
            continue
        if ref_type == "batch" or ref_id.startswith("batch."):
            out.append(ref_id)
    return _tokens(out)


def _quality_input_resolver(input_ref: Mapping[str, object], binding: Mapping[str, object]) -> object:
    input_id = str(_as_map(input_ref).get("input_id", "")).strip()
    params = _as_map(_as_map(binding).get("parameters"))
    mapping = {
        "field.temperature": int(_as_int(params.get("temperature", 29315), 29315)),
        "quantity.pressure_head": int(max(0, _as_int(params.get("pressure_head", 0), 0))),
        "quantity.entropy_index": int(max(0, _as_int(params.get("entropy_index", 0), 0))),
        "derived.process.tool_wear_permille": int(max(0, min(1000, _as_int(params.get("tool_wear_permille", 0), 0)))),
        "derived.process.input_batch_quality_permille": int(max(0, min(1000, _as_int(params.get("input_batch_quality_permille", 900), 900)))),
        "derived.process.spec_score_permille": int(max(0, min(1000, _as_int(params.get("spec_score_permille", 1000), 1000)))),
        "derived.process.calibration_state_permille": int(max(0, min(1000, _as_int(params.get("calibration_state_permille", 1000), 1000)))),
        "derived.process.run_id": str(params.get("run_id", "")).strip(),
        "derived.process.step_id": str(params.get("step_id", "")).strip(),
        "derived.process.tick": int(max(0, _as_int(params.get("tick", 0), 0))),
    }
    if input_id in mapping:
        return mapping[input_id]
    if input_id in params:
        return params.get(input_id)
    return 0


def _evaluate_process_quality(
    *,
    current_tick: int,
    run_id: str,
    process_id: str,
    process_version: str,
    yield_model_id: str,
    defect_model_id: str,
    output_batch_ids: List[str],
    input_batch_ids: List[str],
    quality_inputs: Mapping[str, object] | None,
    stochastic_quality_enabled: bool,
    yield_model_registry_payload: Mapping[str, object] | None,
    defect_model_registry_payload: Mapping[str, object] | None,
    constitutive_model_registry_payload: Mapping[str, object] | None,
    model_type_registry_payload: Mapping[str, object] | None,
    model_cache_policy_registry_payload: Mapping[str, object] | None,
    cache_rows: object,
) -> dict:
    inputs = _as_map(quality_inputs)
    yield_registry = _yield_model_rows_by_id(yield_model_registry_payload)
    defect_registry = _defect_model_rows_by_id(defect_model_registry_payload)
    yield_row = dict(yield_registry.get(str(yield_model_id).strip()) or {})
    defect_row = dict(defect_registry.get(str(defect_model_id).strip()) or {})
    if not yield_row or not defect_row:
        return {
            "result": "skipped",
            "reason": "missing_model_registry_row",
            "yield_factor": 1000,
            "defect_flags": [],
            "quality_grade": "grade.A",
            "error_estimate_permille": 0,
            "evaluation_results": [],
            "output_actions": [],
            "cache_rows": [dict(row) for row in _as_list(cache_rows) if isinstance(row, Mapping)],
        }

    model_rows_by_id = constitutive_model_rows_by_id(constitutive_model_registry_payload)
    yield_model_ref = str(yield_row.get("model_id", "")).strip()
    defect_model_ref = str(defect_row.get("model_id", "")).strip()
    if (yield_model_ref not in model_rows_by_id) or (defect_model_ref not in model_rows_by_id):
        return {
            "result": "skipped",
            "reason": "missing_constitutive_model_row",
            "yield_factor": 1000,
            "defect_flags": [],
            "quality_grade": "grade.A",
            "error_estimate_permille": 0,
            "evaluation_results": [],
            "output_actions": [],
            "cache_rows": [dict(row) for row in _as_list(cache_rows) if isinstance(row, Mapping)],
        }

    use_yield_rng = bool(stochastic_quality_enabled) and bool(yield_row.get("stochastic_allowed", False))
    use_defect_rng = bool(stochastic_quality_enabled) and bool(defect_row.get("stochastic_allowed", False))
    tick = int(max(0, _as_int(current_tick, 0)))
    quality_step_id = "step.quality.finalize"
    parameters_base = {
        "temperature": int(_as_int(inputs.get("temperature", 29315), 29315)),
        "pressure_head": int(max(0, _as_int(inputs.get("pressure_head", 0), 0))),
        "entropy_index": int(max(0, _as_int(inputs.get("entropy_index", 0), 0))),
        "tool_wear_permille": int(max(0, min(1000, _as_int(inputs.get("tool_wear_permille", 0), 0)))),
        "input_batch_quality_permille": int(max(0, min(1000, _as_int(inputs.get("input_batch_quality_permille", 900), 900)))),
        "spec_score_permille": int(max(0, min(1000, _as_int(inputs.get("spec_score_permille", 1000), 1000)))),
        "calibration_state_permille": int(max(0, min(1000, _as_int(inputs.get("calibration_state_permille", 1000), 1000)))),
        "run_id": str(run_id),
        "step_id": str(quality_step_id),
        "tick": int(tick),
        "process_id": str(process_id),
        "process_version": str(process_version),
        "output_batch_ids": list(output_batch_ids),
        "input_batch_ids": list(input_batch_ids),
    }
    binding_rows = [
        {
            "binding_id": "binding.proc2.yield.{}".format(str(run_id)),
            "model_id": str(yield_model_ref),
            "target_kind": "custom",
            "target_id": str(run_id),
            "tier": "macro",
            "parameters": dict(
                parameters_base,
                stochastic_allowed=bool(use_yield_rng),
                rng_stream_name=(str(yield_row.get("rng_stream_name", "")).strip() if use_yield_rng else ""),
            ),
            "enabled": True,
            "extensions": {},
        },
        {
            "binding_id": "binding.proc2.defect.{}".format(str(run_id)),
            "model_id": str(defect_model_ref),
            "target_kind": "custom",
            "target_id": str(run_id),
            "tier": "macro",
            "parameters": dict(
                parameters_base,
                stochastic_allowed=bool(use_defect_rng),
                rng_stream_name=(str(defect_row.get("rng_stream_name", "")).strip() if use_defect_rng else ""),
            ),
            "enabled": True,
            "extensions": {},
        },
    ]
    eval_result = evaluate_model_bindings(
        current_tick=int(tick),
        model_rows=[dict(model_rows_by_id[yield_model_ref]), dict(model_rows_by_id[defect_model_ref])],
        binding_rows=binding_rows,
        cache_rows=[dict(row) for row in _as_list(cache_rows) if isinstance(row, Mapping)],
        model_type_rows=model_type_rows_by_id(model_type_registry_payload),
        cache_policy_rows=cache_policy_rows_by_id(model_cache_policy_registry_payload),
        input_resolver_fn=_quality_input_resolver,
        max_cost_units=16,
    )
    output_actions = [dict(row) for row in _as_list(eval_result.get("output_actions")) if isinstance(row, Mapping)]

    yield_factor = 1000
    quality_grade = "grade.A"
    error_estimate = 0
    defect_flags: List[str] = []
    defect_severity = 0
    contamination_tags: List[str] = []
    rng_rows: List[dict] = []

    for row in output_actions:
        payload = _as_map(row.get("payload"))
        output_id = str(row.get("output_id", "")).strip().lower()
        if "yield_factor" in output_id:
            yield_factor = int(max(0, min(1000, _as_int(payload.get("yield_factor_permille", payload.get("value", yield_factor)), yield_factor))))
            error_estimate = int(max(0, min(1000, _as_int(payload.get("error_estimate_permille", error_estimate), error_estimate))))
            grade = str(payload.get("quality_grade", "")).strip()
            if grade:
                quality_grade = grade
        elif "quality_grade" in output_id:
            grade = str(payload.get("quality_grade", payload.get("value", quality_grade))).strip()
            if grade:
                quality_grade = grade
        elif "error_estimate" in output_id:
            error_estimate = int(max(0, min(1000, _as_int(payload.get("value", error_estimate), error_estimate))))
        if "defect_flags" in output_id or isinstance(payload.get("defect_flags"), list):
            defect_flags = _tokens(list(payload.get("defect_flags", defect_flags)))
            defect_severity = int(max(0, min(1000, _as_int(payload.get("defect_severity", defect_severity), defect_severity))))
            contamination_tags = _tokens(list(payload.get("contamination_tags", contamination_tags)))
        if payload.get("stochastic_allowed") and str(payload.get("rng_stream_name", "")).strip():
            rng_rows.append(
                {
                    "run_id": str(run_id),
                    "model_id": str(row.get("model_id", "")).strip(),
                    "rng_stream_name": str(payload.get("rng_stream_name", "")).strip(),
                    "rng_seed_hash": str(payload.get("rng_seed_hash", "")).strip(),
                    "tick": int(tick),
                }
            )

    if not defect_flags and defect_severity <= 0:
        defect_flags = []
    if not contamination_tags and ("contamination" in set(defect_flags)):
        contamination_tags = ["contamination.process"]

    if str(quality_grade).strip() not in {"grade.A", "grade.B", "grade.C"}:
        quality_grade = "grade.C" if yield_factor < 760 else "grade.B"
        if yield_factor >= 900 and not defect_flags:
            quality_grade = "grade.A"

    return {
        "result": "complete",
        "reason": "",
        "yield_factor": int(max(0, min(1000, yield_factor))),
        "defect_flags": _tokens(defect_flags),
        "quality_grade": str(quality_grade),
        "error_estimate_permille": int(max(0, min(1000, error_estimate))),
        "defect_severity": int(max(0, min(1000, defect_severity))),
        "contamination_tags": _tokens(contamination_tags),
        "evaluation_results": [dict(row) for row in _as_list(eval_result.get("evaluation_results")) if isinstance(row, Mapping)],
        "output_actions": output_actions,
        "cache_rows": [dict(row) for row in _as_list(eval_result.get("cache_rows")) if isinstance(row, Mapping)],
        "rng_rows": [dict(row) for row in _as_list(rng_rows) if isinstance(row, Mapping)],
    }


def process_run_start(
    *,
    current_tick: int,
    process_definition_row: Mapping[str, object],
    action_template_registry_payload: Mapping[str, object] | None,
    temporal_domain_registry_payload: Mapping[str, object] | None,
    input_refs: object,
    run_id: str | None = None,
    qc_policy_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    definition = build_process_definition_row(
        process_id=str(_as_map(process_definition_row).get("process_id", "")).strip(),
        version=str(_as_map(process_definition_row).get("version", "")).strip() or "1.0.0",
        description=str(_as_map(process_definition_row).get("description", "")).strip(),
        step_graph=_as_map(process_definition_row).get("step_graph"),
        input_signature=_as_map(process_definition_row).get("input_signature"),
        output_signature=_as_map(process_definition_row).get("output_signature"),
        required_tools=_as_map(process_definition_row).get("required_tools"),
        required_environment=_as_map(process_definition_row).get("required_environment"),
        tier_contract_id=str(_as_map(process_definition_row).get("tier_contract_id", "")).strip(),
        coupling_budget_id=str(_as_map(process_definition_row).get("coupling_budget_id", "")).strip() or None,
        qc_policy_id=str(_as_map(process_definition_row).get("qc_policy_id", "")).strip() or None,
        stabilization_policy_id=str(_as_map(process_definition_row).get("stabilization_policy_id", "")).strip() or None,
        process_lifecycle_policy_id=str(_as_map(process_definition_row).get("process_lifecycle_policy_id", "")).strip() or None,
        process_cert_type_id=str(_as_map(process_definition_row).get("process_cert_type_id", "")).strip() or None,
        drift_policy_id=str(_as_map(process_definition_row).get("drift_policy_id", "")).strip() or None,
        yield_model_id=str(_as_map(process_definition_row).get("yield_model_id", "")).strip() or None,
        defect_model_id=str(_as_map(process_definition_row).get("defect_model_id", "")).strip() or None,
        deterministic_fingerprint=str(_as_map(process_definition_row).get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(_as_map(process_definition_row).get("extensions")),
    )
    validation = validate_process_definition(
        process_definition_row=definition,
        action_template_registry_payload=action_template_registry_payload,
        temporal_domain_registry_payload=temporal_domain_registry_payload,
        qc_policy_registry_payload=qc_policy_registry_payload,
        drift_policy_registry_payload=drift_policy_registry_payload,
    )
    if str(validation.get("result", "")).strip() != "complete":
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_INVALID_DEFINITION, "validation": dict(validation)}
    token = str(run_id or "").strip() or "process_run.{}".format(canonical_sha256({"tick": int(max(0, _as_int(current_tick, 0))), "process_id": definition.get("process_id"), "input_refs": _as_list(input_refs)})[:16])
    run_record = build_process_run_record_row(run_id=token, process_id=str(definition.get("process_id", "")).strip(), version=str(definition.get("version", "")).strip(), start_tick=int(max(0, _as_int(current_tick, 0))), end_tick=None, status="running", input_refs=input_refs, output_refs=[], extensions={})
    run_state = {
        "run_id": token,
        "process_id": str(definition.get("process_id", "")).strip(),
        "version": str(definition.get("version", "")).strip(),
        "qc_policy_id": str(definition.get("qc_policy_id", "")).strip() or "qc.none",
        "base_qc_policy_id": str(definition.get("qc_policy_id", "")).strip() or "qc.none",
        "stabilization_policy_id": str(definition.get("stabilization_policy_id", "")).strip() or "stab.default",
        "process_lifecycle_policy_id": str(definition.get("process_lifecycle_policy_id", "")).strip() or "proc.lifecycle.default",
        "process_cert_type_id": str(definition.get("process_cert_type_id", "")).strip() or "cert.process.default",
        "drift_policy_id": str(definition.get("drift_policy_id", "")).strip() or "drift.default",
        "yield_model_id": str(definition.get("yield_model_id", "")).strip(),
        "defect_model_id": str(definition.get("defect_model_id", "")).strip(),
        "step_order": _tokens(validation.get("ordered_step_ids")),
        "step_status": dict((step_id, "pending") for step_id in _tokens(validation.get("ordered_step_ids"))),
        "deps": _deps(definition),
        "step_records": [],
        "task_requests": [],
        "output_refs": [],
        "energy_ledger_refs": [],
        "emission_refs": [],
        "entropy_events": [],
        "transform_results": [],
        "observation_artifacts": [],
        "report_artifacts": [],
        "process_quality_record_rows": [],
        "batch_quality_rows": [],
        "quality_model_evaluation_rows": [],
        "quality_rng_event_rows": [],
        "quality_model_cache_rows": [],
        "qc_result_record_rows": [],
        "qc_measurement_observation_rows": [],
        "qc_sampling_decision_rows": [],
        "qc_rework_request_rows": [],
        "qc_drift_escalation_rows": [],
        "qc_certification_hook_rows": [],
        "process_drift_state_rows": [],
        "drift_event_record_rows": [],
        "qc_policy_change_rows": [],
        "revalidation_run_rows": [],
        "process_capsule_invalidation_rows": [],
        "process_metrics_state_rows": [],
        "process_maturity_record_rows": [],
        "process_maturity_observation_rows": [],
        "process_certification_artifact_rows": [],
        "process_certification_revocation_rows": [],
        "current_maturity_state": "exploration",
        "maturity_state_extensions": {},
        "process_capsule_eligible": False,
        "process_capsule_forced_invalid": False,
        "qc_result_hash_chain": "",
        "sampling_decision_hash_chain": "",
        "qc_drift_escalation_hash_chain": "",
        "qc_certification_hook_hash_chain": "",
        "drift_state_hash_chain": "",
        "drift_event_hash_chain": "",
        "qc_policy_change_hash_chain": "",
        "revalidation_run_hash_chain": "",
        "metrics_state_hash_chain": "",
        "process_maturity_hash_chain": "",
        "process_cert_hash_chain": "",
        "decision_log_rows": [],
        "run_status": "running",
    }
    run_state["deterministic_fingerprint"] = canonical_sha256(dict(run_state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "validation": dict(validation), "run_record_row": run_record, "run_state": run_state}


def process_run_tick(*, current_tick: int, run_state: Mapping[str, object], process_definition_row: Mapping[str, object], budget_units: int, completed_action_step_ids: object = None, wait_ready_step_ids: object = None, transform_step_results: Mapping[str, object] | None = None, verify_step_results: Mapping[str, object] | None = None) -> dict:
    state = dict(run_state or {})
    run_id = str(state.get("run_id", "")).strip()
    if not run_id:
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_RUN_NOT_FOUND}
    tick = int(max(0, _as_int(current_tick, 0)))
    budget = int(max(0, _as_int(budget_units, 0)))
    done_actions = set(_tokens(completed_action_step_ids))
    done_wait = set(_tokens(wait_ready_step_ids))
    transform_map = dict((str(k).strip(), _as_map(v)) for k, v in _as_map(transform_step_results).items() if str(k).strip())
    verify_map = dict((str(k).strip(), _as_map(v)) for k, v in _as_map(verify_step_results).items() if str(k).strip())

    definition = build_process_definition_row(
        process_id=str(_as_map(process_definition_row).get("process_id", "")).strip(),
        version=str(_as_map(process_definition_row).get("version", "")).strip() or "1.0.0",
        description=str(_as_map(process_definition_row).get("description", "")).strip(),
        step_graph=_as_map(process_definition_row).get("step_graph"),
        input_signature=_as_map(process_definition_row).get("input_signature"),
        output_signature=_as_map(process_definition_row).get("output_signature"),
        required_tools=_as_map(process_definition_row).get("required_tools"),
        required_environment=_as_map(process_definition_row).get("required_environment"),
        tier_contract_id=str(_as_map(process_definition_row).get("tier_contract_id", "")).strip(),
        coupling_budget_id=str(_as_map(process_definition_row).get("coupling_budget_id", "")).strip() or None,
        qc_policy_id=str(_as_map(process_definition_row).get("qc_policy_id", "")).strip() or None,
        stabilization_policy_id=str(_as_map(process_definition_row).get("stabilization_policy_id", "")).strip() or None,
        process_lifecycle_policy_id=str(_as_map(process_definition_row).get("process_lifecycle_policy_id", "")).strip() or None,
        process_cert_type_id=str(_as_map(process_definition_row).get("process_cert_type_id", "")).strip() or None,
        drift_policy_id=str(_as_map(process_definition_row).get("drift_policy_id", "")).strip() or None,
        yield_model_id=str(_as_map(process_definition_row).get("yield_model_id", "")).strip() or None,
        defect_model_id=str(_as_map(process_definition_row).get("defect_model_id", "")).strip() or None,
        deterministic_fingerprint=str(_as_map(process_definition_row).get("deterministic_fingerprint", "")).strip(),
        extensions=_as_map(_as_map(process_definition_row).get("extensions")),
    )
    steps = process_step_rows_by_id(_as_map(definition.get("step_graph")).get("steps"))

    step_status = dict((str(k).strip(), str(v).strip()) for k, v in _as_map(state.get("step_status")).items())
    deps = dict((str(k).strip(), _tokens(v)) for k, v in _as_map(state.get("deps")).items())
    records = [dict(row) for row in _as_list(state.get("step_records")) if isinstance(row, Mapping)]
    consumed = 0

    for step_id in _tokens(state.get("step_order")):
        if step_status.get(step_id) in {"completed", "failed"}:
            continue
        if any(step_status.get(dep) != "completed" for dep in deps.get(step_id, [])):
            continue
        step = dict(steps.get(step_id) or {})
        if not step:
            continue
        cost = int(max(0, _as_int(step.get("cost_units", 0), 0)))
        if consumed + cost > budget:
            state.setdefault("decision_log_rows", []).append({"tick": tick, "step_id": step_id, "reason": "deferred_non_critical_budget"})
            continue
        consumed += cost
        kind = str(step.get("step_kind", "")).strip()
        records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="started", extensions={"step_kind": kind}))
        if kind == "action":
            if step_id in done_actions:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "action_signal"}))
            else:
                step_status[step_id] = "waiting_action"
                state.setdefault("task_requests", []).append({"run_id": run_id, "step_id": step_id, "tick": tick, "action_template_id": str(step.get("action_template_id", "")).strip()})
        elif kind == "wait":
            if step_id in done_wait:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "temporal_ready"}))
            else:
                step_status[step_id] = "waiting_time"
        elif kind == "verify":
            verify = dict(verify_map.get(step_id) or {})
            passed = bool(verify.get("pass", True))
            state.setdefault("report_artifacts", []).append({"artifact_type_id": "artifact.process.verify_report", "run_id": run_id, "step_id": step_id, "tick": tick, "pass": passed})
            if passed:
                step_status[step_id] = "completed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))
            else:
                step_status[step_id] = "failed"
                records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="failed"))
        elif kind == "transform":
            result = dict(transform_map.get(step_id) or {})
            if int(_as_int(result.get("direct_mass_delta", 0), 0)) != 0 or int(_as_int(result.get("direct_energy_delta", 0), 0)) != 0:
                return {
                    "result": "refused",
                    "reason_code": REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION,
                    "step_id": step_id,
                    "run_state": state,
                }
            ext = _as_map(step.get("extensions"))
            if bool(ext.get("moves_mass_energy", False) or ext.get("requires_energy_ledger", False)):
                if (not _tokens(result.get("energy_transform_refs"))) or int(max(0, _as_int(result.get("entropy_increment", 0), 0))) <= 0:
                    return {"result": "refused", "reason_code": REFUSAL_PROCESS_LEDGER_REQUIRED, "step_id": step_id, "run_state": state}
            state["energy_ledger_refs"] = _tokens(list(_as_list(state.get("energy_ledger_refs"))) + list(_tokens(result.get("energy_transform_refs"))))
            state["emission_refs"] = _tokens(list(_as_list(state.get("emission_refs"))) + list(_tokens(result.get("emission_refs"))))
            if int(max(0, _as_int(result.get("entropy_increment", 0), 0))) > 0:
                state.setdefault("entropy_events", [])
                state["entropy_events"] = [dict(row) for row in _as_list(state.get("entropy_events")) if isinstance(row, Mapping)] + [
                    {
                        "run_id": run_id,
                        "step_id": step_id,
                        "tick": tick,
                        "entropy_increment": int(max(0, _as_int(result.get("entropy_increment", 0), 0))),
                    }
                ]
            state.setdefault("transform_results", []).append({
                "run_id": run_id,
                "step_id": step_id,
                "tick": tick,
                "energy_transform_refs": _tokens(result.get("energy_transform_refs")),
                "emission_refs": _tokens(result.get("emission_refs")),
                "entropy_increment": int(max(0, _as_int(result.get("entropy_increment", 0), 0))),
            })
            state["output_refs"] = [dict(row) for row in _as_list(state.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(result.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(step.get("outputs")) if isinstance(row, Mapping)]
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))
        else:
            state.setdefault("observation_artifacts", []).append({"artifact_type_id": "artifact.process.measurement", "run_id": run_id, "step_id": step_id, "tick": tick})
            state["output_refs"] = [dict(row) for row in _as_list(state.get("output_refs")) if isinstance(row, Mapping)] + [dict(row) for row in _as_list(step.get("outputs")) if isinstance(row, Mapping)]
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed"))

    for step_id in _tokens(state.get("step_order")):
        if step_status.get(step_id) == "waiting_action" and step_id in done_actions:
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "action_signal"}))
        if step_status.get(step_id) == "waiting_time" and step_id in done_wait:
            step_status[step_id] = "completed"
            records.append(build_process_step_record_row(run_id=run_id, step_id=step_id, tick=tick, status="completed", extensions={"source": "temporal_ready"}))

    state["step_status"] = step_status
    state["step_records"] = records
    state["cost_units_consumed_total"] = int(max(0, _as_int(state.get("cost_units_consumed_total", 0), 0) + consumed))
    state["run_status"] = "failed" if any(step_status.get(step_id) == "failed" for step_id in _tokens(state.get("step_order"))) else ("completed" if all(step_status.get(step_id) == "completed" for step_id in _tokens(state.get("step_order"))) else "running")
    state["deterministic_fingerprint"] = canonical_sha256(dict(state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "run_state": state, "cost_units_consumed": consumed}


def process_run_end(
    *,
    current_tick: int,
    run_record_row: Mapping[str, object],
    run_state: Mapping[str, object],
    status: str | None = None,
    quality_inputs: Mapping[str, object] | None = None,
    tool_ids: object = None,
    environment_snapshot_hash: str | None = None,
    stochastic_quality_enabled: bool = False,
    yield_model_registry_payload: Mapping[str, object] | None = None,
    defect_model_registry_payload: Mapping[str, object] | None = None,
    constitutive_model_registry_payload: Mapping[str, object] | None = None,
    model_type_registry_payload: Mapping[str, object] | None = None,
    model_cache_policy_registry_payload: Mapping[str, object] | None = None,
    qc_policy_registry_payload: Mapping[str, object] | None = None,
    sampling_strategy_registry_payload: Mapping[str, object] | None = None,
    test_procedure_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    instrument_id: str | None = None,
    calibration_cert_id: str | None = None,
    requester_subject_id: str | None = None,
    stabilization_policy_registry_payload: Mapping[str, object] | None = None,
    process_lifecycle_policy_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    process_certification_required: bool = False,
    certification_issuer_subject_id: str | None = None,
    cert_validity_ticks: int | None = None,
    metrics_update_stride: int = 1,
    force_metrics_update: bool = False,
    drift_update_stride: int = 1,
    force_drift_update: bool = False,
    require_human_or_institution_cert: bool = False,
    reliability_failure_count: int = 0,
) -> dict:
    run_record = dict(_as_map(run_record_row))
    run_id = str(run_record.get("run_id", "")).strip()
    if not run_id:
        return {"result": "refused", "reason_code": REFUSAL_PROCESS_RUN_NOT_FOUND}
    state = dict(_as_map(run_state))
    final_status = str(status or "").strip().lower() or str(state.get("run_status", "completed")).strip().lower() or "completed"
    if final_status == "running":
        final_status = "completed"
    finalized = build_process_run_record_row(
        run_id=run_id,
        process_id=str(run_record.get("process_id", "")).strip(),
        version=str(run_record.get("version", "")).strip() or "1.0.0",
        start_tick=_as_int(run_record.get("start_tick", 0), 0),
        end_tick=int(max(0, _as_int(current_tick, 0))),
        status=final_status,
        input_refs=_as_list(run_record.get("input_refs")),
        output_refs=_as_list(state.get("output_refs")),
        deterministic_fingerprint="",
        extensions=dict(_as_map(run_record.get("extensions")), run_state_fingerprint=str(state.get("deterministic_fingerprint", "")).strip()),
    )

    output_batch_ids = _batch_ids_from_refs(state.get("output_refs"))
    input_batch_ids = _batch_ids_from_refs(run_record.get("input_refs"))
    qc_policy_id = str(state.get("qc_policy_id", "")).strip() or "qc.none"
    yield_model_id = str(state.get("yield_model_id", "")).strip()
    defect_model_id = str(state.get("defect_model_id", "")).strip()
    quality_result = {
        "result": "skipped",
        "reason": "no_output_batches",
        "yield_factor": 1000,
        "defect_flags": [],
        "quality_grade": "grade.A",
        "error_estimate_permille": 0,
        "defect_severity": 0,
        "contamination_tags": [],
        "evaluation_results": [],
        "output_actions": [],
        "cache_rows": [dict(row) for row in _as_list(state.get("quality_model_cache_rows")) if isinstance(row, Mapping)],
        "rng_rows": [],
    }
    if output_batch_ids and yield_model_id and defect_model_id:
        quality_result = _evaluate_process_quality(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            run_id=str(run_id),
            process_id=str(run_record.get("process_id", "")).strip(),
            process_version=str(run_record.get("version", "")).strip() or "1.0.0",
            yield_model_id=str(yield_model_id),
            defect_model_id=str(defect_model_id),
            output_batch_ids=list(output_batch_ids),
            input_batch_ids=list(input_batch_ids),
            quality_inputs=_as_map(quality_inputs),
            stochastic_quality_enabled=bool(stochastic_quality_enabled),
            yield_model_registry_payload=yield_model_registry_payload,
            defect_model_registry_payload=defect_model_registry_payload,
            constitutive_model_registry_payload=constitutive_model_registry_payload,
            model_type_registry_payload=model_type_registry_payload,
            model_cache_policy_registry_payload=model_cache_policy_registry_payload,
            cache_rows=state.get("quality_model_cache_rows"),
        )
    elif output_batch_ids:
        quality_result["reason"] = "missing_process_quality_model_ids"

    quality_record = {}
    if output_batch_ids:
        quality_record = build_process_quality_record_row(
            run_id=str(run_id),
            yield_factor=int(max(0, min(1000, _as_int(quality_result.get("yield_factor", 1000), 1000)))),
            defect_flags=_tokens(quality_result.get("defect_flags")),
            quality_grade=str(quality_result.get("quality_grade", "grade.C")).strip() or "grade.C",
            extensions={
                "process_id": str(run_record.get("process_id", "")).strip(),
                "process_version": str(run_record.get("version", "")).strip() or "1.0.0",
                "yield_model_id": str(yield_model_id),
                "defect_model_id": str(defect_model_id),
                "output_batch_ids": list(output_batch_ids),
                "input_batch_ids": list(input_batch_ids),
                "quality_reason": str(quality_result.get("reason", "")).strip(),
                "error_estimate_permille": int(max(0, min(1000, _as_int(quality_result.get("error_estimate_permille", 0), 0)))),
                "defect_severity": int(max(0, min(1000, _as_int(quality_result.get("defect_severity", 0), 0)))),
                "stochastic_quality_enabled": bool(stochastic_quality_enabled),
            },
        )
    traceability = {
        "run_id": str(run_id),
        "process_id": str(run_record.get("process_id", "")).strip(),
        "process_version": str(run_record.get("version", "")).strip() or "1.0.0",
        "input_batch_ids": list(input_batch_ids),
        "tool_ids": _tokens(tool_ids),
        "environment_snapshot_hash": str(environment_snapshot_hash or canonical_sha256({"run_id": run_id, "tick": int(max(0, _as_int(current_tick, 0)))})).strip(),
    }
    generated_batch_quality_rows: List[dict] = []
    if output_batch_ids:
        contamination_tags = _tokens(quality_result.get("contamination_tags"))
        if (not contamination_tags) and ("contamination" in set(_tokens(quality_result.get("defect_flags")))):
            contamination_tags = ["contamination.process"]
        for batch_id in list(output_batch_ids):
            row = build_batch_quality_row(
                batch_id=str(batch_id),
                quality_grade=str(quality_result.get("quality_grade", "grade.C")).strip() or "grade.C",
                defect_flags=_tokens(quality_result.get("defect_flags")),
                contamination_tags=list(contamination_tags),
                yield_factor=int(max(0, min(1000, _as_int(quality_result.get("yield_factor", 1000), 1000)))),
                extensions={
                    "traceability": dict(traceability),
                    "quality_model_ids": {
                        "yield_model_id": str(yield_model_id),
                        "defect_model_id": str(defect_model_id),
                    },
                    "source": "PROC2-4",
                },
            )
            if row:
                generated_batch_quality_rows.append(dict(row))

    merged_quality_rows = [dict(row) for row in _as_list(state.get("process_quality_record_rows")) if isinstance(row, Mapping)]
    if quality_record:
        merged_quality_rows.append(dict(quality_record))
    merged_quality_rows = sorted(merged_quality_rows, key=lambda row: (str(row.get("run_id", "")), str(row.get("deterministic_fingerprint", ""))))

    merged_batch_rows = [dict(row) for row in _as_list(state.get("batch_quality_rows")) if isinstance(row, Mapping)] + [dict(row) for row in list(generated_batch_quality_rows)]
    merged_batch_rows = sorted(merged_batch_rows, key=lambda row: str(row.get("batch_id", "")))

    qc_result = evaluate_qc_for_run(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        run_id=str(run_id),
        qc_policy_id=str(qc_policy_id),
        batch_quality_rows=list(merged_batch_rows),
        process_quality_record_rows=list(merged_quality_rows),
        qc_policy_registry_payload=qc_policy_registry_payload,
        sampling_strategy_registry_payload=sampling_strategy_registry_payload,
        test_procedure_registry_payload=test_procedure_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        instrument_id=instrument_id,
        calibration_cert_id=calibration_cert_id,
        requester_subject_id=requester_subject_id,
    )

    rejected_ids = set(_tokens(qc_result.get("rejected_batch_ids")))
    rework_ids = set(_tokens(qc_result.get("rework_batch_ids")))
    warning_ids = set(_tokens(qc_result.get("warning_batch_ids")))
    quarantine_ids = set(_tokens(qc_result.get("quarantine_batch_ids")))

    batch_with_qc: List[dict] = []
    for row in merged_batch_rows:
        item = dict(row)
        batch_id = str(item.get("batch_id", "")).strip()
        ext = _as_map(item.get("extensions"))
        if batch_id in quarantine_ids:
            ext["qc_status"] = "quarantine"
            ext["qc_usable"] = False
        elif batch_id in rejected_ids:
            ext["qc_status"] = "rejected"
            ext["qc_usable"] = False
        elif batch_id in rework_ids:
            ext["qc_status"] = "rework_required"
            ext["qc_usable"] = False
        elif batch_id in warning_ids:
            ext["qc_status"] = "accept_warning"
            ext["qc_usable"] = True
        if batch_id in (rejected_ids | rework_ids | warning_ids | quarantine_ids):
            ext["qc_policy_id"] = str(qc_policy_id)
            ext["qc_result_hash_chain"] = str(qc_result.get("qc_result_hash_chain", "")).strip()
        item["extensions"] = ext
        batch_with_qc.append(item)
    merged_batch_rows = sorted(batch_with_qc, key=lambda row: str(row.get("batch_id", "")))

    state["process_quality_record_rows"] = merged_quality_rows
    state["batch_quality_rows"] = merged_batch_rows
    state["quality_model_evaluation_rows"] = [
        dict(row)
        for row in _as_list(state.get("quality_model_evaluation_rows"))
        if isinstance(row, Mapping)
    ] + [
        dict(row)
        for row in _as_list(quality_result.get("evaluation_results"))
        if isinstance(row, Mapping)
    ]
    state["quality_rng_event_rows"] = [
        dict(row)
        for row in _as_list(state.get("quality_rng_event_rows"))
        if isinstance(row, Mapping)
    ] + [
        dict(row)
        for row in _as_list(quality_result.get("rng_rows"))
        if isinstance(row, Mapping)
    ]
    state["quality_model_cache_rows"] = [dict(row) for row in _as_list(quality_result.get("cache_rows")) if isinstance(row, Mapping)]
    state["qc_result_record_rows"] = sorted(
        [dict(row) for row in _as_list(state.get("qc_result_record_rows")) if isinstance(row, Mapping)]
        + [dict(row) for row in _as_list(qc_result.get("qc_result_rows")) if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("run_id", "")), str(row.get("batch_id", ""))),
    )
    state["qc_measurement_observation_rows"] = sorted(
        [dict(row) for row in _as_list(state.get("qc_measurement_observation_rows")) if isinstance(row, Mapping)]
        + [dict(row) for row in _as_list(qc_result.get("measurement_rows")) if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("batch_id", "")), str(row.get("test_id", ""))),
    )
    state["qc_sampling_decision_rows"] = sorted(
        [dict(row) for row in _as_list(state.get("qc_sampling_decision_rows")) if isinstance(row, Mapping)]
        + [dict(row) for row in _as_list(qc_result.get("decision_rows")) if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("run_id", "")), str(row.get("batch_id", ""))),
    )
    state["qc_rework_request_rows"] = sorted(
        [dict(row) for row in _as_list(state.get("qc_rework_request_rows")) if isinstance(row, Mapping)]
        + [
            {
                "request_id": "request.process.rework.{}".format(
                    canonical_sha256(
                        {
                            "run_id": str(run_id),
                            "batch_id": str(batch_id),
                            "tick": int(max(0, _as_int(current_tick, 0))),
                        }
                    )[:16]
                ),
                "run_id": str(run_id),
                "batch_id": str(batch_id),
                "tick": int(max(0, _as_int(current_tick, 0))),
                "status": "requested",
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "run_id": str(run_id),
                        "batch_id": str(batch_id),
                        "tick": int(max(0, _as_int(current_tick, 0))),
                        "status": "requested",
                    }
                ),
                "extensions": {
                    "source": "PROC3-3",
                    "qc_policy_id": str(qc_policy_id),
                },
            }
            for batch_id in sorted(rework_ids)
        ],
        key=lambda row: (str(row.get("run_id", "")), str(row.get("batch_id", ""))),
    )

    qc_policy_rows = _qc_policy_rows_by_id(qc_policy_registry_payload)
    qc_policy_row = dict(qc_policy_rows.get(str(qc_policy_id)) or {})
    qc_policy_ext = _as_map(qc_policy_row.get("extensions"))
    drift_fail_rate_threshold = int(max(0, min(1000, _as_int(qc_policy_ext.get("drift_escalation_fail_rate_permille", 1001), 1001))))
    fail_rate = int(max(0, min(1000, _as_int(qc_result.get("fail_rate_permille", 0), 0))))
    sampled_count = int(max(0, _as_int(qc_result.get("sampled_count", 0), 0)))
    failed_count = int(max(0, _as_int(qc_result.get("failed_count", 0), 0)))
    cert_invalidation_on_fail = bool(qc_policy_ext.get("cert_invalidation_on_fail", False))

    if sampled_count > 0 and fail_rate >= drift_fail_rate_threshold and drift_fail_rate_threshold <= 1000:
        drift_row = {
            "event_id": "event.process.drift_escalation.{}".format(
                canonical_sha256(
                    {
                        "run_id": str(run_id),
                        "tick": int(max(0, _as_int(current_tick, 0))),
                        "fail_rate_permille": int(fail_rate),
                        "threshold_permille": int(drift_fail_rate_threshold),
                    }
                )[:16]
            ),
            "run_id": str(run_id),
            "process_id": str(run_record.get("process_id", "")).strip(),
            "tick": int(max(0, _as_int(current_tick, 0))),
            "event_kind_id": "process.drift_detected",
            "fail_rate_permille": int(fail_rate),
            "threshold_permille": int(drift_fail_rate_threshold),
            "deterministic_fingerprint": "",
            "extensions": {
                "qc_policy_id": str(qc_policy_id),
                "sampled_count": int(sampled_count),
                "failed_count": int(failed_count),
                "source": "PROC3-4",
                "explain_contract_id": "explain.qc_failure",
            },
        }
        drift_row["deterministic_fingerprint"] = canonical_sha256(dict(drift_row, deterministic_fingerprint=""))
        state["qc_drift_escalation_rows"] = sorted(
            [dict(row) for row in _as_list(state.get("qc_drift_escalation_rows")) if isinstance(row, Mapping)] + [dict(drift_row)],
            key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("event_id", ""))),
        )
        state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "qc_drift_escalated",
                "event_id": str(drift_row.get("event_id", "")).strip(),
                "fail_rate_permille": int(fail_rate),
                "threshold_permille": int(drift_fail_rate_threshold),
            }
        ]
    else:
        state["qc_drift_escalation_rows"] = [dict(row) for row in _as_list(state.get("qc_drift_escalation_rows")) if isinstance(row, Mapping)]

    if cert_invalidation_on_fail and failed_count > 0:
        cert_row = {
            "hook_id": "hook.process.certification.invalidate.{}".format(
                canonical_sha256(
                    {
                        "run_id": str(run_id),
                        "tick": int(max(0, _as_int(current_tick, 0))),
                        "failed_count": int(failed_count),
                    }
                )[:16]
            ),
            "run_id": str(run_id),
            "process_id": str(run_record.get("process_id", "")).strip(),
            "tick": int(max(0, _as_int(current_tick, 0))),
            "reason_code": "process.qc_failure_threshold",
            "cert_action": "invalidate_pending",
            "deterministic_fingerprint": "",
            "extensions": {
                "qc_policy_id": str(qc_policy_id),
                "failed_count": int(failed_count),
                "source": "PROC3-4",
                "explain_contract_id": "explain.qc_failure",
            },
        }
        cert_row["deterministic_fingerprint"] = canonical_sha256(dict(cert_row, deterministic_fingerprint=""))
        state["qc_certification_hook_rows"] = sorted(
            [dict(row) for row in _as_list(state.get("qc_certification_hook_rows")) if isinstance(row, Mapping)] + [dict(cert_row)],
            key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("hook_id", ""))),
        )
    else:
        state["qc_certification_hook_rows"] = [dict(row) for row in _as_list(state.get("qc_certification_hook_rows")) if isinstance(row, Mapping)]

    state["observation_artifacts"] = [dict(row) for row in _as_list(state.get("observation_artifacts")) if isinstance(row, Mapping)] + [
        dict(row)
        for row in _as_list(qc_result.get("measurement_rows"))
        if isinstance(row, Mapping)
    ]
    state["report_artifacts"] = [dict(row) for row in _as_list(state.get("report_artifacts")) if isinstance(row, Mapping)] + [
        {
            "artifact_type_id": "artifact.record.process_qc_result",
            "run_id": str(row.get("run_id", "")).strip(),
            "batch_id": str(row.get("batch_id", "")).strip(),
            "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            "sampled": bool(row.get("sampled", False)),
            "passed": bool(row.get("passed", False)),
            "action_taken": str(row.get("action_taken", "")).strip(),
            "visibility_policy": "policy.epistemic.inspector",
        }
        for row in _as_list(qc_result.get("qc_result_rows"))
        if isinstance(row, Mapping)
    ]

    state["qc_result_hash_chain"] = str(qc_result.get("qc_result_hash_chain", "")).strip()
    state["sampling_decision_hash_chain"] = str(qc_result.get("sampling_decision_hash_chain", "")).strip()
    state["qc_drift_escalation_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "run_id": str(row.get("run_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "fail_rate_permille": int(max(0, min(1000, _as_int(row.get("fail_rate_permille", 0), 0)))),
                "threshold_permille": int(max(0, min(1000, _as_int(row.get("threshold_permille", 0), 0)))),
            }
            for row in [dict(item) for item in _as_list(state.get("qc_drift_escalation_rows")) if isinstance(item, Mapping)]
        ]
    )
    state["qc_certification_hook_hash_chain"] = canonical_sha256(
        [
            {
                "hook_id": str(row.get("hook_id", "")).strip(),
                "run_id": str(row.get("run_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "reason_code": str(row.get("reason_code", "")).strip(),
                "cert_action": str(row.get("cert_action", "")).strip(),
            }
            for row in [dict(item) for item in _as_list(state.get("qc_certification_hook_rows")) if isinstance(item, Mapping)]
        ]
    )
    state.setdefault("decision_log_rows", [])
    if output_batch_ids:
        state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "quality_modeled",
                "yield_model_id": str(yield_model_id),
                "defect_model_id": str(defect_model_id),
                "output_batch_ids": list(output_batch_ids),
                "quality_result": str(quality_result.get("result", "")),
            }
        ]
    state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
        {
            "tick": int(max(0, _as_int(current_tick, 0))),
            "run_id": str(run_id),
            "reason": "qc_evaluated",
            "qc_policy_id": str(qc_policy_id),
            "sampled_count": int(sampled_count),
            "failed_count": int(failed_count),
            "fail_rate_permille": int(fail_rate),
            "qc_result_hash_chain": str(state.get("qc_result_hash_chain", "")).strip(),
            "sampling_decision_hash_chain": str(state.get("sampling_decision_hash_chain", "")).strip(),
        }
    ]
    if rework_ids:
        state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "qc_rework_requested",
                "batch_ids": sorted(rework_ids),
            }
        ]
    if rejected_ids or quarantine_ids:
        state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "qc_batches_rejected",
                "batch_ids": sorted(rejected_ids | quarantine_ids),
            }
        ]
    if cert_invalidation_on_fail and failed_count > 0:
        state["decision_log_rows"] = [dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "qc_certification_invalidation_hook",
                "failed_count": int(failed_count),
                "qc_policy_id": str(qc_policy_id),
            }
        ]

    process_id = str(run_record.get("process_id", "")).strip()
    process_version = str(run_record.get("version", "")).strip() or "1.0.0"
    stabilization_policy_id = str(state.get("stabilization_policy_id", "")).strip() or "stab.default"
    process_lifecycle_policy_id = (
        str(state.get("process_lifecycle_policy_id", "")).strip()
        or "proc.lifecycle.default"
    )
    process_cert_type_id = (
        str(state.get("process_cert_type_id", "")).strip() or "cert.process.default"
    )
    metrics_key = "{}@{}".format(process_id, process_version)
    metrics_by_key = process_metrics_rows_by_key(state.get("process_metrics_state_rows"))
    previous_metrics_row = dict(metrics_by_key.get(metrics_key) or {})
    qc_rows_for_run = [
        dict(row)
        for row in _as_list(state.get("qc_result_record_rows"))
        if isinstance(row, Mapping) and str(row.get("run_id", "")).strip() == str(run_id)
    ]
    metrics_update = update_process_metrics_for_run(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        process_id=str(process_id),
        version=str(process_version),
        previous_metrics_row=previous_metrics_row,
        process_quality_row=(dict(quality_record) if quality_record else {}),
        qc_result_rows=qc_rows_for_run,
        environment_snapshot_hash=str(traceability.get("environment_snapshot_hash", "")).strip(),
        calibration_cert_id=str(calibration_cert_id or "").strip(),
        update_stride=int(max(1, _as_int(metrics_update_stride, 1))),
        force_update=bool(force_metrics_update),
        policy_id=str(stabilization_policy_id),
    )
    metrics_row = dict(metrics_update.get("metrics_row") or previous_metrics_row)
    if metrics_row:
        metrics_by_key[metrics_key] = dict(metrics_row)
    state["process_metrics_state_rows"] = [
        dict(metrics_by_key[key]) for key in sorted(metrics_by_key.keys())
    ]
    decision_row = _as_map(metrics_update.get("decision_log_row"))
    if decision_row:
        state["decision_log_rows"] = [
            dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
        ] + [dict(decision_row)]

    drift_policy_id = str(state.get("drift_policy_id", "")).strip() or "drift.default"
    drift_policy_rows = drift_policy_rows_by_id(drift_policy_registry_payload)
    drift_policy_row = dict(
        drift_policy_rows.get(str(drift_policy_id))
        or drift_policy_rows.get("drift.default")
        or {
            "drift_policy_id": "drift.default",
            "weights": {
                "qc_fail_rate_delta": 260,
                "yield_variance_delta": 210,
                "environment_deviation_score": 150,
                "tool_degradation_score": 150,
                "calibration_deviation_score": 90,
                "entropy_growth_rate": 140,
            },
            "thresholds": {"normal": 220, "warning": 450, "critical": 700},
            "qc_escalation_rules": {
                "warning_qc_policy_id": "qc.strict_sampling",
                "critical_qc_policy_id": "qc.strict_sampling",
            },
            "revalidation_trial_count": 3,
            "extensions": {"source": "PROC6-3.default"},
        }
    )
    drift_state_by_key = process_drift_rows_by_key(state.get("process_drift_state_rows"))
    previous_drift_state_row = dict(drift_state_by_key.get(metrics_key) or {})
    quality_input_map = _as_map(quality_inputs)
    env_deviation_score = int(
        max(0, min(1000, _as_int(_as_map(metrics_row).get("env_deviation_score", 0), 0)))
    )
    tool_degradation_score = int(
        max(0, min(1000, _as_int(quality_input_map.get("tool_wear_permille", 0), 0)))
    )
    calibration_state_permille = int(
        max(0, min(1000, _as_int(quality_input_map.get("calibration_state_permille", 1000), 1000)))
    )
    calibration_deviation_score = int(max(0, min(1000, 1000 - calibration_state_permille)))
    entropy_growth_rate = int(
        max(0, min(1000, _as_int(quality_input_map.get("entropy_index", 0), 0)))
    )
    drift_eval = evaluate_process_drift(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        process_id=str(process_id),
        version=str(process_version),
        previous_metrics_row=previous_metrics_row,
        metrics_row=metrics_row,
        environment_deviation_score=int(env_deviation_score),
        tool_degradation_score=int(tool_degradation_score),
        calibration_deviation_score=int(calibration_deviation_score),
        entropy_growth_rate=int(entropy_growth_rate),
        drift_policy_row=drift_policy_row,
        previous_drift_state_row=previous_drift_state_row,
        update_stride=int(max(1, _as_int(drift_update_stride, 1))),
        force_update=bool(force_drift_update),
        reliability_failure_count=int(max(0, _as_int(reliability_failure_count, 0))),
    )
    drift_state_row = _as_map(drift_eval.get("drift_state_row"))
    drift_event_row = _as_map(drift_eval.get("drift_event_row"))
    drift_band = str(
        drift_state_row.get(
            "drift_band",
            _as_map(previous_drift_state_row).get("drift_band", "drift.normal"),
        )
    ).strip() or "drift.normal"
    drift_score = int(max(0, min(1000, _as_int(drift_state_row.get("drift_score", 0), 0))))
    state["current_drift_band"] = str(drift_band)
    state["current_drift_score"] = int(drift_score)
    if drift_state_row:
        drift_state_by_key[metrics_key] = dict(drift_state_row)
        state["process_drift_state_rows"] = [
            dict(drift_state_by_key[key]) for key in sorted(drift_state_by_key.keys())
        ]
    else:
        state["process_drift_state_rows"] = [
            dict(row)
            for row in _as_list(state.get("process_drift_state_rows"))
            if isinstance(row, Mapping)
        ]
    if drift_event_row:
        merged_drift_events = normalize_drift_event_record_rows(
            [
                dict(row)
                for row in _as_list(state.get("drift_event_record_rows"))
                if isinstance(row, Mapping)
            ]
            + [dict(drift_event_row)]
        )
        # Critical events must explicitly log capsule invalidation and certificate revocation actions.
        if str(drift_band) == "drift.critical":
            extra_events: List[dict] = []
            for action_taken in ("capsule_invalidate", "cert_revoke"):
                event_row = build_drift_event_record_row(
                    event_id="",
                    process_id=str(process_id),
                    version=str(process_version),
                    drift_band=str(drift_band),
                    drift_score=int(drift_score),
                    tick=int(max(0, _as_int(current_tick, 0))),
                    action_taken=action_taken,
                    extensions={
                        "source": "PROC6-4",
                        "drift_policy_id": str(drift_policy_id),
                    },
                )
                if event_row:
                    extra_events.append(dict(event_row))
            merged_drift_events = normalize_drift_event_record_rows(
                list(merged_drift_events) + extra_events
            )
        state["drift_event_record_rows"] = merged_drift_events
        explain_contract_id = (
            "explain.drift_critical"
            if str(drift_band) == "drift.critical"
            else "explain.drift_warning"
        )
        state["report_artifacts"] = [
            dict(row) for row in _as_list(state.get("report_artifacts")) if isinstance(row, Mapping)
        ] + [
            {
                "artifact_type_id": "artifact.explain.process_drift",
                "run_id": str(run_id),
                "process_id": str(process_id),
                "version": str(process_version),
                "tick": int(max(0, _as_int(current_tick, 0))),
                "drift_band": str(drift_band),
                "drift_score": int(drift_score),
                "event_id": str(drift_event_row.get("event_id", "")).strip(),
                "explain_contract_id": explain_contract_id,
                "visibility_policy": "policy.epistemic.inspector",
            }
        ]
    drift_decision_row = _as_map(drift_eval.get("decision_log_row"))
    if drift_decision_row:
        state["decision_log_rows"] = [
            dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
        ] + [dict(drift_decision_row)]

    if bool(drift_eval.get("qc_escalation_required", False)):
        next_qc_policy_id = str(drift_eval.get("escalated_qc_policy_id", "")).strip()
        current_qc_policy = str(state.get("qc_policy_id", "")).strip() or "qc.none"
        if next_qc_policy_id and next_qc_policy_id != current_qc_policy:
            change_row = {
                "event_id": "event.process.qc_policy_change.{}".format(
                    canonical_sha256(
                        {
                            "process_id": str(process_id),
                            "version": str(process_version),
                            "tick": int(max(0, _as_int(current_tick, 0))),
                            "from_qc_policy_id": str(current_qc_policy),
                            "to_qc_policy_id": str(next_qc_policy_id),
                            "drift_band": str(drift_band),
                        }
                    )[:16]
                ),
                "process_id": str(process_id),
                "version": str(process_version),
                "tick": int(max(0, _as_int(current_tick, 0))),
                "from_qc_policy_id": str(current_qc_policy),
                "to_qc_policy_id": str(next_qc_policy_id),
                "reason_code": "drift.qc_escalation",
                "deterministic_fingerprint": "",
                "extensions": {
                    "source": "PROC6-4",
                    "drift_policy_id": str(drift_policy_id),
                    "drift_band": str(drift_band),
                    "explain_contract_id": "explain.drift_warning",
                },
            }
            change_row["deterministic_fingerprint"] = canonical_sha256(
                dict(change_row, deterministic_fingerprint="")
            )
            state["qc_policy_change_rows"] = sorted(
                [
                    dict(row)
                    for row in _as_list(state.get("qc_policy_change_rows"))
                    if isinstance(row, Mapping)
                ]
                + [dict(change_row)],
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("event_id", "")),
                ),
            )
            state["qc_policy_id"] = str(next_qc_policy_id)
            state["decision_log_rows"] = [
                dict(row)
                for row in _as_list(state.get("decision_log_rows"))
                if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "qc_policy_escalated_by_drift",
                    "from_qc_policy_id": str(current_qc_policy),
                    "to_qc_policy_id": str(next_qc_policy_id),
                    "drift_band": str(drift_band),
                }
            ]

    if bool(drift_eval.get("capsule_invalidation_required", False)):
        invalidation_row = {
            "event_id": "event.process.capsule_invalidated.{}".format(
                canonical_sha256(
                    {
                        "process_id": str(process_id),
                        "version": str(process_version),
                        "tick": int(max(0, _as_int(current_tick, 0))),
                        "reason_code": "capsule.drift_exceeded",
                    }
                )[:16]
            ),
            "process_id": str(process_id),
            "version": str(process_version),
            "tick": int(max(0, _as_int(current_tick, 0))),
            "reason_code": "capsule.drift_exceeded",
            "deterministic_fingerprint": "",
            "extensions": {
                "source": "PROC6-4",
                "drift_band": str(drift_band),
                "drift_score": int(drift_score),
                "explain_contract_id": "explain.capsule_invalidated_by_drift",
            },
        }
        invalidation_row["deterministic_fingerprint"] = canonical_sha256(
            dict(invalidation_row, deterministic_fingerprint="")
        )
        state["process_capsule_invalidation_rows"] = sorted(
            [
                dict(row)
                for row in _as_list(state.get("process_capsule_invalidation_rows"))
                if isinstance(row, Mapping)
            ]
            + [dict(invalidation_row)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("event_id", "")),
            ),
        )
        state["process_capsule_forced_invalid"] = True
        state["report_artifacts"] = [
            dict(row) for row in _as_list(state.get("report_artifacts")) if isinstance(row, Mapping)
        ] + [
            {
                "artifact_type_id": "artifact.explain.process_capsule_invalidated",
                "run_id": str(run_id),
                "process_id": str(process_id),
                "version": str(process_version),
                "tick": int(max(0, _as_int(current_tick, 0))),
                "reason_code": "capsule.drift_exceeded",
                "explain_contract_id": "explain.capsule_invalidated_by_drift",
                "visibility_policy": "policy.epistemic.inspector",
            }
        ]

    if bool(drift_eval.get("revalidation_required", False)):
        schedule_result = schedule_revalidation_trials(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            process_id=str(process_id),
            version=str(process_version),
            trial_count=int(max(1, _as_int(drift_eval.get("revalidation_trial_count", 3), 3))),
            existing_rows=state.get("revalidation_run_rows"),
        )
        state["revalidation_run_rows"] = [
            dict(row)
            for row in _as_list(schedule_result.get("revalidation_rows"))
            if isinstance(row, Mapping)
        ]
        if _as_list(schedule_result.get("scheduled_rows")):
            state["decision_log_rows"] = [
                dict(row)
                for row in _as_list(state.get("decision_log_rows"))
                if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "revalidation_scheduled",
                    "trial_count": int(
                        len(
                            [
                                row
                                for row in _as_list(schedule_result.get("scheduled_rows"))
                                if isinstance(row, Mapping)
                            ]
                        )
                    ),
                }
            ]
            state["report_artifacts"] = [
                dict(row)
                for row in _as_list(state.get("report_artifacts"))
                if isinstance(row, Mapping)
            ] + [
                {
                    "artifact_type_id": "artifact.explain.process_revalidation_required",
                    "run_id": str(run_id),
                    "process_id": str(process_id),
                    "version": str(process_version),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "explain_contract_id": "explain.revalidation_required",
                    "visibility_policy": "policy.epistemic.inspector",
                }
            ]

    revalidation_apply = apply_revalidation_trial_result(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        process_id=str(process_id),
        version=str(process_version),
        run_passed=bool(final_status == "completed" and failed_count <= 0),
        revalidation_rows=state.get("revalidation_run_rows"),
    )
    state["revalidation_run_rows"] = [
        dict(row)
        for row in _as_list(revalidation_apply.get("revalidation_rows"))
        if isinstance(row, Mapping)
    ]
    if bool(revalidation_apply.get("consumed", False)):
        pending_count = int(max(0, _as_int(revalidation_apply.get("pending_count", 0), 0)))
        fail_count_trials = int(max(0, _as_int(revalidation_apply.get("fail_count", 0), 0)))
        pass_count_trials = int(max(0, _as_int(revalidation_apply.get("pass_count", 0), 0)))
        state["decision_log_rows"] = [
            dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
        ] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "revalidation_trial_consumed",
                "pending_count": int(pending_count),
                "pass_count": int(pass_count_trials),
                "fail_count": int(fail_count_trials),
            }
        ]
        if pending_count == 0 and pass_count_trials > 0 and fail_count_trials == 0:
            reset_row = build_process_drift_state_row(
                process_id=str(process_id),
                version=str(process_version),
                drift_score=0,
                drift_band="drift.normal",
                last_update_tick=int(max(0, _as_int(current_tick, 0))),
                extensions={
                    "source": "PROC6-5",
                    "revalidation_reset": True,
                },
            )
            if reset_row:
                drift_state_by_key[metrics_key] = dict(reset_row)
                state["process_drift_state_rows"] = [
                    dict(drift_state_by_key[key]) for key in sorted(drift_state_by_key.keys())
                ]
            state["process_capsule_forced_invalid"] = False
            state["qc_policy_id"] = str(state.get("base_qc_policy_id", "qc.none")).strip() or "qc.none"
            state["decision_log_rows"] = [
                dict(row)
                for row in _as_list(state.get("decision_log_rows"))
                if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "revalidation_succeeded_reset_drift",
                }
            ]
        elif pending_count == 0 and fail_count_trials > 0:
            state["process_capsule_forced_invalid"] = True
            state["decision_log_rows"] = [
                dict(row)
                for row in _as_list(state.get("decision_log_rows"))
                if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "revalidation_failed_remain_invalid",
                }
            ]

    stabilization_policy_rows = stabilization_policy_rows_by_id(
        stabilization_policy_registry_payload
    )
    stabilization_policy_row = dict(
        stabilization_policy_rows.get(str(stabilization_policy_id))
        or stabilization_policy_rows.get("stab.default")
        or {
            "policy_id": "stab.default",
            "weights": {
                "runs": 200,
                "consistency": 250,
                "qc_pass": 250,
                "defect": 150,
                "environment": 100,
                "calibration": 50,
            },
            "thresholds": {
                "defined": 120,
                "stabilized": 650,
                "certified": 780,
                "capsule_eligible": 860,
                "cert_qc_min": 850,
                "cert_defect_max": 180,
            },
            "min_runs": 8,
            "stability_horizon_ticks": 64,
            "extensions": {"source": "PROC4-4.default"},
        }
    )
    lifecycle_policy_rows = process_lifecycle_policy_rows_by_id(
        process_lifecycle_policy_registry_payload
    )
    lifecycle_policy_row = dict(
        lifecycle_policy_rows.get(str(process_lifecycle_policy_id))
        or lifecycle_policy_rows.get("proc.lifecycle.default")
        or {
            "process_lifecycle_policy_id": "proc.lifecycle.default",
            "allowed_states": [
                "exploration",
                "defined",
                "stabilized",
                "certified",
                "capsule_eligible",
            ],
            "allow_capsule_without_certification": True,
            "extensions": {"source": "PROC4-4.default"},
        }
    )
    certification_gate_passed = bool(
        str(quality_result.get("result", "")).strip() in {"complete", "skipped"}
    ) and int(failed_count) <= 0
    maturity_eval = evaluate_process_maturity(
        current_tick=int(max(0, _as_int(current_tick, 0))),
        process_id=str(process_id),
        version=str(process_version),
        metrics_row=dict(metrics_row),
        previous_maturity_state=str(state.get("current_maturity_state", "exploration")),
        previous_state_extensions=_as_map(state.get("maturity_state_extensions")),
        stabilization_policy_row=stabilization_policy_row,
        lifecycle_policy_row=lifecycle_policy_row,
        certification_gate_passed=bool(certification_gate_passed),
        certification_required=bool(process_certification_required),
    )
    state["current_maturity_state"] = str(
        maturity_eval.get("next_maturity_state", "exploration")
    ).strip() or "exploration"
    state["maturity_state_extensions"] = dict(
        _as_map(maturity_eval.get("state_extensions"))
    )
    maturity_record_row = _as_map(maturity_eval.get("record_row"))
    if maturity_record_row:
        state["process_maturity_record_rows"] = sorted(
            [
                dict(row)
                for row in _as_list(state.get("process_maturity_record_rows"))
                if isinstance(row, Mapping)
            ]
            + [dict(maturity_record_row)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("record_id", "")),
            ),
        )
        state["decision_log_rows"] = [
            dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
        ] + [
            {
                "tick": int(max(0, _as_int(current_tick, 0))),
                "run_id": str(run_id),
                "reason": "process_maturity_transition",
                "previous_state": str(maturity_eval.get("previous_maturity_state", "")).strip(),
                "next_state": str(maturity_eval.get("next_maturity_state", "")).strip(),
                "stabilization_score": int(
                    max(0, min(1000, _as_int(maturity_eval.get("stabilization_score", 0), 0)))
                ),
            }
        ]
    maturity_observation_row = _as_map(maturity_eval.get("observation_row"))
    if maturity_observation_row:
        state["process_maturity_observation_rows"] = sorted(
            [
                dict(row)
                for row in _as_list(state.get("process_maturity_observation_rows"))
                if isinstance(row, Mapping)
            ]
            + [dict(maturity_observation_row)],
            key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("process_id", "")),
                str(row.get("version", "")),
            ),
        )
    maturity_explain_row = _as_map(maturity_eval.get("explain_row"))
    if maturity_explain_row:
        deny_reason = str(
            _as_map(maturity_eval.get("state_extensions")).get("deny_reason", "")
        ).strip()
        explain_contract_id = "explain.process_not_stable"
        if maturity_record_row:
            explain_contract_id = "explain.process_maturity_change"
        elif deny_reason in {
            "certification_gate_failed",
            "qc_pass_rate_below_minimum",
            "defect_rate_above_maximum",
            "score_below_certified_threshold",
            "state_disallowed_by_lifecycle_policy",
        }:
            explain_contract_id = "explain.certification_denied"
        state["report_artifacts"] = [
            dict(row) for row in _as_list(state.get("report_artifacts")) if isinstance(row, Mapping)
        ] + [
            dict(
                maturity_explain_row,
                explain_contract_id=explain_contract_id,
                visibility_policy="policy.epistemic.inspector",
            )
        ]
        if explain_contract_id == "explain.certification_denied":
            state["decision_log_rows"] = [
                dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "process_certification_denied",
                    "reason_code": deny_reason,
                }
            ]

    state["process_quality_hash_chain"] = canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "yield_factor": int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0)))),
                "defect_flags": _tokens(row.get("defect_flags")),
                "quality_grade": str(row.get("quality_grade", "")).strip(),
            }
            for row in state["process_quality_record_rows"]
        ]
    )
    state["batch_quality_hash_chain"] = canonical_sha256(
        [
            {
                "batch_id": str(row.get("batch_id", "")).strip(),
                "quality_grade": str(row.get("quality_grade", "")).strip(),
                "defect_flags": _tokens(row.get("defect_flags")),
                "contamination_tags": _tokens(row.get("contamination_tags")),
                "yield_factor": int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0)))),
                "traceability_run_id": str(_as_map(_as_map(row.get("extensions")).get("traceability")).get("run_id", "")).strip(),
            }
            for row in state["batch_quality_rows"]
        ]
    )
    cert_rows = sorted(
        [
            dict(row)
            for row in _as_list(state.get("process_certification_artifact_rows"))
            if isinstance(row, Mapping)
        ],
        key=lambda row: (
            int(max(0, _as_int(row.get("issued_tick", 0), 0))),
            str(row.get("cert_id", "")),
        ),
    )
    cert_revocation_rows = sorted(
        [
            dict(row)
            for row in _as_list(state.get("process_certification_revocation_rows"))
            if isinstance(row, Mapping)
        ],
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    revoked_cert_ids = set(
        str(row.get("cert_id", "")).strip() for row in cert_revocation_rows if str(row.get("cert_id", "")).strip()
    )
    active_cert_rows = [
        dict(row)
        for row in cert_rows
        if str(row.get("cert_id", "")).strip() and str(row.get("cert_id", "")).strip() not in revoked_cert_ids
    ]
    next_maturity_state = str(state.get("current_maturity_state", "exploration")).strip()
    should_issue_cert = (
        next_maturity_state in {"certified", "capsule_eligible"} and not active_cert_rows
    )
    if should_issue_cert:
        issued_tick = int(max(0, _as_int(current_tick, 0)))
        valid_until_tick = (
            None
            if cert_validity_ticks is None
            else int(max(issued_tick, issued_tick + max(0, _as_int(cert_validity_ticks, 0))))
        )
        cert_row = build_process_certificate_artifact_row(
            cert_id="",
            process_id=str(process_id),
            version=str(process_version),
            cert_type_id=str(process_cert_type_id),
            issuer_subject_id=(
                str(certification_issuer_subject_id).strip()
                if str(certification_issuer_subject_id or "").strip()
                else "subject.system.process_certifier"
            ),
            issued_tick=issued_tick,
            valid_until_tick=valid_until_tick,
            extensions={
                "source": "PROC4-5",
                "run_id": str(run_id),
                "maturity_state": str(next_maturity_state),
            },
        )
        if cert_row:
            cert_rows.append(dict(cert_row))
            state["decision_log_rows"] = [
                dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(issued_tick),
                    "run_id": str(run_id),
                    "reason": "process_certification_issued",
                    "cert_id": str(cert_row.get("cert_id", "")).strip(),
                    "cert_type_id": str(process_cert_type_id),
                    "maturity_state": str(next_maturity_state),
                }
            ]

    qc_failure_spike = bool(sampled_count > 0 and fail_rate >= drift_fail_rate_threshold)
    drift_cert_revocation_required = bool(
        drift_band == "drift.critical"
        or bool(drift_eval.get("certification_revocation_required", False))
    )
    should_revoke = bool(
        active_cert_rows
        and (
            (cert_invalidation_on_fail and failed_count > 0)
            or qc_failure_spike
            or drift_cert_revocation_required
            or next_maturity_state not in {"certified", "capsule_eligible"}
        )
    )
    if should_revoke:
        if drift_cert_revocation_required:
            revoke_reason = "process.drift_critical"
        elif (cert_invalidation_on_fail and failed_count > 0) or qc_failure_spike:
            revoke_reason = "process.qc_failure_spike"
        else:
            revoke_reason = "process.maturity_dropped"
        for cert_row in list(active_cert_rows):
            cert_id = str(cert_row.get("cert_id", "")).strip()
            if (not cert_id) or cert_id in set(
                str(row.get("cert_id", "")).strip() for row in cert_revocation_rows
            ):
                continue
            rev_row = build_process_certificate_revocation_row(
                event_id="",
                cert_id=cert_id,
                process_id=str(process_id),
                version=str(process_version),
                cert_type_id=str(process_cert_type_id),
                reason_code=str(revoke_reason),
                tick=int(max(0, _as_int(current_tick, 0))),
                extensions={
                    "source": "PROC4-5",
                    "run_id": str(run_id),
                    "maturity_state": str(next_maturity_state),
                },
            )
            if rev_row:
                cert_revocation_rows.append(dict(rev_row))
        if cert_revocation_rows:
            state["decision_log_rows"] = [
                dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
            ] + [
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "run_id": str(run_id),
                    "reason": "process_certification_revoked",
                    "reason_code": str(revoke_reason),
                }
            ]

    state["process_certification_artifact_rows"] = sorted(
        list(cert_rows),
        key=lambda row: (
            int(max(0, _as_int(row.get("issued_tick", 0), 0))),
            str(row.get("cert_id", "")),
        ),
    )
    state["process_certification_revocation_rows"] = sorted(
        list(cert_revocation_rows),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    revoked_cert_ids_after = set(
        str(row.get("cert_id", "")).strip()
        for row in state["process_certification_revocation_rows"]
        if str(row.get("cert_id", "")).strip()
    )
    active_cert_ids_after = sorted(
        set(
            str(row.get("cert_id", "")).strip()
            for row in state["process_certification_artifact_rows"]
            if str(row.get("cert_id", "")).strip()
        )
        - revoked_cert_ids_after
    )
    capsule_gate = process_capsule_eligibility_status(
        maturity_state=str(state.get("current_maturity_state", "exploration")),
        lifecycle_policy_row=lifecycle_policy_row,
        has_process_certificate=bool(active_cert_ids_after),
        require_human_or_institution_cert=bool(require_human_or_institution_cert),
    )
    drift_forced_invalid = bool(state.get("process_capsule_forced_invalid", False))
    state["process_capsule_eligible"] = bool(capsule_gate.get("eligible", False)) and (not drift_forced_invalid)
    capsule_gate_reason_code = (
        "process.capsule_invalidated_by_drift"
        if drift_forced_invalid
        else str(capsule_gate.get("reason_code", "")).strip()
    )
    state["decision_log_rows"] = [
        dict(row) for row in _as_list(state.get("decision_log_rows")) if isinstance(row, Mapping)
    ] + [
        {
            "tick": int(max(0, _as_int(current_tick, 0))),
            "run_id": str(run_id),
            "reason": (
                "process_capsule_eligibility_granted"
                if bool(state.get("process_capsule_eligible", False))
                else "process_capsule_eligibility_refused"
            ),
            "maturity_state": str(state.get("current_maturity_state", "exploration")),
            "has_active_process_certificate": bool(active_cert_ids_after),
            "reason_code": str(capsule_gate_reason_code),
        }
    ]
    state["metrics_state_hash_chain"] = canonical_sha256(
        [
            {
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "runs_count": int(max(0, _as_int(row.get("runs_count", 0), 0))),
                "yield_mean": int(max(0, min(1000, _as_int(row.get("yield_mean", 0), 0)))),
                "yield_variance": int(max(0, _as_int(row.get("yield_variance", 0), 0))),
                "defect_rate": int(max(0, min(1000, _as_int(row.get("defect_rate", 0), 0)))),
                "qc_pass_rate": int(max(0, min(1000, _as_int(row.get("qc_pass_rate", 0), 0)))),
                "env_deviation_score": int(
                    max(0, min(1000, _as_int(row.get("env_deviation_score", 0), 0)))
                ),
                "calibration_deviation_score": int(
                    max(0, min(1000, _as_int(row.get("calibration_deviation_score", 0), 0)))
                ),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in [dict(item) for item in _as_list(state.get("process_metrics_state_rows")) if isinstance(item, Mapping)]
        ]
    )
    state["process_maturity_hash_chain"] = canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "maturity_state": str(row.get("maturity_state", "")).strip(),
                "stabilization_score": int(
                    max(0, min(1000, _as_int(row.get("stabilization_score", 0), 0)))
                ),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in [dict(item) for item in _as_list(state.get("process_maturity_record_rows")) if isinstance(item, Mapping)]
        ]
    )
    state["process_cert_hash_chain"] = canonical_sha256(
        {
            "certificates": [
                {
                    "cert_id": str(row.get("cert_id", "")).strip(),
                    "process_id": str(row.get("process_id", "")).strip(),
                    "version": str(row.get("version", "")).strip(),
                    "cert_type_id": str(row.get("cert_type_id", "")).strip(),
                    "issued_tick": int(max(0, _as_int(row.get("issued_tick", 0), 0))),
                    "valid_until_tick": (
                        None
                        if row.get("valid_until_tick") is None
                        else int(max(0, _as_int(row.get("valid_until_tick", 0), 0)))
                    ),
                }
                for row in [dict(item) for item in _as_list(state.get("process_certification_artifact_rows")) if isinstance(item, Mapping)]
            ],
            "revocations": [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "cert_id": str(row.get("cert_id", "")).strip(),
                    "process_id": str(row.get("process_id", "")).strip(),
                    "version": str(row.get("version", "")).strip(),
                    "reason_code": str(row.get("reason_code", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                }
                for row in [dict(item) for item in _as_list(state.get("process_certification_revocation_rows")) if isinstance(item, Mapping)]
            ],
        }
    )
    state["drift_state_hash_chain"] = canonical_sha256(
        [
            {
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "drift_score": int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
                "drift_band": str(row.get("drift_band", "")).strip(),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in sorted(
                [
                    dict(item)
                    for item in _as_list(state.get("process_drift_state_rows"))
                    if isinstance(item, Mapping)
                ],
                key=lambda item: (
                    str(item.get("process_id", "")),
                    str(item.get("version", "")),
                ),
            )
        ]
    )
    state["drift_event_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "drift_band": str(row.get("drift_band", "")).strip(),
                "drift_score": int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "action_taken": str(row.get("action_taken", "")).strip(),
            }
            for row in sorted(
                [
                    dict(item)
                    for item in _as_list(state.get("drift_event_record_rows"))
                    if isinstance(item, Mapping)
                ],
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick", 0), 0))),
                    str(item.get("event_id", "")),
                ),
            )
        ]
    )
    state["qc_policy_change_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "from_qc_policy_id": str(row.get("from_qc_policy_id", "")).strip(),
                "to_qc_policy_id": str(row.get("to_qc_policy_id", "")).strip(),
                "reason_code": str(row.get("reason_code", "")).strip(),
            }
            for row in sorted(
                [
                    dict(item)
                    for item in _as_list(state.get("qc_policy_change_rows"))
                    if isinstance(item, Mapping)
                ],
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick", 0), 0))),
                    str(item.get("event_id", "")),
                ),
            )
        ]
    )
    state["revalidation_run_hash_chain"] = canonical_sha256(
        [
            {
                "revalidation_id": str(row.get("revalidation_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "trial_index": int(max(1, _as_int(row.get("trial_index", 1), 1))),
                "scheduled_tick": int(max(0, _as_int(row.get("scheduled_tick", 0), 0))),
                "status": str(row.get("status", "")).strip(),
            }
            for row in sorted(
                [
                    dict(item)
                    for item in _as_list(state.get("revalidation_run_rows"))
                    if isinstance(item, Mapping)
                ],
                key=lambda item: (
                    str(item.get("process_id", "")),
                    str(item.get("version", "")),
                    int(max(1, _as_int(item.get("trial_index", 1), 1))),
                    str(item.get("revalidation_id", "")),
                ),
            )
        ]
    )
    state["process_capsule_invalidation_hash_chain"] = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "reason_code": str(row.get("reason_code", "")).strip(),
            }
            for row in sorted(
                [
                    dict(item)
                    for item in _as_list(state.get("process_capsule_invalidation_rows"))
                    if isinstance(item, Mapping)
                ],
                key=lambda item: (
                    int(max(0, _as_int(item.get("tick", 0), 0))),
                    str(item.get("event_id", "")),
                ),
            )
        ]
    )

    finalized["extensions"] = dict(
        _as_map(finalized.get("extensions")),
        process_quality_hash_chain=str(state.get("process_quality_hash_chain", "")).strip(),
        batch_quality_hash_chain=str(state.get("batch_quality_hash_chain", "")).strip(),
        qc_result_hash_chain=str(state.get("qc_result_hash_chain", "")).strip(),
        sampling_decision_hash_chain=str(state.get("sampling_decision_hash_chain", "")).strip(),
        qc_drift_escalation_hash_chain=str(state.get("qc_drift_escalation_hash_chain", "")).strip(),
        qc_certification_hook_hash_chain=str(state.get("qc_certification_hook_hash_chain", "")).strip(),
        drift_state_hash_chain=str(state.get("drift_state_hash_chain", "")).strip(),
        drift_event_hash_chain=str(state.get("drift_event_hash_chain", "")).strip(),
        qc_policy_change_hash_chain=str(state.get("qc_policy_change_hash_chain", "")).strip(),
        revalidation_run_hash_chain=str(state.get("revalidation_run_hash_chain", "")).strip(),
        process_capsule_invalidation_hash_chain=str(
            state.get("process_capsule_invalidation_hash_chain", "")
        ).strip(),
        metrics_state_hash_chain=str(state.get("metrics_state_hash_chain", "")).strip(),
        process_maturity_hash_chain=str(state.get("process_maturity_hash_chain", "")).strip(),
        process_cert_hash_chain=str(state.get("process_cert_hash_chain", "")).strip(),
        current_maturity_state=str(state.get("current_maturity_state", "exploration")).strip(),
        process_capsule_eligible=bool(state.get("process_capsule_eligible", False)),
        process_capsule_forced_invalid=bool(state.get("process_capsule_forced_invalid", False)),
        current_drift_band=str(state.get("current_drift_band", "drift.normal")).strip(),
        current_drift_score=int(max(0, _as_int(state.get("current_drift_score", 0), 0))),
    )
    state["run_status"] = final_status
    state["deterministic_fingerprint"] = canonical_sha256(dict(state, deterministic_fingerprint=""))
    return {"result": "complete", "reason_code": "", "run_record_row": finalized, "run_state": state}


__all__ = [
    "REFUSAL_PROCESS_INVALID_DEFINITION",
    "REFUSAL_PROCESS_RUN_NOT_FOUND",
    "REFUSAL_PROCESS_LEDGER_REQUIRED",
    "REFUSAL_PROCESS_DIRECT_MASS_ENERGY_MUTATION",
    "build_process_quality_record_row",
    "build_process_run_record_row",
    "build_process_step_record_row",
    "process_run_start",
    "process_run_tick",
    "process_run_end",
]
