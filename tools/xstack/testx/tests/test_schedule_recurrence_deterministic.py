"""FAST test: core schedule recurrence helper remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.schedule_recurrence_deterministic"
TEST_TAGS = ["fast", "core", "schedule", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.schedule.schedule_engine import advance_schedule
    from tools.xstack.compatx.canonical_json import canonical_sha256

    schedule = {
        "schema_version": "1.0.0",
        "schedule_id": "schedule.test.interval.alias",
        "target_id": "target.test",
        "start_tick": 0,
        "recurrence_rule": {"rule_type": "interval", "interval_ticks": 4, "extensions": {}},
        "next_due_tick": 0,
        "cancellation_policy": "keep",
        "active": True,
        "extensions": {},
    }

    first = advance_schedule(schedule, current_tick=10)
    second = advance_schedule(schedule, current_tick=10)
    if first != second:
        return {"status": "fail", "message": "schedule recurrence output is non-deterministic"}

    next_due = int((dict(first.get("schedule") or {})).get("next_due_tick", -1))
    if next_due != 12:
        return {"status": "fail", "message": "schedule recurrence next_due_tick mismatch"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "schedule recurrence deterministic hash diverged"}

    return {"status": "pass", "message": "Schedule recurrence deterministic behavior passed"}

