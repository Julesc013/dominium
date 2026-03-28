"""PROC-6 deterministic drift scoring and revalidation helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_DRIFT_BANDS = ("drift.normal", "drift.warning", "drift.critical")


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _rows_from_registry(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    if isinstance(body.get(key), list):
        return [dict(item) for item in _as_list(body.get(key)) if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    if isinstance(record.get(key), list):
        return [dict(item) for item in _as_list(record.get(key)) if isinstance(item, Mapping)]
    return []


def _metric_key(process_id: object, version: object) -> str:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    return "{}@{}".format(process_token, version_token) if process_token else ""


def drift_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _rows_from_registry(registry_payload, "drift_policies")
    if not rows:
        rows = _rows_from_registry(registry_payload, "process_drift_policies")
    out: Dict[str, dict] = {}
    for row in rows:
        policy_id = _token(row.get("drift_policy_id")) or _token(
            row.get("process_drift_policy_id")
        )
        if not policy_id:
            continue
        weights = dict(
            (
                str(key).strip(),
                int(max(0, min(1000, _as_int(value, 0)))),
            )
            for key, value in sorted(
                _as_map(row.get("weights")).items(), key=lambda item: str(item[0])
            )
            if str(key).strip()
        )
        if not weights:
            weights = {
                "qc_fail_rate_delta": 250,
                "yield_variance_delta": 200,
                "environment_deviation_score": 150,
                "tool_degradation_score": 150,
                "calibration_deviation_score": 120,
                "entropy_growth_rate": 130,
            }
        thresholds = dict(
            (
                str(key).strip(),
                int(max(0, min(1000, _as_int(value, 0)))),
            )
            for key, value in sorted(
                _as_map(row.get("thresholds")).items(), key=lambda item: str(item[0])
            )
            if str(key).strip()
        )
        if not thresholds:
            warning = int(
                max(0, min(1000, _as_int(row.get("warning_threshold_permille", 450), 450)))
            )
            critical = int(
                max(
                    warning,
                    min(1000, _as_int(row.get("critical_threshold_permille", row.get("revocation_threshold_permille", 700)), 700)),
                )
            )
            thresholds = {
                "normal": int(max(0, warning // 2)),
                "warning": int(warning),
                "critical": int(critical),
            }
        qc_escalation_rules = dict(
            (str(key).strip(), value)
            for key, value in sorted(
                _as_map(row.get("qc_escalation_rules")).items(), key=lambda item: str(item[0])
            )
            if str(key).strip()
        )
        if not qc_escalation_rules:
            ext = _as_map(row.get("extensions"))
            qc_escalation_rules = {
                "warning_qc_policy_id": _token(ext.get("warning_qc_policy_id")) or "qc.strict_sampling",
                "critical_qc_policy_id": _token(ext.get("critical_qc_policy_id")) or "qc.strict_sampling",
            }
        payload = {
            "schema_version": "1.0.0",
            "drift_policy_id": str(policy_id),
            "process_drift_policy_id": _token(row.get("process_drift_policy_id")) or str(policy_id),
            "weights": dict(weights),
            "thresholds": {
                "normal": int(max(0, min(1000, _as_int(thresholds.get("normal", 250), 250)))),
                "warning": int(max(0, min(1000, _as_int(thresholds.get("warning", 450), 450)))),
                "critical": int(max(0, min(1000, _as_int(thresholds.get("critical", 700), 700)))),
            },
            "qc_escalation_rules": dict(qc_escalation_rules),
            "revalidation_trial_count": int(
                max(1, _as_int(row.get("revalidation_trial_count", 3), 3))
            ),
            "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
            "extensions": _as_map(row.get("extensions")),
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(
                dict(payload, deterministic_fingerprint="")
            )
        out[str(policy_id)] = payload
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_process_drift_state_row(
    *,
    process_id: str,
    version: str,
    drift_score: int,
    drift_band: str,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    band_token = _token(drift_band).lower() or "drift.normal"
    if (not process_token) or (band_token not in set(_DRIFT_BANDS)):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "process_id": process_token,
        "version": version_token,
        "drift_score": int(max(0, min(1000, _as_int(drift_score, 0)))),
        "drift_band": band_token,
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_process_drift_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            _token(item.get("process_id")),
            _token(item.get("version")) or "1.0.0",
            int(max(0, _as_int(item.get("last_update_tick", 0), 0))),
        ),
    ):
        normalized = build_process_drift_state_row(
            process_id=_token(row.get("process_id")),
            version=_token(row.get("version")) or "1.0.0",
            drift_score=int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
            drift_band=_token(row.get("drift_band")) or "drift.normal",
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        key = _metric_key(normalized.get("process_id"), normalized.get("version"))
        if key:
            out[key] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def process_drift_rows_by_key(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_process_drift_state_rows(rows):
        key = _metric_key(row.get("process_id"), row.get("version"))
        if key:
            out[key] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_drift_event_record_row(
    *,
    event_id: str,
    process_id: str,
    version: str,
    drift_band: str,
    drift_score: int,
    tick: int,
    action_taken: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    band_token = _token(drift_band).lower() or "drift.normal"
    action_token = _token(action_taken)
    if (
        (not process_token)
        or (band_token not in set(_DRIFT_BANDS))
        or (not action_token)
    ):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": _token(event_id),
        "process_id": process_token,
        "version": version_token,
        "drift_band": band_token,
        "drift_score": int(max(0, min(1000, _as_int(drift_score, 0)))),
        "tick": int(max(0, _as_int(tick, 0))),
        "action_taken": action_token,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.process.drift.{}".format(
            canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "drift_band": band_token,
                    "drift_score": int(payload["drift_score"]),
                    "tick": int(payload["tick"]),
                    "action_taken": action_token,
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_drift_event_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            _token(item.get("event_id")),
        ),
    ):
        normalized = build_drift_event_record_row(
            event_id=_token(row.get("event_id")),
            process_id=_token(row.get("process_id")),
            version=_token(row.get("version")) or "1.0.0",
            drift_band=_token(row.get("drift_band")) or "drift.normal",
            drift_score=int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            action_taken=_token(row.get("action_taken")) or "qc_escalate",
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = _token(normalized.get("event_id"))
        if event_id:
            out[event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_revalidation_run_row(
    *,
    revalidation_id: str,
    process_id: str,
    version: str,
    trial_index: int,
    scheduled_tick: int,
    status: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    status_token = _token(status).lower() or "scheduled"
    if status_token not in {
        "scheduled",
        "completed_pass",
        "completed_fail",
    }:
        return {}
    if not process_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "revalidation_id": _token(revalidation_id),
        "process_id": process_token,
        "version": version_token,
        "trial_index": int(max(1, _as_int(trial_index, 1))),
        "scheduled_tick": int(max(0, _as_int(scheduled_tick, 0))),
        "status": status_token,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["revalidation_id"]:
        payload["revalidation_id"] = "revalidation.process.{}".format(
            canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "trial_index": int(payload["trial_index"]),
                    "scheduled_tick": int(payload["scheduled_tick"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_revalidation_run_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            _token(item.get("process_id")),
            _token(item.get("version")) or "1.0.0",
            int(max(1, _as_int(item.get("trial_index", 1), 1))),
            _token(item.get("revalidation_id")),
        ),
    ):
        normalized = build_revalidation_run_row(
            revalidation_id=_token(row.get("revalidation_id")),
            process_id=_token(row.get("process_id")),
            version=_token(row.get("version")) or "1.0.0",
            trial_index=int(max(1, _as_int(row.get("trial_index", 1), 1))),
            scheduled_tick=int(max(0, _as_int(row.get("scheduled_tick", 0), 0))),
            status=_token(row.get("status")) or "scheduled",
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        token = _token(normalized.get("revalidation_id"))
        if token:
            out[token] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _band_for_score(score: int, thresholds: Mapping[str, object]) -> str:
    warning = int(max(0, min(1000, _as_int(_as_map(thresholds).get("warning", 450), 450))))
    critical = int(max(warning, min(1000, _as_int(_as_map(thresholds).get("critical", 700), 700))))
    value = int(max(0, min(1000, _as_int(score, 0))))
    if value >= critical:
        return "drift.critical"
    if value >= warning:
        return "drift.warning"
    return "drift.normal"


def _compute_drift_components(
    *,
    previous_metrics_row: Mapping[str, object] | None,
    metrics_row: Mapping[str, object],
    environment_deviation_score: int,
    tool_degradation_score: int,
    calibration_deviation_score: int,
    entropy_growth_rate: int,
) -> dict:
    previous = _as_map(previous_metrics_row)
    current = _as_map(metrics_row)
    previous_qc_pass = int(max(0, min(1000, _as_int(previous.get("qc_pass_rate", current.get("qc_pass_rate", 1000)), 1000))))
    current_qc_pass = int(max(0, min(1000, _as_int(current.get("qc_pass_rate", 1000), 1000))))
    previous_variance = int(max(0, _as_int(previous.get("yield_variance", current.get("yield_variance", 0)), 0)))
    current_variance = int(max(0, _as_int(current.get("yield_variance", 0), 0)))
    qc_fail_rate_delta = int(
        max(0, min(1000, (1000 - current_qc_pass) - (1000 - previous_qc_pass)))
    )
    yield_variance_delta = int(max(0, min(1000, (current_variance - previous_variance) // 10)))
    return {
        "qc_fail_rate_delta": int(qc_fail_rate_delta),
        "yield_variance_delta": int(yield_variance_delta),
        "environment_deviation_score": int(max(0, min(1000, _as_int(environment_deviation_score, 0)))),
        "tool_degradation_score": int(max(0, min(1000, _as_int(tool_degradation_score, 0)))),
        "calibration_deviation_score": int(max(0, min(1000, _as_int(calibration_deviation_score, 0)))),
        "entropy_growth_rate": int(max(0, min(1000, _as_int(entropy_growth_rate, 0)))),
    }


def evaluate_process_drift(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    drift_policy_row: Mapping[str, object],
    previous_metrics_row: Mapping[str, object] | None,
    metrics_row: Mapping[str, object],
    previous_drift_state_row: Mapping[str, object] | None = None,
    environment_deviation_score: int = 0,
    tool_degradation_score: int = 0,
    calibration_deviation_score: int = 0,
    entropy_growth_rate: int = 0,
    reliability_failure_count: int = 0,
    update_stride: int = 1,
    force_update: bool = False,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    stride = int(max(1, _as_int(update_stride, 1)))
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    previous_state = _as_map(previous_drift_state_row)
    policy = _as_map(drift_policy_row)
    thresholds = _as_map(policy.get("thresholds"))
    weights = _as_map(policy.get("weights"))

    if (not bool(force_update)) and stride > 1 and (tick % stride != 0):
        retained = (
            dict(previous_state)
            if previous_state
            else build_process_drift_state_row(
                process_id=process_token,
                version=version_token,
                drift_score=0,
                drift_band="drift.normal",
                last_update_tick=0,
                extensions={
                    "source": "PROC6-3",
                    "deferred": True,
                    "drift_policy_id": _token(policy.get("drift_policy_id")) or "drift.default",
                },
            )
        )
        result = {
            "result": "deferred",
            "reason_code": "degrade.process.drift_stride",
            "drift_state_row": retained,
            "drift_event_row": {},
            "qc_escalation_required": False,
            "capsule_invalidation_required": False,
            "certification_revocation_required": False,
            "revalidation_required": False,
            "force_expand_required": False,
            "escalated_qc_policy_id": "",
            "revalidation_trial_count": int(
                max(1, _as_int(policy.get("revalidation_trial_count", 3), 3))
            ),
            "decision_log_row": {
                "tick": int(tick),
                "process_id": process_token,
                "version": version_token,
                "reason": "drift_update_deferred",
                "reason_code": "degrade.process.drift_stride",
                "update_stride": int(stride),
            },
        }
        result["deterministic_fingerprint"] = canonical_sha256(
            dict(result, deterministic_fingerprint="")
        )
        return result

    components = _compute_drift_components(
        previous_metrics_row=previous_metrics_row,
        metrics_row=metrics_row,
        environment_deviation_score=environment_deviation_score,
        tool_degradation_score=tool_degradation_score,
        calibration_deviation_score=calibration_deviation_score,
        entropy_growth_rate=entropy_growth_rate,
    )
    if int(max(0, _as_int(reliability_failure_count, 0))) > 0:
        reliability_uplift = int(
            max(
                0,
                min(1000, int(_as_int(reliability_failure_count, 0)) * 40),
            )
        )
        components["entropy_growth_rate"] = int(
            max(0, min(1000, int(components["entropy_growth_rate"]) + reliability_uplift))
        )

    weighted_sum = 0
    total_weight = 0
    for key in sorted(components.keys()):
        weight = int(max(0, _as_int(weights.get(key, 0), 0)))
        weighted_sum += weight * int(components[key])
        total_weight += weight
    if total_weight <= 0:
        total_weight = 1
    drift_score = int(max(0, min(1000, weighted_sum // total_weight)))
    drift_band = _band_for_score(drift_score, thresholds)
    previous_band = _token(previous_state.get("drift_band")).lower() or "drift.normal"

    state_row = build_process_drift_state_row(
        process_id=process_token,
        version=version_token,
        drift_score=int(drift_score),
        drift_band=str(drift_band),
        last_update_tick=int(tick),
        extensions={
            "source": "PROC6-3",
            "drift_policy_id": _token(policy.get("drift_policy_id")) or "drift.default",
            "components": dict(components),
            "previous_drift_band": str(previous_band),
        },
    )

    escalation_rules = _as_map(policy.get("qc_escalation_rules"))
    warning_qc_policy = _token(escalation_rules.get("warning_qc_policy_id")) or "qc.strict_sampling"
    critical_qc_policy = _token(escalation_rules.get("critical_qc_policy_id")) or warning_qc_policy
    revalidation_trial_count = int(
        max(1, _as_int(policy.get("revalidation_trial_count", 3), 3))
    )

    qc_escalation_required = drift_band in {"drift.warning", "drift.critical"}
    capsule_invalidation_required = drift_band == "drift.critical"
    certification_revocation_required = drift_band == "drift.critical"
    revalidation_required = drift_band == "drift.critical"
    force_expand_required = drift_band == "drift.critical"
    escalated_qc_policy_id = (
        critical_qc_policy if drift_band == "drift.critical" else warning_qc_policy
    )

    action_taken = ""
    if drift_band == "drift.warning":
        action_taken = "qc_escalate"
    elif drift_band == "drift.critical":
        action_taken = "revalidate_required"

    event_row = (
        build_drift_event_record_row(
            event_id="",
            process_id=process_token,
            version=version_token,
            drift_band=str(drift_band),
            drift_score=int(drift_score),
            tick=int(tick),
            action_taken=str(action_taken),
            extensions={
                "source": "PROC6-3",
                "drift_policy_id": _token(policy.get("drift_policy_id")) or "drift.default",
                "qc_escalation_required": bool(qc_escalation_required),
                "capsule_invalidation_required": bool(capsule_invalidation_required),
                "certification_revocation_required": bool(certification_revocation_required),
                "revalidation_trial_count": int(revalidation_trial_count),
            },
        )
        if (
            drift_band != "drift.normal"
            and (drift_band != previous_band or drift_score >= int(_as_int(thresholds.get("warning", 450), 450)))
        )
        else {}
    )

    decision_log_row = {
        "tick": int(tick),
        "process_id": process_token,
        "version": version_token,
        "reason": "drift_evaluated",
        "drift_band": str(drift_band),
        "drift_score": int(drift_score),
        "drift_policy_id": _token(policy.get("drift_policy_id")) or "drift.default",
    }
    out = {
        "result": "complete",
        "reason_code": "",
        "drift_state_row": state_row,
        "drift_event_row": event_row,
        "qc_escalation_required": bool(qc_escalation_required),
        "capsule_invalidation_required": bool(capsule_invalidation_required),
        "certification_revocation_required": bool(certification_revocation_required),
        "revalidation_required": bool(revalidation_required),
        "force_expand_required": bool(force_expand_required),
        "escalated_qc_policy_id": str(escalated_qc_policy_id),
        "revalidation_trial_count": int(revalidation_trial_count),
        "decision_log_row": decision_log_row,
        "components": dict(components),
    }
    out["deterministic_fingerprint"] = canonical_sha256(
        dict(out, deterministic_fingerprint="")
    )
    return out


def schedule_revalidation_trials(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    trial_count: int,
    existing_rows: object,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    trials = int(max(1, _as_int(trial_count, 1)))
    rows = normalize_revalidation_run_rows(existing_rows)
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    active_rows = [
        dict(row)
        for row in rows
        if str(row.get("process_id", "")).strip() == process_token
        and str(row.get("version", "")).strip() == version_token
        and str(row.get("status", "")).strip() == "scheduled"
    ]
    if active_rows:
        return {
            "result": "complete",
            "scheduled_rows": [],
            "revalidation_rows": rows,
            "deterministic_fingerprint": canonical_sha256(
                {"rows": rows, "scheduled_rows": [], "tick": int(tick)}
            ),
        }
    scheduled_rows: List[dict] = []
    for index in range(1, trials + 1):
        scheduled_rows.append(
            build_revalidation_run_row(
                revalidation_id="",
                process_id=process_token,
                version=version_token,
                trial_index=int(index),
                scheduled_tick=int(tick + index),
                status="scheduled",
                extensions={
                    "source": "PROC6-5",
                    "required_micro_run": True,
                },
            )
        )
    merged = normalize_revalidation_run_rows(rows + scheduled_rows)
    out = {
        "result": "complete",
        "scheduled_rows": [dict(row) for row in scheduled_rows if row],
        "revalidation_rows": merged,
    }
    out["deterministic_fingerprint"] = canonical_sha256(
        dict(out, deterministic_fingerprint="")
    )
    return out


def apply_revalidation_trial_result(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    run_passed: bool,
    revalidation_rows: object,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    rows = normalize_revalidation_run_rows(revalidation_rows)
    updated: List[dict] = []
    consumed = False
    consumed_row = {}
    for row in rows:
        item = dict(row)
        if consumed:
            updated.append(item)
            continue
        if (
            str(item.get("process_id", "")).strip() != process_token
            or str(item.get("version", "")).strip() != version_token
            or str(item.get("status", "")).strip() != "scheduled"
            or int(max(0, _as_int(item.get("scheduled_tick", 0), 0))) > tick
        ):
            updated.append(item)
            continue
        consumed = True
        item = build_revalidation_run_row(
            revalidation_id=str(item.get("revalidation_id", "")).strip(),
            process_id=process_token,
            version=version_token,
            trial_index=int(max(1, _as_int(item.get("trial_index", 1), 1))),
            scheduled_tick=int(max(0, _as_int(item.get("scheduled_tick", 0), 0))),
            status=("completed_pass" if bool(run_passed) else "completed_fail"),
            extensions=dict(
                _as_map(item.get("extensions")),
                completed_tick=int(tick),
            ),
        )
        consumed_row = dict(item)
        updated.append(item)
    if not consumed:
        updated = rows
    updated = normalize_revalidation_run_rows(updated)
    pass_count = len(
        [
            row
            for row in updated
            if str(row.get("process_id", "")).strip() == process_token
            and str(row.get("version", "")).strip() == version_token
            and str(row.get("status", "")).strip() == "completed_pass"
        ]
    )
    fail_count = len(
        [
            row
            for row in updated
            if str(row.get("process_id", "")).strip() == process_token
            and str(row.get("version", "")).strip() == version_token
            and str(row.get("status", "")).strip() == "completed_fail"
        ]
    )
    pending_count = len(
        [
            row
            for row in updated
            if str(row.get("process_id", "")).strip() == process_token
            and str(row.get("version", "")).strip() == version_token
            and str(row.get("status", "")).strip() == "scheduled"
        ]
    )
    out = {
        "result": "complete",
        "revalidation_rows": updated,
        "consumed": bool(consumed),
        "consumed_row": consumed_row,
        "pass_count": int(pass_count),
        "fail_count": int(fail_count),
        "pending_count": int(pending_count),
    }
    out["deterministic_fingerprint"] = canonical_sha256(
        dict(out, deterministic_fingerprint="")
    )
    return out


__all__ = [
    "build_drift_event_record_row",
    "build_process_drift_state_row",
    "build_revalidation_run_row",
    "drift_policy_rows_by_id",
    "evaluate_process_drift",
    "normalize_drift_event_record_rows",
    "normalize_process_drift_state_rows",
    "normalize_revalidation_run_rows",
    "process_drift_rows_by_key",
    "schedule_revalidation_trials",
    "apply_revalidation_trial_result",
]
