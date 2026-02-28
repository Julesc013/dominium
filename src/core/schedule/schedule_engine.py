"""Deterministic core ScheduleComponent helpers."""

from __future__ import annotations

from typing import Mapping


REFUSAL_CORE_SCHEDULE_INVALID = "refusal.core.schedule.invalid"


class ScheduleError(ValueError):
    """Deterministic schedule refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _normalize_recurrence_rule(row: object) -> dict:
    payload = dict(row or {}) if isinstance(row, dict) else {}
    rule_type = str(payload.get("rule_type", "")).strip() or "none"
    interval_ticks = int(max(0, _as_int(payload.get("interval_ticks", 0), 0)))
    if rule_type not in ("none", "interval"):
        rule_type = "none"
    return {
        "rule_type": rule_type,
        "interval_ticks": interval_ticks,
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_schedule(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    schedule_id = str(payload.get("schedule_id", "")).strip()
    target_id = str(payload.get("target_id", "")).strip()
    cancellation_policy = str(payload.get("cancellation_policy", "")).strip() or "keep"
    if not schedule_id or not target_id:
        raise ScheduleError(
            REFUSAL_CORE_SCHEDULE_INVALID,
            "schedule missing required schedule_id/target_id",
            {"schedule_id": schedule_id, "target_id": target_id},
        )
    start_tick = int(max(0, _as_int(payload.get("start_tick", 0), 0)))
    recurrence_rule = _normalize_recurrence_rule(payload.get("recurrence_rule"))
    next_due_tick = payload.get("next_due_tick")
    if next_due_tick is None:
        normalized_next_due_tick = int(start_tick)
    else:
        normalized_next_due_tick = int(max(0, _as_int(next_due_tick, 0)))
    return {
        "schema_version": "1.0.0",
        "schedule_id": schedule_id,
        "target_id": target_id,
        "start_tick": start_tick,
        "recurrence_rule": recurrence_rule,
        "next_due_tick": normalized_next_due_tick,
        "cancellation_policy": cancellation_policy,
        "extensions": dict(payload.get("extensions") or {}),
    }


def advance_schedule(schedule_row: Mapping[str, object], *, current_tick: int) -> dict:
    row = normalize_schedule(schedule_row)
    now = int(max(0, _as_int(current_tick, 0)))
    due = now >= int(row.get("next_due_tick", 0))
    recurrence_rule = dict(row.get("recurrence_rule") or {})
    if due and str(recurrence_rule.get("rule_type", "none")) == "interval":
        interval = int(max(1, _as_int(recurrence_rule.get("interval_ticks", 1), 1)))
        next_due = int(row.get("next_due_tick", 0))
        while next_due <= now:
            next_due += interval
        row["next_due_tick"] = int(next_due)
    elif due and str(recurrence_rule.get("rule_type", "none")) == "none":
        row["next_due_tick"] = int(now)
    return {"schedule": row, "due": bool(due)}

