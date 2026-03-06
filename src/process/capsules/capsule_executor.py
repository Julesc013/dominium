"""PROC-5 deterministic process-capsule execution helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.chem.process_run_engine import build_batch_quality_row
from src.meta.compile import compiled_model_execute, compiled_model_is_valid
from src.process.capsules.capsule_builder import (
    REFUSAL_PROCESS_CAPSULE_INVALID,
    normalize_process_capsule_rows,
    process_capsule_rows_by_id,
)
from src.process.process_run_engine import (
    build_process_quality_record_row,
    build_process_run_record_row,
)
from src.process.qc.qc_engine import evaluate_qc_for_run
from src.system.statevec import (
    build_state_vector_definition_row,
    normalize_state_vector_definition_rows,
    normalize_state_vector_snapshot_rows,
    serialize_state,
    state_vector_definition_for_owner,
)


REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN = "refusal.process.capsule.out_of_domain"
REFUSAL_PROCESS_CAPSULE_EXECUTION_REFUSED = "refusal.process.capsule.execution_refused"


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


def build_capsule_execution_record_row(
    *,
    exec_id: str,
    capsule_id: str,
    tick_start: int,
    tick_end: int,
    inputs_hash: str,
    outputs_hash: str,
    qc_outcome_hash: str | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "exec_id": str(exec_id or "").strip(),
        "capsule_id": str(capsule_id or "").strip(),
        "tick_range": {
            "start_tick": int(max(0, _as_int(tick_start, 0))),
            "end_tick": int(max(0, _as_int(tick_end, 0))),
        },
        "inputs_hash": str(inputs_hash or "").strip(),
        "outputs_hash": str(outputs_hash or "").strip(),
        "qc_outcome_hash": (None if qc_outcome_hash is None else str(qc_outcome_hash or "").strip() or None),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["exec_id"]) or (not payload["capsule_id"]):
        return {}
    if not payload["inputs_hash"]:
        payload["inputs_hash"] = canonical_sha256(
            {"capsule_id": payload["capsule_id"], "tick_range": payload["tick_range"], "seed": "inputs"}
        )
    if not payload["outputs_hash"]:
        payload["outputs_hash"] = canonical_sha256(
            {"capsule_id": payload["capsule_id"], "tick_range": payload["tick_range"], "seed": "outputs"}
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_capsule_execution_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("exec_id", "")),
    ):
        tick_range = _as_map(row.get("tick_range"))
        normalized = build_capsule_execution_record_row(
            exec_id=str(row.get("exec_id", "")).strip(),
            capsule_id=str(row.get("capsule_id", "")).strip(),
            tick_start=int(max(0, _as_int(tick_range.get("start_tick", 0), 0))),
            tick_end=int(max(0, _as_int(tick_range.get("end_tick", 0), 0))),
            inputs_hash=str(row.get("inputs_hash", "")).strip(),
            outputs_hash=str(row.get("outputs_hash", "")).strip(),
            qc_outcome_hash=(
                None
                if row.get("qc_outcome_hash") is None
                else str(row.get("qc_outcome_hash", "")).strip() or None
            ),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        token = str(normalized.get("exec_id", "")).strip()
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def build_process_capsule_invalidation_row(
    *,
    capsule_id: str,
    process_id: str,
    version: str,
    tick: int,
    reason_code: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "event_id": "event.process.capsule_invalidated.{}".format(
            canonical_sha256(
                {
                    "capsule_id": str(capsule_id or "").strip(),
                    "process_id": str(process_id or "").strip(),
                    "version": str(version or "").strip() or "1.0.0",
                    "tick": int(max(0, _as_int(tick, 0))),
                    "reason_code": str(reason_code or "").strip(),
                }
            )[:16]
        ),
        "capsule_id": str(capsule_id or "").strip(),
        "process_id": str(process_id or "").strip(),
        "version": str(version or "").strip() or "1.0.0",
        "tick": int(max(0, _as_int(tick, 0))),
        "reason_code": str(reason_code or "").strip(),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if (not payload["capsule_id"]) or (not payload["process_id"]) or (not payload["reason_code"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def _input_features(
    *,
    input_batch_rows: Sequence[Mapping[str, object]],
    environment_entropy_index: int,
    tool_wear_permille: int,
) -> dict:
    rows = [dict(item) for item in list(input_batch_rows or []) if isinstance(item, Mapping)]
    total_mass = int(sum(max(0, _as_int(row.get("quantity_mass_raw", 0), 0)) for row in rows))
    quality_values: List[int] = []
    for row in rows:
        quality = _as_int(_as_map(row.get("quality_distribution")).get("yield_factor_permille", 900), 900)
        quality_values.append(int(max(0, min(1000, quality))))
    quality_mean = int(sum(quality_values) // len(quality_values)) if quality_values else 900
    return {
        "input.total_mass_raw": int(max(0, total_mass)),
        "input.batch_quality_permille": int(max(0, min(1000, quality_mean))),
        "environment.entropy_index": int(max(0, _as_int(environment_entropy_index, 0))),
        "tool.wear_permille": int(max(0, min(1000, _as_int(tool_wear_permille, 0)))),
    }


def _range_violations(validity_row: Mapping[str, object], features: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    feature_map = _as_map(features)
    for key, raw_limits in sorted(_as_map(_as_map(validity_row).get("input_ranges")).items(), key=lambda item: str(item[0])):
        token = str(key or "").strip()
        if (not token) or token not in feature_map:
            continue
        limits = _as_map(raw_limits)
        value = _as_int(feature_map.get(token), 0)
        if "min" in limits and value < _as_int(limits.get("min"), value):
            violations.append("input_range_low:{}".format(token))
        if "max" in limits and value > _as_int(limits.get("max"), value):
            violations.append("input_range_high:{}".format(token))
    return violations


def _quality_outcomes(
    *,
    features: Mapping[str, object],
    capsule_row: Mapping[str, object],
) -> dict:
    feature_map = _as_map(features)
    capsule_ext = _as_map(_as_map(capsule_row).get("extensions"))
    base_yield = int(max(0, min(1000, _as_int(capsule_ext.get("default_yield_factor_permille", 900), 900))))
    quality = int(max(0, min(1000, _as_int(feature_map.get("input.batch_quality_permille", 900), 900))))
    entropy = int(max(0, _as_int(feature_map.get("environment.entropy_index", 0), 0)))
    wear = int(max(0, min(1000, _as_int(feature_map.get("tool.wear_permille", 0), 0))))

    yield_factor = int(base_yield + max(0, quality - 850) // 3 - (entropy // 20) - (wear // 8))
    yield_factor = int(max(0, min(1000, yield_factor)))
    defect_flags: List[str] = []
    if yield_factor < 700:
        defect_flags.append("incomplete")
    if quality < 650:
        defect_flags.append("contamination")
    if wear > 900:
        defect_flags.append("overprocessed")
    quality_grade = "grade.A"
    if defect_flags or yield_factor < 900:
        quality_grade = "grade.B"
    if yield_factor < 760 or len(defect_flags) >= 2:
        quality_grade = "grade.C"
    return {
        "yield_factor": int(yield_factor),
        "defect_flags": _tokens(defect_flags),
        "quality_grade": str(quality_grade),
    }


def evaluate_process_capsule_invalidation(
    *,
    current_tick: int,
    capsule_row: Mapping[str, object],
    qc_fail_rate_permille: int,
    drift_score_permille: int,
    spec_revision_hash: str | None,
    expected_spec_revision_hash: str | None,
) -> dict:
    row = _as_map(capsule_row)
    ext = _as_map(row.get("extensions"))
    reason = ""
    if int(max(0, _as_int(qc_fail_rate_permille, 0))) >= int(
        max(0, _as_int(ext.get("qc_fail_invalidate_threshold_permille", 500), 500))
    ):
        reason = "capsule.qc_failure_spike"
    elif int(max(0, _as_int(drift_score_permille, 0))) >= int(
        max(0, _as_int(ext.get("drift_invalidate_threshold_permille", 600), 600))
    ):
        reason = "capsule.drift_exceeded"
    elif str(spec_revision_hash or "").strip() and str(expected_spec_revision_hash or "").strip() and (
        str(spec_revision_hash).strip() != str(expected_spec_revision_hash).strip()
    ):
        reason = "capsule.spec_revision_changed"

    invalidation_row = (
        build_process_capsule_invalidation_row(
            capsule_id=str(row.get("capsule_id", "")).strip(),
            process_id=str(row.get("process_id", "")).strip(),
            version=str(row.get("version", "")).strip() or "1.0.0",
            tick=int(max(0, _as_int(current_tick, 0))),
            reason_code=reason,
            extensions={
                "qc_fail_rate_permille": int(max(0, _as_int(qc_fail_rate_permille, 0))),
                "drift_score_permille": int(max(0, _as_int(drift_score_permille, 0))),
                "spec_revision_hash": str(spec_revision_hash or "").strip() or None,
                "expected_spec_revision_hash": str(expected_spec_revision_hash or "").strip() or None,
            },
        )
        if reason
        else {}
    )
    return {
        "invalid": bool(reason),
        "reason_code": reason,
        "invalidation_row": invalidation_row,
        "deterministic_fingerprint": canonical_sha256(
            {
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "reason_code": reason,
                "tick": int(max(0, _as_int(current_tick, 0))),
            }
        ),
    }


def execute_process_capsule(
    *,
    current_tick: int,
    capsule_id: str,
    process_capsule_rows: object,
    validity_domain_rows: object,
    input_batch_rows: Sequence[Mapping[str, object]],
    output_batch_ids: object = None,
    process_quality_record_rows: Sequence[Mapping[str, object]] | None = None,
    qc_policy_registry_payload: Mapping[str, object] | None = None,
    sampling_strategy_registry_payload: Mapping[str, object] | None = None,
    test_procedure_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    compiled_model_rows: object | None = None,
    state_vector_definition_rows: object | None = None,
    state_vector_snapshot_rows: object | None = None,
    environment_entropy_index: int = 0,
    tool_wear_permille: int = 0,
    allow_forced_expand: bool = True,
    allow_micro_fallback: bool = True,
    requester_subject_id: str | None = None,
    instrument_id: str | None = None,
    calibration_cert_id: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    capsule_token = str(capsule_id or "").strip()
    capsule_rows = process_capsule_rows_by_id(process_capsule_rows)
    capsule_row = dict(capsule_rows.get(capsule_token) or {})
    if not capsule_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_INVALID,
            "message": "capsule_id is not registered",
            "capsule_id": capsule_token,
        }

    validity_rows = {
        str(row.get("domain_id", "")).strip(): dict(row)
        for row in _as_list(validity_domain_rows)
        if isinstance(row, Mapping) and str(row.get("domain_id", "")).strip()
    }
    validity_row = dict(validity_rows.get(str(capsule_row.get("validity_domain_ref", "")).strip()) or {})
    if not validity_row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_INVALID,
            "message": "missing validity domain for capsule",
            "capsule_id": capsule_token,
        }

    features = _input_features(
        input_batch_rows=input_batch_rows,
        environment_entropy_index=environment_entropy_index,
        tool_wear_permille=tool_wear_permille,
    )
    violations = _range_violations(validity_row=validity_row, features=features)
    if violations:
        forced_expand_event = {
            "event_id": "event.process.capsule_forced_expand.{}".format(
                canonical_sha256(
                    {
                        "capsule_id": capsule_token,
                        "tick": tick,
                        "violations": list(violations),
                    }
                )[:16]
            ),
            "capsule_id": capsule_token,
            "process_id": str(capsule_row.get("process_id", "")).strip(),
            "version": str(capsule_row.get("version", "")).strip() or "1.0.0",
            "tick": int(tick),
            "reason_code": REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN,
            "deterministic_fingerprint": "",
            "extensions": {
                "violations": list(violations),
                "allow_micro_fallback": bool(allow_micro_fallback),
            },
        }
        forced_expand_event["deterministic_fingerprint"] = canonical_sha256(
            dict(forced_expand_event, deterministic_fingerprint="")
        )
        if bool(allow_forced_expand):
            return {
                "result": "forced_expand",
                "reason_code": REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN,
                "forced_expand_event_row": forced_expand_event,
                "micro_fallback_requested": bool(allow_micro_fallback),
                "violations": list(violations),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "capsule_id": capsule_token,
                        "result": "forced_expand",
                        "violations": list(violations),
                        "tick": tick,
                    }
                ),
            }
        return {
            "result": "refused",
            "reason_code": REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN,
            "message": "capsule inputs are out of validity domain",
            "violations": list(violations),
        }

    capsule_ext = _as_map(capsule_row.get("extensions"))
    compiled_model_id = str(capsule_row.get("compiled_model_id", "")).strip()
    compiled_model_used = False
    compiled_validation = {"valid": False, "reason_code": "", "violations": []}
    compiled_execution = {"result": "skipped"}
    next_state_definition_rows = list(state_vector_definition_rows or [])
    next_state_snapshot_rows = list(state_vector_snapshot_rows or [])
    if compiled_model_id:
        compiled_validation = compiled_model_is_valid(
            compiled_model_id=compiled_model_id,
            current_inputs=features,
            compiled_model_rows=compiled_model_rows or [],
            validity_domain_rows=validity_domain_rows or [],
            state_vector_definition_rows=next_state_definition_rows,
        )
        if bool(compiled_validation.get("valid", False)):
            compiled_execution = compiled_model_execute(
                compiled_model_id=compiled_model_id,
                inputs=features,
                compiled_model_rows=compiled_model_rows or [],
                validity_domain_rows=validity_domain_rows or [],
                state_vector_definition_rows=next_state_definition_rows,
                state_vector_snapshot_rows=next_state_snapshot_rows,
                current_tick=tick,
            )
            if str(compiled_execution.get("result", "")).strip() == "complete":
                compiled_model_used = True
                state_def = _as_map(compiled_execution.get("state_vector_definition_row"))
                state_snap = _as_map(compiled_execution.get("state_vector_snapshot_row"))
                if state_def:
                    next_state_definition_rows = normalize_state_vector_definition_rows(
                        list(next_state_definition_rows) + [state_def]
                    )
                if state_snap:
                    next_state_snapshot_rows = normalize_state_vector_snapshot_rows(
                        list(next_state_snapshot_rows) + [state_snap]
                    )

    quality = _quality_outcomes(features=features, capsule_row=capsule_row)
    input_total_mass = int(max(0, _as_int(features.get("input.total_mass_raw", 0), 0)))
    output_total_mass = int((input_total_mass * int(quality.get("yield_factor", 0))) // 1000)
    output_ids = _tokens(output_batch_ids)
    if not output_ids:
        output_ids = [
            "batch.output.capsule.{}".format(
                canonical_sha256(
                    {
                        "capsule_id": capsule_token,
                        "tick": tick,
                        "index": 1,
                    }
                )[:16]
            )
        ]
    mass_per_batch = int(output_total_mass // max(1, len(output_ids)))

    run_id = "run.process_capsule.{}".format(
        canonical_sha256({"capsule_id": capsule_token, "tick": tick, "output_ids": output_ids})[:16]
    )
    input_refs = [
        {
            "name": "input_{}".format(index + 1),
            "ref_id": str(row.get("batch_id", "")).strip()
            or "batch.input.capsule.{}".format(index + 1),
            "ref_type": "batch",
        }
        for index, row in enumerate(
            [dict(item) for item in list(input_batch_rows or []) if isinstance(item, Mapping)]
        )
    ]
    output_refs = [
        {"name": "output_{}".format(index + 1), "ref_id": batch_id, "ref_type": "batch"}
        for index, batch_id in enumerate(output_ids)
    ]
    run_record_row = build_process_run_record_row(
        run_id=run_id,
        process_id=str(capsule_row.get("process_id", "")).strip(),
        version=str(capsule_row.get("version", "")).strip() or "1.0.0",
        start_tick=tick,
        end_tick=tick,
        status="completed",
        input_refs=input_refs,
        output_refs=output_refs,
        extensions={
            "source": "PROC5-4",
            "capsule_run": True,
            "capsule_id": capsule_token,
            "compiled_model_used": bool(compiled_model_used),
            "compiled_model_id": compiled_model_id or None,
            "input_features": dict(features),
            "macro_time_cost_ticks": int(max(1, _as_int(capsule_ext.get("macro_time_cost_ticks", 1), 1))),
        },
    )
    quality_row = build_process_quality_record_row(
        run_id=run_id,
        yield_factor=int(quality.get("yield_factor", 0)),
        defect_flags=list(quality.get("defect_flags") or []),
        quality_grade=str(quality.get("quality_grade", "grade.C")),
        extensions={
            "source": "PROC5-4",
            "capsule_run": True,
            "capsule_id": capsule_token,
            "defect_severity": int(
                min(1000, max(0, len(list(quality.get("defect_flags") or [])) * 250))
            ),
            "output_total_mass_raw": int(output_total_mass),
        },
    )
    batch_quality_rows: List[dict] = []
    for index, batch_id in enumerate(output_ids):
        batch_quality_rows.append(
            build_batch_quality_row(
                batch_id=str(batch_id),
                quality_grade=str(quality.get("quality_grade", "grade.C")),
                defect_flags=list(quality.get("defect_flags") or []),
                contamination_tags=(
                    ["contamination.process_capsule"]
                    if "contamination" in set(_tokens(quality.get("defect_flags")))
                    else []
                ),
                yield_factor=int(quality.get("yield_factor", 0)),
                extensions={
                    "source": "PROC5-4",
                    "capsule_id": capsule_token,
                    "run_id": run_id,
                    "output_index": int(index),
                    "quantity_mass_raw": int(mass_per_batch),
                },
            )
        )
    batch_quality_rows = [dict(row) for row in batch_quality_rows if row]

    qc_policy_id = str(capsule_ext.get("qc_policy_id", "")).strip() or "qc.none"
    qc_eval = evaluate_qc_for_run(
        current_tick=tick,
        run_id=run_id,
        qc_policy_id=qc_policy_id,
        batch_quality_rows=batch_quality_rows,
        process_quality_record_rows=list(process_quality_record_rows or []) + [quality_row],
        qc_policy_registry_payload=qc_policy_registry_payload,
        sampling_strategy_registry_payload=sampling_strategy_registry_payload,
        test_procedure_registry_payload=test_procedure_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        instrument_id=instrument_id,
        calibration_cert_id=calibration_cert_id,
        requester_subject_id=requester_subject_id,
    )

    inputs_hash = canonical_sha256(
        {
            "capsule_id": capsule_token,
            "features": dict(features),
            "input_batch_ids": _tokens(item.get("ref_id") for item in input_refs),
        }
    )
    outputs_hash = canonical_sha256(
        {
            "capsule_id": capsule_token,
            "yield_factor": int(quality.get("yield_factor", 0)),
            "defect_flags": _tokens(quality.get("defect_flags")),
            "quality_grade": str(quality.get("quality_grade", "")),
            "output_batch_ids": list(output_ids),
            "output_total_mass_raw": int(output_total_mass),
        }
    )
    qc_hash = str(qc_eval.get("qc_result_hash_chain", "")).strip() or None

    exec_row = build_capsule_execution_record_row(
        exec_id="capsule.exec.{}".format(
            canonical_sha256(
                {
                    "capsule_id": capsule_token,
                    "run_id": run_id,
                    "tick": tick,
                    "inputs_hash": inputs_hash,
                    "outputs_hash": outputs_hash,
                    "qc_hash": qc_hash,
                }
            )[:16]
        ),
        capsule_id=capsule_token,
        tick_start=tick,
        tick_end=tick,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        qc_outcome_hash=qc_hash,
        extensions={
            "source": "PROC5-4",
            "run_id": run_id,
            "process_id": str(capsule_row.get("process_id", "")).strip(),
            "version": str(capsule_row.get("version", "")).strip() or "1.0.0",
            "compiled_model_used": bool(compiled_model_used),
        },
    )

    state_owner_id = "process_capsule.{}".format(capsule_token)
    state_definition = state_vector_definition_for_owner(
        owner_id=state_owner_id,
        state_vector_definition_rows=next_state_definition_rows,
    )
    if not state_definition:
        fallback = build_state_vector_definition_row(
            owner_id=state_owner_id,
            version="1.0.0",
            state_fields=[
                {"field_id": "run_id", "path": "run_id", "field_kind": "id", "default": ""},
                {"field_id": "progress", "path": "progress", "field_kind": "fixed_point", "default": 1000},
                {"field_id": "status", "path": "status", "field_kind": "text", "default": "completed"},
            ],
            deterministic_fingerprint="",
            extensions={"source": "PROC5-4.fallback"},
        )
        if fallback:
            next_state_definition_rows = normalize_state_vector_definition_rows(
                list(next_state_definition_rows) + [fallback]
            )
            state_definition = dict(fallback)
    state_serialization = (
        serialize_state(
            owner_id=state_owner_id,
            source_state={"run_id": run_id, "progress": 1000, "status": "completed"},
            state_vector_definition_rows=next_state_definition_rows,
            current_tick=tick,
            expected_version=str(_as_map(state_definition).get("version", "")).strip() or "1.0.0",
            extensions={"source": "PROC5-4", "capsule_id": capsule_token},
        )
        if state_definition
        else {"result": "refused", "reason_code": REFUSAL_PROCESS_CAPSULE_EXECUTION_REFUSED}
    )
    if str(state_serialization.get("result", "")).strip() == "complete":
        state_snapshot_row = _as_map(state_serialization.get("snapshot_row"))
        if state_snapshot_row:
            next_state_snapshot_rows = normalize_state_vector_snapshot_rows(
                list(next_state_snapshot_rows) + [state_snapshot_row]
            )
    else:
        state_snapshot_row = {}

    energy_transform_rows = [
        {
            "event_id": "event.process.capsule.energy.{}".format(
                canonical_sha256({"capsule_id": capsule_token, "run_id": run_id, "tick": tick})[:16]
            ),
            "capsule_id": capsule_token,
            "run_id": run_id,
            "tick": int(tick),
            "energy_delta_raw": int(max(0, output_total_mass // 2)),
            "deterministic_fingerprint": "",
            "extensions": {"source": "PROC5-4"},
        }
    ]
    energy_transform_rows[0]["deterministic_fingerprint"] = canonical_sha256(
        dict(energy_transform_rows[0], deterministic_fingerprint="")
    )
    emission_rows = [
        {
            "event_id": "event.process.capsule.emission.{}".format(
                canonical_sha256({"capsule_id": capsule_token, "run_id": run_id, "tick": tick})[:16]
            ),
            "capsule_id": capsule_token,
            "run_id": run_id,
            "tick": int(tick),
            "pollutant_id": str(capsule_ext.get("pollutant_id", "pollutant.pm25")).strip()
            or "pollutant.pm25",
            "emitted_mass_raw": int(max(0, input_total_mass - output_total_mass)),
            "deterministic_fingerprint": "",
            "extensions": {"source": "PROC5-4"},
        }
    ]
    emission_rows[0]["deterministic_fingerprint"] = canonical_sha256(
        dict(emission_rows[0], deterministic_fingerprint="")
    )

    result = {
        "result": "complete",
        "reason_code": "",
        "run_record_row": run_record_row,
        "process_quality_record_row": quality_row,
        "batch_quality_rows": batch_quality_rows,
        "qc_result_rows": [dict(row) for row in _as_list(qc_eval.get("qc_result_rows")) if isinstance(row, Mapping)],
        "qc_measurement_rows": [dict(row) for row in _as_list(qc_eval.get("measurement_rows")) if isinstance(row, Mapping)],
        "sampling_decision_rows": [dict(row) for row in _as_list(qc_eval.get("decision_rows")) if isinstance(row, Mapping)],
        "capsule_execution_record_row": exec_row,
        "energy_transform_rows": energy_transform_rows,
        "emission_rows": emission_rows,
        "compiled_model_used": bool(compiled_model_used),
        "compiled_model_validation": dict(compiled_validation),
        "compiled_model_execution": dict(compiled_execution),
        "state_vector_definition_rows": [dict(row) for row in next_state_definition_rows if isinstance(row, Mapping)],
        "state_vector_snapshot_rows": [dict(row) for row in next_state_snapshot_rows if isinstance(row, Mapping)],
        "state_vector_snapshot_row": state_snapshot_row,
        "inputs_hash": str(inputs_hash),
        "outputs_hash": str(outputs_hash),
        "qc_outcome_hash": qc_hash,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
    }
    if not result["deterministic_fingerprint"]:
        result["deterministic_fingerprint"] = canonical_sha256(
            dict(result, deterministic_fingerprint="")
        )
    return result


__all__ = [
    "REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN",
    "REFUSAL_PROCESS_CAPSULE_EXECUTION_REFUSED",
    "build_capsule_execution_record_row",
    "normalize_capsule_execution_record_rows",
    "build_process_capsule_invalidation_row",
    "evaluate_process_capsule_invalidation",
    "execute_process_capsule",
]

