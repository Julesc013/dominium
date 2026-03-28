"""SIG-7 deterministic degradation policy helpers."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_SIG_NONESSENTIAL_SEND = "refusal.sig.nonessential_send_budget"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_bool(value: object) -> bool:
    return bool(value)


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def apply_sig_budget_degradation(
    *,
    current_tick: int,
    budget_envelope_id: str,
    queue_depth: int,
    base_message_cap: int,
    base_aggregation_section_cap: int,
    pending_broadcast_count: int,
    pending_low_priority_count: int,
    nonessential_send_candidate_count: int,
    strict_profile_enabled: bool,
    allow_broadcast_fanout_degrade: bool = True,
) -> dict:
    """Apply SIG deterministic degradation order under budget pressure.

    Ordered policy:
    1) reduce message processing per tick (queue remains)
    2) reduce aggregation fidelity
    3) reduce broadcast fanout (policy-based, disabled in ranked by default)
    4) delay low-priority bulletins
    5) refuse non-essential sends with refusal code
    """

    tick = int(max(0, _as_int(current_tick, 0)))
    envelope_id = str(budget_envelope_id or "").strip() or "sig.envelope.standard"
    base_cap = int(max(1, _as_int(base_message_cap, 1)))
    base_section_cap = int(max(1, _as_int(base_aggregation_section_cap, 1)))
    pending_broadcast = int(max(0, _as_int(pending_broadcast_count, 0)))
    pending_low_priority = int(max(0, _as_int(pending_low_priority_count, 0)))
    nonessential_candidates = int(max(0, _as_int(nonessential_send_candidate_count, 0)))
    queue = int(max(0, _as_int(queue_depth, 0)))
    overload_ratio_permille = int((queue * 1000) // base_cap)

    message_cap = int(base_cap)
    aggregation_mode = "full"
    aggregation_section_cap = int(base_section_cap)
    broadcast_fanout_cap = None
    delay_low_priority = False
    refuse_nonessential = False
    refusal_codes: List[str] = []
    applied_steps: List[int] = []
    decision_log_rows: List[dict] = []

    def _append_step(step_index: int, step_name: str, details: Mapping[str, object]) -> None:
        decision_log_rows.append(
            {
                "decision_id": "decision.sig.degrade.{}".format(
                    canonical_sha256(
                        {
                            "tick": int(tick),
                            "budget_envelope_id": envelope_id,
                            "step_index": int(step_index),
                            "step_name": str(step_name),
                            "details": dict(details or {}),
                        }
                    )[:16]
                ),
                "tick": int(tick),
                "process_id": "process.sig_budget_degrade",
                "budget_envelope_id": envelope_id,
                "step_index": int(step_index),
                "step_name": str(step_name),
                "details": dict(details or {}),
            }
        )

    if overload_ratio_permille > 1000:
        message_cap = int(max(1, base_cap // 2))
        applied_steps.append(1)
        _append_step(
            1,
            "reduce_message_processing_cap",
            {
                "queue_depth": int(queue),
                "base_message_cap": int(base_cap),
                "message_cap": int(message_cap),
                "overload_ratio_permille": int(overload_ratio_permille),
            },
        )

    if overload_ratio_permille > 1500:
        aggregation_mode = "coarse"
        aggregation_section_cap = int(max(1, base_section_cap // 2))
        applied_steps.append(2)
        _append_step(
            2,
            "reduce_aggregation_fidelity",
            {
                "aggregation_mode": str(aggregation_mode),
                "aggregation_section_cap": int(aggregation_section_cap),
                "base_aggregation_section_cap": int(base_section_cap),
            },
        )

    if (
        overload_ratio_permille > 2000
        and allow_broadcast_fanout_degrade
        and (not _as_bool(strict_profile_enabled))
        and pending_broadcast > 0
    ):
        broadcast_fanout_cap = int(max(1, pending_broadcast // 2))
        applied_steps.append(3)
        _append_step(
            3,
            "reduce_broadcast_fanout",
            {
                "pending_broadcast_count": int(pending_broadcast),
                "broadcast_fanout_cap": int(broadcast_fanout_cap),
                "strict_profile_enabled": bool(strict_profile_enabled),
            },
        )

    if overload_ratio_permille > 2500 and pending_low_priority > 0:
        delay_low_priority = True
        applied_steps.append(4)
        _append_step(
            4,
            "delay_low_priority_bulletins",
            {
                "pending_low_priority_count": int(pending_low_priority),
                "delay_ticks": 1,
            },
        )

    if overload_ratio_permille > 3000 and nonessential_candidates > 0:
        refuse_nonessential = True
        refusal_codes.append(REFUSAL_SIG_NONESSENTIAL_SEND)
        applied_steps.append(5)
        _append_step(
            5,
            "refuse_nonessential_sends",
            {
                "nonessential_send_candidate_count": int(nonessential_candidates),
                "refusal_codes": list(refusal_codes),
            },
        )

    payload = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "budget_envelope_id": envelope_id,
        "overload_ratio_permille": int(overload_ratio_permille),
        "message_cap": int(message_cap),
        "aggregation_mode": str(aggregation_mode),
        "aggregation_section_cap": int(aggregation_section_cap),
        "broadcast_fanout_cap": None if broadcast_fanout_cap is None else int(broadcast_fanout_cap),
        "delay_low_priority": bool(delay_low_priority),
        "refuse_nonessential": bool(refuse_nonessential),
        "refusal_codes": list(sorted(set(str(item).strip() for item in refusal_codes if str(item).strip()))),
        "applied_steps": list(applied_steps),
        "decision_log_rows": [
            _with_fingerprint(dict(row))
            for row in sorted(
                (dict(row) for row in decision_log_rows if isinstance(row, Mapping)),
                key=lambda item: (
                    int(_as_int(item.get("step_index", 0), 0)),
                    str(item.get("decision_id", "")),
                ),
            )
        ],
        "deterministic_fingerprint": "",
    }
    seed = dict(payload)
    seed["decision_log_rows"] = [dict(row) for row in list(payload.get("decision_log_rows") or [])]
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


__all__ = [
    "REFUSAL_SIG_NONESSENTIAL_SEND",
    "apply_sig_budget_degradation",
]
