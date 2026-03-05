"""FAST test: SYS-6 reliability emits forced expand requests when thresholds are exceeded."""

from __future__ import annotations

import sys


TEST_ID = "test_forced_expand_triggered"
TEST_TAGS = ["fast", "system", "sys6", "reliability", "forced_expand"]


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
            "hazard.thermal.overheat": 780,
            "hazard.control.loss": 820,
        }
    )
    health_result = execute_health_tick(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}

    reliability_result = execute_reliability_tick(
        repo_root=repo_root,
        state=state,
        inputs={"denied_expand_system_ids": []},
    )
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick failed"}

    forced_rows = [dict(row) for row in list(state.get("system_forced_expand_event_rows") or []) if isinstance(row, dict)]
    if not forced_rows:
        return {"status": "fail", "message": "forced expand event rows missing despite threshold exceedance"}
    if not str(state.get("system_forced_expand_event_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_forced_expand_event_hash_chain missing"}
    return {"status": "pass", "message": "SYS-6 forced expand request pathway is active"}

