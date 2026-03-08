"""Deterministic LOGIC-10 degradation ordering helpers."""

from __future__ import annotations

from typing import Iterable, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def logic_degradation_order_rows() -> list[dict]:
    rows = [
        {
            "rank": 1,
            "action_id": "prefer_compiled_execution",
            "decision_target": "compiled_model",
            "log_targets": ["logic_throttle_event", "compute_consumption_record"],
        },
        {
            "rank": 2,
            "action_id": "reduce_low_priority_eval_frequency",
            "decision_target": "tick_bucket_stride",
            "log_targets": ["logic_throttle_event", "explain.logic_compute_throttle"],
        },
        {
            "rank": 3,
            "action_id": "cap_networks_per_tick",
            "decision_target": "network_eval_cap",
            "log_targets": ["logic_throttle_event", "compute_consumption_record"],
        },
        {
            "rank": 4,
            "action_id": "reduce_debug_sampling_rate",
            "decision_target": "debug_sampling_policy",
            "log_targets": ["logic_throttle_event", "explain.logic_debug_throttled"],
        },
        {
            "rank": 5,
            "action_id": "refuse_new_debug_sessions",
            "decision_target": "debug_session_admission",
            "log_targets": ["logic_throttle_event", "explain.logic_debug_refused"],
        },
        {
            "rank": 6,
            "action_id": "apply_fail_safe_outputs",
            "decision_target": "safety_pattern",
            "log_targets": ["logic_throttle_event", "explain.logic_command_refused"],
        },
    ]
    out = []
    for row in rows:
        payload = dict(row)
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out.append(payload)
    return out


def plan_logic_degradation_actions(
    *,
    compiled_available: bool,
    current_tick: int,
    requested_network_ids: Iterable[object],
    low_priority_network_ids: Iterable[object],
    safety_critical_network_ids: Iterable[object],
    skipped_network_ids: Iterable[object],
    per_tick_network_cap: int,
    tick_bucket_stride: int,
    active_debug_sessions: int,
    debug_session_capacity: int,
) -> dict:
    requested = sorted(set(_token(item) for item in requested_network_ids if _token(item)))
    low_priority = sorted(set(_token(item) for item in low_priority_network_ids if _token(item)))
    safety_critical = sorted(set(_token(item) for item in safety_critical_network_ids if _token(item)))
    skipped = sorted(set(_token(item) for item in skipped_network_ids if _token(item)))
    plan_rows = []
    tick = int(max(0, _as_int(current_tick, 0)))
    network_cap = int(max(0, _as_int(per_tick_network_cap, 0)))
    stride = int(max(1, _as_int(tick_bucket_stride, 1)))
    session_count = int(max(0, _as_int(active_debug_sessions, 0)))
    session_capacity = int(max(0, _as_int(debug_session_capacity, 0)))

    if bool(compiled_available):
        plan_rows.append(
            {
                "rank": 1,
                "action_id": "prefer_compiled_execution",
                "status": "applied",
                "reason_code": "degrade.logic.prefer_compiled",
                "affected_ids": requested,
            }
        )
    if low_priority and stride > 1:
        deferred_ids = [token for token in low_priority if (tick % stride) != 0]
        plan_rows.append(
            {
                "rank": 2,
                "action_id": "reduce_low_priority_eval_frequency",
                "status": "applied" if deferred_ids else "noop",
                "reason_code": "degrade.logic.tick_bucket",
                "affected_ids": deferred_ids,
                "tick_bucket_stride": stride,
            }
        )
    if network_cap > 0:
        capped_ids = requested[network_cap:]
        plan_rows.append(
            {
                "rank": 3,
                "action_id": "cap_networks_per_tick",
                "status": "applied" if capped_ids else "noop",
                "reason_code": "degrade.logic.network_cap",
                "affected_ids": capped_ids,
                "network_eval_cap": network_cap,
            }
        )
    if session_capacity > 0:
        overflow = max(0, session_count - session_capacity)
        plan_rows.append(
            {
                "rank": 4,
                "action_id": "reduce_debug_sampling_rate",
                "status": "applied" if overflow > 0 else "noop",
                "reason_code": "degrade.logic.debug_subsample",
                "affected_count": int(overflow),
                "throttle_strategy": "deterministic_subsample",
            }
        )
        plan_rows.append(
            {
                "rank": 5,
                "action_id": "refuse_new_debug_sessions",
                "status": "applied" if overflow > 0 else "noop",
                "reason_code": "degrade.logic.debug_refusal",
                "affected_count": int(overflow),
            }
        )
    triggered_fail_safe = [token for token in skipped if token in set(safety_critical)]
    plan_rows.append(
        {
            "rank": 6,
            "action_id": "apply_fail_safe_outputs",
            "status": "applied" if triggered_fail_safe else "noop",
            "reason_code": "degrade.logic.fail_safe",
            "affected_ids": triggered_fail_safe,
        }
    )
    plan_rows = sorted(
        (dict(row) for row in plan_rows),
        key=lambda row: (int(_as_int(row.get("rank", 0), 0)), _token(row.get("action_id"))),
    )
    return {
        "current_tick": tick,
        "plan_rows": plan_rows,
        "plan_hash": canonical_sha256(plan_rows),
        "deterministic_fingerprint": canonical_sha256(
            {
                "current_tick": tick,
                "requested_network_ids": requested,
                "low_priority_network_ids": low_priority,
                "safety_critical_network_ids": safety_critical,
                "skipped_network_ids": skipped,
                "per_tick_network_cap": network_cap,
                "tick_bucket_stride": stride,
                "active_debug_sessions": session_count,
                "debug_session_capacity": session_capacity,
                "plan_rows": plan_rows,
            }
        ),
    }


__all__ = ["logic_degradation_order_rows", "plan_logic_degradation_actions"]
