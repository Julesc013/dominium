"""PROC-4 deterministic maturity scoring and lifecycle transition helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_MATURITY_STATES = (
    "exploration",
    "defined",
    "stabilized",
    "certified",
    "capsule_eligible",
)


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


def build_process_maturity_record_row(
    *,
    record_id: str,
    process_id: str,
    version: str,
    maturity_state: str,
    stabilization_score: int,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    state_token = _token(maturity_state).lower() or "exploration"
    if (not process_token) or state_token not in _MATURITY_STATES:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "record_id": _token(record_id),
        "process_id": process_token,
        "version": version_token,
        "maturity_state": state_token,
        "stabilization_score": int(max(0, min(1000, _as_int(stabilization_score, 0)))),
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["record_id"]:
        payload["record_id"] = "record.process.maturity.{}".format(
            canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "maturity_state": state_token,
                    "stabilization_score": int(payload["stabilization_score"]),
                    "tick": int(payload["tick"]),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def normalize_process_maturity_record_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            _token(item.get("process_id")),
            _token(item.get("version")) or "1.0.0",
            int(max(0, _as_int(item.get("tick", 0), 0))),
            _token(item.get("record_id")),
        ),
    ):
        normalized = build_process_maturity_record_row(
            record_id=_token(row.get("record_id")),
            process_id=_token(row.get("process_id")),
            version=_token(row.get("version")) or "1.0.0",
            maturity_state=_token(row.get("maturity_state")) or "exploration",
            stabilization_score=int(max(0, min(1000, _as_int(row.get("stabilization_score", 0), 0)))),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        record_id = _token(normalized.get("record_id"))
        if record_id:
            out[record_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def process_lifecycle_policy_rows_by_id(
    registry_payload: Mapping[str, object] | None,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _rows_from_registry(registry_payload, "process_lifecycle_policies"):
        policy_id = _token(row.get("process_lifecycle_policy_id"))
        if not policy_id:
            continue
        allowed = sorted(
            set(
                _token(item).lower()
                for item in _as_list(row.get("allowed_states"))
                if _token(item).lower() in set(_MATURITY_STATES + ("drifted", "capsule"))
            )
        )
        payload = {
            "schema_version": "1.0.0",
            "process_lifecycle_policy_id": policy_id,
            "allowed_states": allowed,
            "allow_capsule_without_certification": bool(
                row.get("allow_capsule_without_certification", False)
            ),
            "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
            "extensions": _as_map(row.get("extensions")),
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(
                dict(payload, deterministic_fingerprint="")
            )
        out[policy_id] = payload
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def compute_stabilization_score(
    *, metrics_row: Mapping[str, object], stabilization_policy_row: Mapping[str, object]
) -> int:
    row = _as_map(metrics_row)
    policy = _as_map(stabilization_policy_row)
    weights = _as_map(policy.get("weights"))

    runs_count = int(max(0, _as_int(row.get("runs_count", 0), 0)))
    min_runs = int(max(1, _as_int(policy.get("min_runs", 1), 1)))
    runs_norm = int(max(0, min(1000, (runs_count * 1000) // min_runs)))

    yield_variance = int(max(0, _as_int(row.get("yield_variance", 0), 0)))
    consistency = int(max(0, min(1000, 1000 - min(1000, yield_variance // 50))))

    qc_pass = int(max(0, min(1000, _as_int(row.get("qc_pass_rate", 0), 0))))
    defect_rate = int(max(0, min(1000, _as_int(row.get("defect_rate", 0), 0))))
    env_dev = int(max(0, min(1000, _as_int(row.get("env_deviation_score", 0), 0))))
    cal_dev = int(
        max(0, min(1000, _as_int(row.get("calibration_deviation_score", 0), 0)))
    )

    w_runs = int(max(0, _as_int(weights.get("runs", 0), 0)))
    w_consistency = int(max(0, _as_int(weights.get("consistency", 0), 0)))
    w_qc = int(max(0, _as_int(weights.get("qc_pass", 0), 0)))
    w_defect = int(max(0, _as_int(weights.get("defect", 0), 0)))
    w_env = int(max(0, _as_int(weights.get("environment", 0), 0)))
    w_cal = int(max(0, _as_int(weights.get("calibration", 0), 0)))

    total_weight = int(max(1, w_runs + w_consistency + w_qc + w_defect + w_env + w_cal))
    raw = (
        (w_runs * runs_norm)
        + (w_consistency * consistency)
        + (w_qc * qc_pass)
        - (w_defect * defect_rate)
        - (w_env * env_dev)
        - (w_cal * cal_dev)
    )
    score = int(raw // total_weight)
    return int(max(0, min(1000, score)))


def evaluate_process_maturity(
    *,
    current_tick: int,
    process_id: str,
    version: str,
    metrics_row: Mapping[str, object],
    previous_maturity_state: str,
    previous_state_extensions: Mapping[str, object] | None,
    stabilization_policy_row: Mapping[str, object],
    lifecycle_policy_row: Mapping[str, object] | None,
    certification_gate_passed: bool,
    certification_required: bool,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    prev_state = _token(previous_maturity_state).lower() or "exploration"
    if prev_state not in _MATURITY_STATES:
        prev_state = "exploration"

    policy = _as_map(stabilization_policy_row)
    thresholds = _as_map(policy.get("thresholds"))
    min_runs = int(max(0, _as_int(policy.get("min_runs", 0), 0)))
    horizon = int(max(0, _as_int(policy.get("stability_horizon_ticks", 0), 0)))
    score = compute_stabilization_score(
        metrics_row=_as_map(metrics_row), stabilization_policy_row=policy
    )

    runs_count = int(max(0, _as_int(_as_map(metrics_row).get("runs_count", 0), 0)))
    qc_pass_rate = int(max(0, min(1000, _as_int(_as_map(metrics_row).get("qc_pass_rate", 0), 0))))
    defect_rate = int(max(0, min(1000, _as_int(_as_map(metrics_row).get("defect_rate", 0), 0))))

    threshold_defined = int(max(0, _as_int(thresholds.get("defined", 0), 0)))
    threshold_stabilized = int(max(0, _as_int(thresholds.get("stabilized", 0), 0)))
    threshold_certified = int(max(0, _as_int(thresholds.get("certified", 0), 0)))
    threshold_capsule = int(max(0, _as_int(thresholds.get("capsule_eligible", 0), 0)))
    cert_qc_min = int(max(0, _as_int(thresholds.get("cert_qc_min", 0), 0)))
    cert_defect_max = int(max(0, _as_int(thresholds.get("cert_defect_max", 1000), 1000)))

    ext = _as_map(previous_state_extensions)
    first_certified_tick = int(max(0, _as_int(ext.get("first_certified_tick", 0), 0)))

    next_state = "exploration"
    deny_reason = ""

    if runs_count >= max(min_runs, 1) and score >= threshold_defined:
        next_state = "defined"
    if runs_count >= max(min_runs, 1) and score >= threshold_stabilized:
        next_state = "stabilized"

    cert_gate_ok = bool(certification_gate_passed) and score >= threshold_certified
    cert_gate_ok = cert_gate_ok and qc_pass_rate >= cert_qc_min and defect_rate <= cert_defect_max
    if bool(certification_required) and not bool(certification_gate_passed):
        cert_gate_ok = False
        deny_reason = "certification_gate_failed"
    if score < threshold_certified:
        deny_reason = "score_below_certified_threshold"
    elif qc_pass_rate < cert_qc_min:
        deny_reason = "qc_pass_rate_below_minimum"
    elif defect_rate > cert_defect_max:
        deny_reason = "defect_rate_above_maximum"

    if next_state == "stabilized" and cert_gate_ok:
        next_state = "certified"
        if first_certified_tick <= 0:
            first_certified_tick = tick
    elif prev_state in {"certified", "capsule_eligible"} and cert_gate_ok:
        next_state = "certified"
        if first_certified_tick <= 0:
            first_certified_tick = tick
    else:
        if next_state != "certified":
            first_certified_tick = 0

    if next_state == "certified" and score >= threshold_capsule:
        if horizon <= 0 or (tick - first_certified_tick) >= horizon:
            next_state = "capsule_eligible"

    lifecycle_policy = _as_map(lifecycle_policy_row)
    allowed_states = set(
        _token(item).lower() for item in _as_list(lifecycle_policy.get("allowed_states"))
    )
    if allowed_states and next_state not in allowed_states:
        deny_reason = "state_disallowed_by_lifecycle_policy"
        if "stabilized" in allowed_states and next_state in {"certified", "capsule_eligible"}:
            next_state = "stabilized"
        elif "defined" in allowed_states and next_state == "stabilized":
            next_state = "defined"
        elif "exploration" in allowed_states:
            next_state = "exploration"

    changed = next_state != prev_state
    record = (
        build_process_maturity_record_row(
            record_id="",
            process_id=process_token,
            version=version_token,
            maturity_state=next_state,
            stabilization_score=score,
            tick=tick,
            extensions={
                "source": "PROC4-4",
                "previous_maturity_state": prev_state,
                "policy_id": _token(policy.get("policy_id")) or "stab.default",
                "first_certified_tick": int(first_certified_tick),
                "deny_reason": deny_reason,
            },
        )
        if changed
        else {}
    )
    observation_row = (
        {
            "artifact_type_id": "artifact.observation.process_maturity_evaluation",
            "process_id": process_token,
            "version": version_token,
            "tick": int(tick),
            "maturity_state": next_state,
            "stabilization_score": int(score),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "tick": int(tick),
                    "maturity_state": next_state,
                    "stabilization_score": int(score),
                    "source": "PROC4-4",
                }
            ),
            "extensions": {
                "source": "PROC4-4",
                "policy_id": _token(policy.get("policy_id")) or "stab.default",
                "deny_reason": deny_reason,
            },
        }
        if not changed
        else {}
    )
    explain_row = {
        "artifact_type_id": "artifact.explain.process_maturity_change",
        "event_kind_id": (
            "process.maturity.transition" if changed else "process.maturity.no_transition"
        ),
        "process_id": process_token,
        "version": version_token,
        "tick": int(tick),
        "maturity_state": next_state,
        "stabilization_score": int(score),
        "deterministic_fingerprint": canonical_sha256(
            {
                "process_id": process_token,
                "version": version_token,
                "tick": int(tick),
                "state": next_state,
                "score": int(score),
                "changed": bool(changed),
                "deny_reason": deny_reason,
            }
        ),
        "extensions": {
            "source": "PROC4-4",
            "previous_maturity_state": prev_state,
            "changed": bool(changed),
            "deny_reason": deny_reason,
        },
    }

    out = {
        "result": "complete",
        "process_id": process_token,
        "version": version_token,
        "stabilization_score": int(score),
        "previous_maturity_state": prev_state,
        "next_maturity_state": next_state,
        "changed": bool(changed),
        "record_row": record,
        "observation_row": observation_row,
        "explain_row": explain_row,
        "state_extensions": {
            "first_certified_tick": int(first_certified_tick),
            "deny_reason": deny_reason,
            "policy_id": _token(policy.get("policy_id")) or "stab.default",
        },
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def build_process_certificate_artifact_row(
    *,
    cert_id: str,
    process_id: str,
    version: str,
    cert_type_id: str,
    issuer_subject_id: str,
    issued_tick: int,
    valid_until_tick: int | None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    cert_type_token = _token(cert_type_id) or "cert.process.default"
    issuer_token = _token(issuer_subject_id) or "subject.system.process_certifier"
    if not process_token:
        return {}
    issued = int(max(0, _as_int(issued_tick, 0)))
    valid_until = (
        None
        if valid_until_tick is None
        else int(max(issued, _as_int(valid_until_tick, issued)))
    )
    payload = {
        "schema_version": "1.0.0",
        "cert_id": _token(cert_id),
        "process_id": process_token,
        "version": version_token,
        "cert_type_id": cert_type_token,
        "issuer_subject_id": issuer_token,
        "issued_tick": int(issued),
        "valid_until_tick": valid_until,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["cert_id"]:
        payload["cert_id"] = "cert.process.{}".format(
            canonical_sha256(
                {
                    "process_id": process_token,
                    "version": version_token,
                    "cert_type_id": cert_type_token,
                    "issuer_subject_id": issuer_token,
                    "issued_tick": int(issued),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


def build_process_certificate_revocation_row(
    *,
    event_id: str,
    cert_id: str,
    process_id: str,
    version: str,
    cert_type_id: str,
    reason_code: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    process_token = _token(process_id)
    version_token = _token(version) or "1.0.0"
    cert_token = _token(cert_id)
    cert_type_token = _token(cert_type_id) or "cert.process.default"
    reason_token = _token(reason_code) or "process.certification_revoked"
    tick_value = int(max(0, _as_int(tick, 0)))
    if (not process_token) or (not cert_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": _token(event_id),
        "cert_id": cert_token,
        "process_id": process_token,
        "version": version_token,
        "cert_type_id": cert_type_token,
        "reason_code": reason_token,
        "tick": int(tick_value),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _as_map(extensions),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.process.cert_revocation.{}".format(
            canonical_sha256(
                {
                    "cert_id": cert_token,
                    "process_id": process_token,
                    "version": version_token,
                    "reason_code": reason_token,
                    "tick": int(tick_value),
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(
            dict(payload, deterministic_fingerprint="")
        )
    return payload


__all__ = [
    "build_process_maturity_record_row",
    "normalize_process_maturity_record_rows",
    "process_lifecycle_policy_rows_by_id",
    "compute_stabilization_score",
    "evaluate_process_maturity",
    "build_process_certificate_artifact_row",
    "build_process_certificate_revocation_row",
]
