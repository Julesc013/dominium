"""FAST test: SYS-6 logs canonical failure events when failure thresholds are exceeded."""

from __future__ import annotations

import sys


TEST_ID = "test_failure_event_logged"
TEST_TAGS = ["fast", "system", "sys6", "reliability", "failure"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys6_testlib import (
        base_state,
        execute_health_tick,
        execute_reliability_tick,
    )

    state = base_state(
        hazard_levels={
            "hazard.thermal.overheat": 980,
            "hazard.control.loss": 980,
        }
    )
    health_result = execute_health_tick(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}

    reliability_result = execute_reliability_tick(repo_root=repo_root, state=state)
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick failed"}

    failure_rows = [dict(row) for row in list(state.get("system_failure_event_rows") or []) if isinstance(row, dict)]
    if not failure_rows:
        return {"status": "fail", "message": "failure events missing at threshold exceedance"}
    if not str(state.get("system_failure_event_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_failure_event_hash_chain missing"}

    info_rows = [dict(row) for row in list(state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    if not any(str(dict(row.get("extensions") or {}).get("artifact_type_id", "")).strip() == "artifact.record.system_failure" for row in info_rows):
        return {"status": "fail", "message": "failure RECORD artifact not emitted"}
    return {"status": "pass", "message": "SYS-6 failure events are canonical and logged"}

