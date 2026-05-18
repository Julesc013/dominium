"""Deterministic core ScheduleComponent helpers."""

from __future__ import annotations

from typing import Callable, Dict, List, Mapping

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


def _normalize_temporal_domain_id(value: object) -> str:
    token = str(value or "").strip()
    return token or "time.canonical_tick"


def _domain_value_as_int(value: object, default_value: int = 0) -> int:
    if isinstance(value, Mapping):
        payload = dict(value)
        for key in ("value", "ticks", "time_value", "domain_time_value"):
            if key in payload:
                return int(max(0, _as_int(payload.get(key, default_value), default_value)))
    return int(max(0, _as_int(value, default_value)))


def normalize_schedule(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    schedule_id = str(payload.get("schedule_id", "")).strip()
    target_id = str(payload.get("target_id", "")).strip()
    temporal_domain_id = _normalize_temporal_domain_id(payload.get("temporal_domain_id"))
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
        "temporal_domain_id": temporal_domain_id,
        "start_tick": start_tick,
        "recurrence_rule": recurrence_rule,
        "next_due_tick": normalized_next_due_tick,
        "cancellation_policy": cancellation_policy,
        "active": bool(active),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_schedule_time_binding(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    schedule_id = str(payload.get("schedule_id", "")).strip()
    if not schedule_id:
        raise ScheduleError(
            REFUSAL_CORE_SCHEDULE_INVALID,
            "schedule_time_binding missing schedule_id",
            {"schedule_id": schedule_id},
        )
    temporal_domain_id = _normalize_temporal_domain_id(payload.get("temporal_domain_id"))
    target_time_value = _domain_value_as_int(payload.get("target_time_value", 0), 0)
    evaluation_policy_id = str(payload.get("evaluation_policy_id", "")).strip() or "schedule.eval.gte_target"
    out = {
        "schema_version": "1.0.0",
        "schedule_id": schedule_id,
        "temporal_domain_id": temporal_domain_id,
        "target_time_value": int(target_time_value),
        "evaluation_policy_id": evaluation_policy_id,
        "deterministic_fingerprint": "",
        "extensions": dict(payload.get("extensions") or {}),
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def normalize_schedule_time_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("schedule_id", ""))):
        try:
            normalized = normalize_schedule_time_binding(row)
        except ScheduleError:
            continue
        out[str(normalized.get("schedule_id", "")).strip()] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


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
    schedule_time_binding_rows: object = None,
    resolve_domain_time_fn: Callable[[str, str, int], object] | None = None,
) -> dict:
    """Advance schedules deterministically and emit due events."""

    rows: List[dict] = []
    for row in list(schedule_rows or []):
        if not isinstance(row, dict):
            continue
        rows.append(normalize_schedule(row))
    rows = sorted(rows, key=lambda row: str(row.get("schedule_id", "")))

    binding_rows = normalize_schedule_time_binding_rows(schedule_time_binding_rows)
    binding_by_schedule_id = dict(
        (str(row.get("schedule_id", "")).strip(), dict(row))
        for row in binding_rows
        if str(row.get("schedule_id", "")).strip()
    )

    limit = len(rows)
    if max_schedules is not None:
        limit = min(limit, max(0, _as_int(max_schedules, len(rows))))

    processed = rows[:limit]
    deferred = rows[limit:]

    tick = int(max(0, _as_int(current_tick, 0)))
    due_events: List[dict] = []
    updated: List[dict] = []
    domain_evaluations: List[dict] = []

    for row in processed:
        schedule_id = str(row.get("schedule_id", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        temporal_domain_id = _normalize_temporal_domain_id(row.get("temporal_domain_id"))
        binding = dict(binding_by_schedule_id.get(schedule_id) or {})

        if temporal_domain_id == "time.canonical_tick":
            advanced = advance_schedule(row, current_tick=tick)
            updated_row = dict(advanced.get("schedule") or row)
            updated.append(updated_row)
            recurrence_rule = dict(updated_row.get("recurrence_rule") or {})
            domain_eval = {
                "schedule_id": schedule_id,
                "target_id": target_id,
                "temporal_domain_id": temporal_domain_id,
                "tick": int(tick),
                "domain_time_value": int(tick),
                "target_time_value": int(max(0, _as_int(updated_row.get("next_due_tick", tick), tick))),
                "due": bool(advanced.get("due", False)),
                "evaluation_policy_id": "schedule.eval.gte_target",
                "deterministic_fingerprint": "",
            }
            domain_eval["deterministic_fingerprint"] = canonical_sha256(dict(domain_eval, deterministic_fingerprint=""))
            domain_evaluations.append(domain_eval)
            if not bool(advanced.get("due", False)):
                continue
            event = {
                "schedule_id": schedule_id,
                "target_id": target_id,
                "temporal_domain_id": temporal_domain_id,
                "due_tick": int(max(0, _as_int(advanced.get("due_tick", 0), 0))),
                "next_due_tick": int(max(0, _as_int(updated_row.get("next_due_tick", 0), 0))),
                "trigger_process_id": str(recurrence_rule.get("trigger_process_id", "")),
                "tick": int(tick),
                "domain_time_value": int(tick),
                "target_time_value": int(max(0, _as_int(advanced.get("due_tick", tick), tick))),
                "evaluation_policy_id": "schedule.eval.gte_target",
                "deterministic_fingerprint": "",
            }
            event["deterministic_fingerprint"] = canonical_sha256(dict(event, deterministic_fingerprint=""))
            due_events.append(event)
            continue

        eval_policy = str(binding.get("evaluation_policy_id", "")).strip() or "schedule.eval.gte_target"
        if not binding:
            binding = normalize_schedule_time_binding(
                {
                    "schedule_id": schedule_id,
                    "temporal_domain_id": temporal_domain_id,
                    "target_time_value": int(max(0, _as_int(row.get("next_due_tick", row.get("start_tick", 0)), 0))),
                    "evaluation_policy_id": eval_policy,
                    "extensions": {"derived_from_schedule": True},
                }
            )
        domain_value = _domain_value_as_int(
            resolve_domain_time_fn(temporal_domain_id, target_id, tick) if callable(resolve_domain_time_fn) else None,
            default_value=-1,
        )
        target_value = int(max(0, _as_int(binding.get("target_time_value", 0), 0)))
        due = bool(row.get("active", True)) and (domain_value >= target_value) and (domain_value >= 0)
        recurrence_rule = dict(row.get("recurrence_rule") or {})

        updated_row = dict(row)
        if due and str(recurrence_rule.get("rule_type", "none")) == "interval":
            interval = int(max(1, _as_int(recurrence_rule.get("interval_ticks", 1), 1)))
            next_target = int(target_value)
            while next_target <= domain_value:
                next_target += interval
            binding["target_time_value"] = int(next_target)
            updated_row["next_due_tick"] = int(tick)
        elif due and str(recurrence_rule.get("rule_type", "none")) == "none":
            binding["target_time_value"] = int(target_value)
            updated_row["next_due_tick"] = int(tick)

        binding["temporal_domain_id"] = temporal_domain_id
        binding["evaluation_policy_id"] = eval_policy
        binding["deterministic_fingerprint"] = canonical_sha256(dict(binding, deterministic_fingerprint=""))
        binding_by_schedule_id[schedule_id] = dict(binding)
        updated.append(updated_row)

        domain_eval = {
            "schedule_id": schedule_id,
            "target_id": target_id,
            "temporal_domain_id": temporal_domain_id,
            "tick": int(tick),
            "domain_time_value": int(domain_value),
            "target_time_value": int(target_value),
            "due": bool(due),
            "evaluation_policy_id": eval_policy,
            "deterministic_fingerprint": "",
        }
        domain_eval["deterministic_fingerprint"] = canonical_sha256(dict(domain_eval, deterministic_fingerprint=""))
        domain_evaluations.append(domain_eval)

        if not due:
            continue
        event = {
            "schedule_id": schedule_id,
            "target_id": target_id,
            "temporal_domain_id": temporal_domain_id,
            "due_tick": int(target_value),
            "next_due_tick": int(max(0, _as_int(updated_row.get("next_due_tick", tick), tick))),
            "trigger_process_id": str(recurrence_rule.get("trigger_process_id", "")),
            "tick": int(tick),
            "domain_time_value": int(domain_value),
            "target_time_value": int(target_value),
            "evaluation_policy_id": eval_policy,
            "deterministic_fingerprint": "",
        }
        event["deterministic_fingerprint"] = canonical_sha256(dict(event, deterministic_fingerprint=""))
        due_events.append(event)

    updated.extend(dict(row) for row in deferred)
    updated = sorted(updated, key=lambda row: str(row.get("schedule_id", "")))

    deferred_ids = [str(row.get("schedule_id", "")) for row in deferred]
    due_events_sorted = sorted(
        due_events,
        key=lambda row: (
            int(_as_int(row.get("due_tick", 0), 0)),
            str(row.get("schedule_id", "")),
        ),
    )
    binding_rows_out = [dict(binding_by_schedule_id[key]) for key in sorted(binding_by_schedule_id.keys())]
    domain_evaluations = sorted(
        (dict(row) for row in domain_evaluations),
        key=lambda row: (
            int(_as_int(row.get("tick", 0), 0)),
            str(row.get("temporal_domain_id", "")),
            str(row.get("schedule_id", "")),
        ),
    )
    return {
        "schedules": updated,
        "schedule_time_bindings": binding_rows_out,
        "due_events": due_events_sorted,
        "due_schedules": list(due_events_sorted),
        "domain_evaluations": domain_evaluations,
        "schedule_domain_evaluation_hash": canonical_sha256(list(domain_evaluations)),
        "processed_count": int(len(processed)),
        "deferred_schedule_ids": deferred_ids,
        "deferred_count": int(len(deferred_ids)),
        "cost_units": int(max(0, _as_int(cost_units_per_schedule, 1))) * int(len(processed)),
        "budget_outcome": "complete" if not deferred_ids else "degraded",
    }
