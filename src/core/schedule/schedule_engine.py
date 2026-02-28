"""Deterministic core ScheduleComponent helpers."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


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
    trigger_process_id = str(payload.get("trigger_process_id", "")).strip()
    return {
        "rule_type": rule_type,
        "interval_ticks": interval_ticks,
        "trigger_process_id": trigger_process_id,
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
    active_value = payload.get("active")
    active = True if active_value is None else bool(active_value)
    return {
        "schema_version": "1.0.0",
        "schedule_id": schedule_id,
        "target_id": target_id,
        "start_tick": start_tick,
        "recurrence_rule": recurrence_rule,
        "next_due_tick": normalized_next_due_tick,
        "cancellation_policy": cancellation_policy,
        "active": bool(active),
        "extensions": dict(payload.get("extensions") or {}),
    }


def advance_schedule(schedule_row: Mapping[str, object], *, current_tick: int) -> dict:
    row = normalize_schedule(schedule_row)
    now = int(max(0, _as_int(current_tick, 0)))
    due_tick = int(row.get("next_due_tick", 0))
    due = bool(row.get("active", True)) and (now >= due_tick)
    recurrence_rule = dict(row.get("recurrence_rule") or {})
    if due and str(recurrence_rule.get("rule_type", "none")) == "interval":
        interval = int(max(1, _as_int(recurrence_rule.get("interval_ticks", 1), 1)))
        next_due = int(due_tick)
        while next_due <= now:
            next_due += interval
        row["next_due_tick"] = int(next_due)
    elif due and str(recurrence_rule.get("rule_type", "none")) == "none":
        row["next_due_tick"] = int(now)
    return {"schedule": row, "due": bool(due), "due_tick": int(due_tick)}


def tick_schedules(
    *,
    schedule_rows: object,
    current_tick: int,
    max_schedules: int | None = None,
    cost_units_per_schedule: int = 1,
) -> dict:
    """Advance schedules deterministically and emit due events."""

    rows: List[dict] = []
    for row in list(schedule_rows or []):
        if not isinstance(row, dict):
            continue
        rows.append(normalize_schedule(row))
    rows = sorted(rows, key=lambda row: str(row.get("schedule_id", "")))

    limit = len(rows)
    if max_schedules is not None:
        limit = min(limit, max(0, _as_int(max_schedules, len(rows))))

    processed = rows[:limit]
    deferred = rows[limit:]

    tick = int(max(0, _as_int(current_tick, 0)))
    due_events: List[dict] = []
    updated: List[dict] = []

    for row in processed:
        advanced = advance_schedule(row, current_tick=tick)
        updated_row = dict(advanced.get("schedule") or row)
        updated.append(updated_row)
        if not bool(advanced.get("due", False)):
            continue
        recurrence_rule = dict(updated_row.get("recurrence_rule") or {})
        event = {
            "schedule_id": str(updated_row.get("schedule_id", "")),
            "target_id": str(updated_row.get("target_id", "")),
            "due_tick": int(max(0, _as_int(advanced.get("due_tick", 0), 0))),
            "next_due_tick": int(max(0, _as_int(updated_row.get("next_due_tick", 0), 0))),
            "trigger_process_id": str(recurrence_rule.get("trigger_process_id", "")),
            "tick": int(tick),
            "deterministic_fingerprint": "",
        }
        seed = dict(event)
        seed["deterministic_fingerprint"] = ""
        event["deterministic_fingerprint"] = canonical_sha256(seed)
        due_events.append(event)

    updated.extend(dict(row) for row in deferred)
    updated = sorted(updated, key=lambda row: str(row.get("schedule_id", "")))

    deferred_ids = [str(row.get("schedule_id", "")) for row in deferred]
    return {
        "schedules": updated,
        "due_events": sorted(
            due_events,
            key=lambda row: (
                int(_as_int(row.get("due_tick", 0), 0)),
                str(row.get("schedule_id", "")),
            ),
        ),
        "processed_count": int(len(processed)),
        "deferred_schedule_ids": deferred_ids,
        "deferred_count": int(len(deferred_ids)),
        "cost_units": int(max(0, _as_int(cost_units_per_schedule, 1))) * int(len(processed)),
        "budget_outcome": "complete" if not deferred_ids else "degraded",
    }
