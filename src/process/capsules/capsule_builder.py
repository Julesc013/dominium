"""PROC-5 deterministic process-capsule generation helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.meta.compile import (
    evaluate_compile_request,
)
from src.meta.compile.compile_engine import (
    build_validity_domain_row,
)
from src.process.maturity import normalize_process_maturity_record_rows
from src.process.maturity.metrics_engine import normalize_process_metrics_state_rows
from src.specs import tolerance_policy_rows_by_id
from src.system.statevec import (
    state_vector_definition_for_owner,
)


REFUSAL_PROCESS_CAPSULE_INVALID = "refusal.process.capsule.invalid"
REFUSAL_PROCESS_CAPSULE_INELIGIBLE = "refusal.process.capsule.ineligible"
REFUSAL_PROCESS_CAPSULE_STATEVEC_REQUIRED = "refusal.process.capsule.statevec_required"
REFUSAL_PROCESS_CAPSULE_ERROR_BOUNDS_REQUIRED = "refusal.process.capsule.error_bounds_required"


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


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(item) for item in _as_list(body.get(key)) if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(item) for item in _as_list(record.get(key)) if isinstance(item, Mapping)]
    return []


def build_process_capsule_row(
    *,
    capsule_id: str,
    process_id: str,
    version: str,
    input_signature_ref: str,
    output_signature_ref: str,
    validity_domain_ref: str,
    error_bound_policy_id: str,
    state_vector_definition_id: str,
    coupling_budget_id: str,
    compiled_model_id: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "capsule_id": str(capsule_id or "").strip(),
        "process_id": str(process_id or "").strip(),
        "version": str(version or "").strip() or "1.0.0",
        "input_signature_ref": str(input_signature_ref or "").strip(),
        "output_signature_ref": str(output_signature_ref or "").strip(),
        "validity_domain_ref": str(validity_domain_ref or "").strip(),
        "error_bound_policy_id": str(error_bound_policy_id or "").strip(),
        "state_vector_definition_id": str(state_vector_definition_id or "").strip(),
        "coupling_budget_id": str(coupling_budget_id or "").strip(),
        "compiled_model_id": (None if compiled_model_id is None else str(compiled_model_id or "").strip() or None),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not all(
        (
            payload["capsule_id"],
            payload["process_id"],
            payload["input_signature_ref"],
            payload["output_signature_ref"],
            payload["validity_domain_ref"],
            payload["error_bound_policy_id"],
            payload["state_vector_definition_id"],
            payload["coupling_budget_id"],
        )
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_process_capsule_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("capsule_id", "")),
    ):
        normalized = build_process_capsule_row(
            capsule_id=str(row.get("capsule_id", "")).strip(),
            process_id=str(row.get("process_id", "")).strip(),
            version=str(row.get("version", "")).strip() or "1.0.0",
            input_signature_ref=str(row.get("input_signature_ref", "")).strip(),
            output_signature_ref=str(row.get("output_signature_ref", "")).strip(),
            validity_domain_ref=str(row.get("validity_domain_ref", "")).strip(),
            error_bound_policy_id=str(row.get("error_bound_policy_id", "")).strip(),
            state_vector_definition_id=str(row.get("state_vector_definition_id", "")).strip(),
            coupling_budget_id=str(row.get("coupling_budget_id", "")).strip(),
            compiled_model_id=(
                None
                if row.get("compiled_model_id") is None
                else str(row.get("compiled_model_id", "")).strip() or None
            ),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(normalized.get("capsule_id", "")).strip()
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def process_capsule_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("capsule_id", "")).strip(), dict(row))
        for row in normalize_process_capsule_rows(rows)
        if str(row.get("capsule_id", "")).strip()
    )


def build_capsule_generated_record_row(
    *,
    capsule_id: str,
    process_id: str,
    version: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "event_id": "event.process.capsule_generated.{}".format(
            canonical_sha256(
                {
                    "capsule_id": str(capsule_id or "").strip(),
                    "process_id": str(process_id or "").strip(),
                    "version": str(version or "").strip() or "1.0.0",
                    "tick": int(max(0, _as_int(tick, 0))),
                }
            )[:16]
        ),
        "capsule_id": str(capsule_id or "").strip(),
        "process_id": str(process_id or "").strip(),
        "version": str(version or "").strip() or "1.0.0",
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["capsule_id"]) or (not payload["process_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def _latest_maturity_state(
    *, process_id: str, version: str, process_maturity_record_rows: object
) -> str:
    token = "{}@{}".format(str(process_id or "").strip(), str(version or "").strip() or "1.0.0")
    state = "exploration"
    for row in sorted(
        normalize_process_maturity_record_rows(process_maturity_record_rows),
        key=lambda item: (
            str(item.get("process_id", "")),
            str(item.get("version", "")),
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("record_id", "")),
        ),
    ):
        key = "{}@{}".format(
            str(row.get("process_id", "")).strip(),
            str(row.get("version", "")).strip() or "1.0.0",
        )
        if key != token:
            continue
        state = str(row.get("maturity_state", "")).strip().lower() or state
    return state


def _metrics_for_process(
    *, process_id: str, version: str, process_metrics_state_rows: object
) -> dict:
    token = "{}@{}".format(str(process_id or "").strip(), str(version or "").strip() or "1.0.0")
    for row in sorted(
        normalize_process_metrics_state_rows(process_metrics_state_rows),
        key=lambda item: (
            str(item.get("process_id", "")),
            str(item.get("version", "")),
            int(max(0, _as_int(item.get("last_update_tick", 0), 0))),
        ),
    ):
        key = "{}@{}".format(
            str(row.get("process_id", "")).strip(),
            str(row.get("version", "")).strip() or "1.0.0",
        )
        if key == token:
            return dict(row)
    return {}


def _validity_ranges_from_metrics(metrics_row: Mapping[str, object]) -> dict:
    row = _as_map(metrics_row)
    ext = _as_map(row.get("extensions"))
    observed_ranges = _as_map(ext.get("observed_input_ranges"))
    if observed_ranges:
        out: Dict[str, dict] = {}
        for key, value in sorted(observed_ranges.items(), key=lambda item: str(item[0])):
            limits = _as_map(value)
            out[str(key).strip()] = {
                "min": int(max(0, _as_int(limits.get("min", 0), 0))),
                "max": int(max(0, _as_int(limits.get("max", 1000), 1000))),
            }
        return out

    yield_mean = int(max(0, min(1000, _as_int(row.get("yield_mean", 800), 800))))
    yield_variance = int(max(0, _as_int(row.get("yield_variance", 2000), 2000)))
    env_dev = int(max(0, min(1000, _as_int(row.get("env_deviation_score", 100), 100))))
    cal_dev = int(max(0, min(1000, _as_int(row.get("calibration_deviation_score", 100), 100))))
    spread = int(max(50, min(400, (yield_variance // 100) + 40)))
    return {
        "input.total_mass_raw": {"min": 0, "max": 100000000},
        "input.batch_quality_permille": {
            "min": int(max(0, yield_mean - spread)),
            "max": int(min(1000, yield_mean + spread)),
        },
        "environment.entropy_index": {
            "min": 0,
            "max": int(max(100, min(5000, 1500 + env_dev))),
        },
        "tool.wear_permille": {
            "min": 0,
            "max": int(max(200, min(1000, 1000 - (cal_dev // 2)))),
        },
    }


def _definition_signature_ref(
    *, process_id: str, version: str, process_definition_row: Mapping[str, object], io_key: str
) -> str:
    io_rows = [
        dict(item)
        for item in _as_list(_as_map(process_definition_row).get(io_key))
        if isinstance(item, Mapping)
    ]
    return "signature.process.{}.{}.{}.{}".format(
        str(process_id or "").strip().replace(".", "_"),
        str(version or "").strip().replace(".", "_"),
        str(io_key).strip(),
        canonical_sha256(io_rows)[:16],
    )


def generate_process_capsule(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    process_maturity_record_rows: object,
    process_metrics_state_rows: object,
    state_vector_definition_rows: object,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    process_definition_row: Mapping[str, object] | None = None,
    error_bound_policy_id: str = "tol.default",
    coupling_budget_id: str = "budget.coupling.process.default",
    compile_with_compiled_model: bool = False,
    compiled_type_registry_payload: Mapping[str, object] | None = None,
    verification_procedure_registry_payload: Mapping[str, object] | None = None,
    compile_policy_registry_payload: Mapping[str, object] | None = None,
    compile_policy_id: str = "compile.default",
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    process_token = str(process_id or "").strip()
    version_token = str(version or "").strip() or "1.0.0"
    if not process_token:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_INVALID,
            "message": "process_id is required",
        }

    maturity_state = _latest_maturity_state(
        process_id=process_token,
        version=version_token,
        process_maturity_record_rows=process_maturity_record_rows,
    )
    if maturity_state != "capsule_eligible":
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_INELIGIBLE,
            "message": "process is not capsule_eligible",
            "process_id": process_token,
            "version": version_token,
            "maturity_state": maturity_state,
        }

    state_owner_id = "process.{}@{}".format(process_token, version_token)
    state_definition = state_vector_definition_for_owner(
        owner_id=state_owner_id,
        state_vector_definition_rows=state_vector_definition_rows,
    )
    if not state_definition:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_STATEVEC_REQUIRED,
            "message": "missing state vector definition",
            "owner_id": state_owner_id,
        }

    error_policy = str(error_bound_policy_id or "").strip() or "tol.default"
    tolerance_rows = tolerance_policy_rows_by_id(tolerance_policy_registry_payload)
    if error_policy not in tolerance_rows:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_ERROR_BOUNDS_REQUIRED,
            "message": "error bound policy is not registered",
            "error_bound_policy_id": error_policy,
        }

    metrics_row = _metrics_for_process(
        process_id=process_token,
        version=version_token,
        process_metrics_state_rows=process_metrics_state_rows,
    )
    validity_ranges = _validity_ranges_from_metrics(metrics_row)
    validity_row = build_validity_domain_row(
        domain_id="validity_domain.process_capsule.{}".format(
            canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "ranges": validity_ranges,
                }
            )[:16]
        ),
        input_ranges=validity_ranges,
        timing_constraints={"tick_stride": 1},
        environmental_constraints={
            "env_deviation_max_permille": int(
                max(0, min(1000, _as_int(_as_map(metrics_row).get("env_deviation_score", 100), 100)))
            )
        },
        extensions={"source": "PROC5-3", "process_id": process_token, "version": version_token},
    )

    input_signature_ref = _definition_signature_ref(
        process_id=process_token,
        version=version_token,
        process_definition_row=_as_map(process_definition_row),
        io_key="input_signature",
    )
    output_signature_ref = _definition_signature_ref(
        process_id=process_token,
        version=version_token,
        process_definition_row=_as_map(process_definition_row),
        io_key="output_signature",
    )

    compile_request_row = {}
    compile_result_row = {}
    compiled_model_row = {}
    equivalence_proof_row = {}
    compile_validity_row = {}
    compiled_model_id = None
    compile_result_token = "skipped"

    if bool(compile_with_compiled_model):
        compile_request = {
            "request_id": "compile_request.process_capsule.{}".format(
                canonical_sha256(
                    {
                        "process_id": process_token,
                        "version": version_token,
                        "tick": tick,
                        "compile_policy_id": str(compile_policy_id or "compile.default"),
                    }
                )[:16]
            ),
            "source_kind": "process_graph",
            "source_ref": {
                "nodes": [
                    {
                        "node_id": str(step.get("step_id", "")).strip()
                        or "node.{}".format(index + 1),
                        "op": str(step.get("step_kind", "")).strip() or "passthrough",
                        "prunable": False,
                        "extensions": {"source": "process_definition"},
                    }
                    for index, step in enumerate(
                        _as_list(_as_map(_as_map(process_definition_row).get("step_graph")).get("steps"))
                    )
                    if isinstance(step, Mapping)
                ],
                "validity_domain": {
                    "domain_id": str(validity_row.get("domain_id", "")).strip(),
                    "input_ranges": _as_map(validity_row.get("input_ranges")),
                    "timing_constraints": _as_map(validity_row.get("timing_constraints")),
                    "environmental_constraints": _as_map(validity_row.get("environmental_constraints")),
                },
                "input_signature_ref": input_signature_ref,
                "output_signature_ref": output_signature_ref,
            },
            "target_compiled_type_id": "compiled.reduced_graph",
            "error_bound_policy_id": error_policy,
            "extensions": {
                "source": "PROC5-3",
                "process_id": process_token,
                "version": version_token,
            },
        }
        compile_eval = evaluate_compile_request(
            current_tick=tick,
            compile_request=compile_request,
            compiled_type_registry_payload=compiled_type_registry_payload,
            verification_procedure_registry_payload=verification_procedure_registry_payload,
            compile_policy_registry_payload=compile_policy_registry_payload,
            compile_policy_id=str(compile_policy_id or "").strip() or "compile.default",
        )
        compile_request_row = _as_map(compile_eval.get("compile_request_row"))
        compile_result_row = _as_map(compile_eval.get("compile_result_row"))
        compiled_model_row = _as_map(compile_eval.get("compiled_model_row"))
        equivalence_proof_row = _as_map(compile_eval.get("equivalence_proof_row"))
        compile_validity_row = _as_map(compile_eval.get("validity_domain_row"))
        if str(compile_eval.get("result", "")).strip() == "complete":
            compile_result_token = "complete"
            compiled_model_id = str(compiled_model_row.get("compiled_model_id", "")).strip() or None
            if compile_validity_row:
                validity_row = dict(compile_validity_row)
        else:
            compile_result_token = "refused"

    capsule_id = "process_capsule.{}".format(
        canonical_sha256(
            {
                "process_id": process_token,
                "version": version_token,
                "state_vector_owner_id": state_owner_id,
                "state_vector_definition_id": str(
                    state_definition.get("deterministic_fingerprint", "")
                ).strip(),
                "input_signature_ref": input_signature_ref,
                "output_signature_ref": output_signature_ref,
                "validity_domain_ref": str(validity_row.get("domain_id", "")).strip(),
                "error_bound_policy_id": error_policy,
                "compiled_model_id": compiled_model_id,
            }
        )[:16]
    )
    capsule_row = build_process_capsule_row(
        capsule_id=capsule_id,
        process_id=process_token,
        version=version_token,
        input_signature_ref=input_signature_ref,
        output_signature_ref=output_signature_ref,
        validity_domain_ref=str(validity_row.get("domain_id", "")).strip(),
        error_bound_policy_id=error_policy,
        state_vector_definition_id="statevec.definition.{}".format(
            canonical_sha256(
                {
                    "owner_id": state_owner_id,
                    "version": str(state_definition.get("version", "")).strip() or "1.0.0",
                    "fingerprint": str(state_definition.get("deterministic_fingerprint", "")).strip(),
                }
            )[:16]
        ),
        coupling_budget_id=str(coupling_budget_id or "").strip()
        or "budget.coupling.process.default",
        compiled_model_id=compiled_model_id,
        extensions={
            "source": "PROC5-3",
            "process_id": process_token,
            "version": version_token,
            "maturity_state": maturity_state,
            "state_vector_owner_id": state_owner_id,
            "compile_result": compile_result_token,
            "metrics_last_update_tick": int(
                max(0, _as_int(_as_map(metrics_row).get("last_update_tick", 0), 0))
            ),
            "default_yield_factor_permille": int(
                max(0, min(1000, _as_int(_as_map(metrics_row).get("yield_mean", 900), 900)))
            ),
            "extensions": _as_map(extensions),
        },
    )
    if not capsule_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_INVALID,
            "message": "failed to build process capsule row",
        }

    capsule_generated_row = build_capsule_generated_record_row(
        capsule_id=str(capsule_row.get("capsule_id", "")).strip(),
        process_id=process_token,
        version=version_token,
        tick=tick,
        extensions={
            "source": "PROC5-3",
            "validity_domain_ref": str(capsule_row.get("validity_domain_ref", "")).strip(),
            "compiled_model_id": (None if compiled_model_id is None else str(compiled_model_id)),
            "compile_result": compile_result_token,
        },
    )
    decision_log_row = {
        "tick": int(tick),
        "reason": "process_capsule_generated",
        "process_id": process_token,
        "version": version_token,
        "capsule_id": str(capsule_row.get("capsule_id", "")).strip(),
        "maturity_state": maturity_state,
        "compile_result": compile_result_token,
    }

    result = {
        "result": "complete",
        "reason_code": "",
        "process_capsule_row": capsule_row,
        "capsule_generated_record_row": capsule_generated_row,
        "validity_domain_row": validity_row,
        "state_vector_definition_row": dict(state_definition),
        "compile_request_row": compile_request_row,
        "compile_result_row": compile_result_row,
        "compiled_model_row": compiled_model_row,
        "equivalence_proof_row": equivalence_proof_row,
        "decision_log_row": decision_log_row,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
    }
    if not result["deterministic_fingerprint"]:
        result["deterministic_fingerprint"] = canonical_sha256(
            dict(result, deterministic_fingerprint="")
        )
    return result


__all__ = [
    "REFUSAL_PROCESS_CAPSULE_INVALID",
    "REFUSAL_PROCESS_CAPSULE_INELIGIBLE",
    "REFUSAL_PROCESS_CAPSULE_STATEVEC_REQUIRED",
    "REFUSAL_PROCESS_CAPSULE_ERROR_BOUNDS_REQUIRED",
    "build_process_capsule_row",
    "normalize_process_capsule_rows",
    "process_capsule_rows_by_id",
    "build_capsule_generated_record_row",
    "generate_process_capsule",
]

