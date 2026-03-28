"""FAST test: schedules normalize and declare temporal domain bindings."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_schedule_has_domain_binding"
TEST_TAGS = ["fast", "time", "schedule", "temp0"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.schedule.schedule_engine import normalize_schedule
    from signals.aggregation.aggregation_engine import normalize_schedule_rows

    schedule_row = {
        "schedule_id": "schedule.temp0.binding.default",
        "target_id": "assembly.temp0.binding.default",
        "start_tick": 12,
        "recurrence_rule": {"rule_type": "interval", "interval_ticks": 5, "extensions": {}},
        "next_due_tick": 12,
        "cancellation_policy": "keep",
        "active": True,
        "extensions": {},
    }
    normalized = normalize_schedule(schedule_row)
    if str(normalized.get("temporal_domain_id", "")).strip() != "time.canonical_tick":
        return {"status": "fail", "message": "normalize_schedule must default temporal_domain_id to time.canonical_tick"}

    explicit_row = dict(schedule_row)
    explicit_row["temporal_domain_id"] = "time.proper"
    explicit = normalize_schedule(explicit_row)
    if str(explicit.get("temporal_domain_id", "")).strip() != "time.proper":
        return {"status": "fail", "message": "normalize_schedule must preserve explicit temporal_domain_id"}

    agg_rows = normalize_schedule_rows(
        [
            {
                "schedule_id": "schedule.temp0.aggregation.default",
                "next_due_tick": 0,
                "interval_ticks": 1,
            }
        ]
    )
    if not agg_rows:
        return {"status": "fail", "message": "aggregation schedule normalization returned no rows"}
    if str(dict(agg_rows[0]).get("temporal_domain_id", "")).strip() != "time.canonical_tick":
        return {"status": "fail", "message": "aggregation schedule rows must default temporal_domain_id"}

    schema_path = os.path.join(repo_root, "schemas", "schedule.schema.json")
    try:
        schema_payload = json.load(open(schema_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "schedule.schema.json missing or invalid"}
    required = list(schema_payload.get("required") or [])
    if "temporal_domain_id" not in required:
        return {"status": "fail", "message": "schedule.schema.json must require temporal_domain_id"}

    return {"status": "pass", "message": "schedule temporal domain binding is enforced"}
