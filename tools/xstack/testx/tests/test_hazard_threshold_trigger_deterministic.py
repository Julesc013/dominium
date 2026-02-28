"""FAST test: core hazard threshold triggering is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.hazard_threshold_trigger_deterministic"
TEST_TAGS = ["fast", "core", "hazard", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.hazards.hazard_engine import tick_hazard_models
    from tools.xstack.compatx.canonical_json import canonical_sha256

    hazards = [
        {
            "schema_version": "1.0.0",
            "hazard_id": "hazard.test.alpha",
            "hazard_type_id": "hazard.wear.general",
            "target_id": "asset.alpha",
            "accumulation": 90,
            "threshold": 100,
            "consequence_process_id": "process.asset_failure_mark_failed",
            "active": True,
            "extensions": {"threshold_crossed": False, "allow_retrigger": False},
        }
    ]
    deltas = {"hazard.test.alpha": 15}

    first = tick_hazard_models(hazard_rows=hazards, current_tick=120, delta_by_hazard_id=deltas)
    second = tick_hazard_models(hazard_rows=hazards, current_tick=120, delta_by_hazard_id=deltas)
    if first != second:
        return {"status": "fail", "message": "hazard threshold tick output is non-deterministic"}

    consequence_rows = [dict(row) for row in list(first.get("consequence_events") or []) if isinstance(row, dict)]
    if len(consequence_rows) != 1:
        return {"status": "fail", "message": "hazard threshold crossing should emit exactly one consequence event"}

    event_row = dict(consequence_rows[0])
    if str(event_row.get("hazard_id", "")) != "hazard.test.alpha":
        return {"status": "fail", "message": "hazard consequence event hazard_id mismatch"}
    if str(event_row.get("consequence_process_id", "")) != "process.asset_failure_mark_failed":
        return {"status": "fail", "message": "hazard consequence process mismatch"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "hazard threshold deterministic hash diverged"}

    return {"status": "pass", "message": "Hazard threshold deterministic behavior passed"}

