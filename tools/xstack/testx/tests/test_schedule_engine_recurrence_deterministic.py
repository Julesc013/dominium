"""FAST test: core schedule recurrence computation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.schedule_engine_recurrence_deterministic"
TEST_TAGS = ["fast", "core", "schedule", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.schedule.schedule_engine import advance_schedule
    from tools.xstack.compatx.canonical_json import canonical_sha256

    schedule = {
        "schema_version": "1.0.0",
        "schedule_id": "schedule.test.interval",
        "target_id": "target.test",
        "temporal_domain_id": "time.canonical_tick",
        "start_tick": 0,
        "recurrence_rule": {
            "rule_type": "interval",
            "interval_ticks": 3,
            "extensions": {},
        },
        "next_due_tick": 0,
        "cancellation_policy": "keep",
        "extensions": {},
    }

    first = advance_schedule(schedule, current_tick=10)
    second = advance_schedule(schedule, current_tick=10)
    if first != second:
        return {"status": "fail", "message": "advance_schedule returned non-deterministic output"}
    if not bool(first.get("due", False)):
        return {"status": "fail", "message": "schedule should be due at tick 10 for 3-tick interval from tick 0"}
    next_due_tick = int((dict(first.get("schedule") or {})).get("next_due_tick", -1))
    if next_due_tick != 12:
        return {"status": "fail", "message": "schedule next_due_tick mismatch for deterministic recurrence stepping"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "schedule recurrence hash diverged across runs"}

    return {"status": "pass", "message": "Schedule recurrence deterministic behavior passed"}
