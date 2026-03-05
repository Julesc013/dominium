"""FAST test: SYS-6 applies safe fallback when forced expand is denied."""

from __future__ import annotations

import sys


TEST_ID = "test_safe_fallback_on_denied_expand"
TEST_TAGS = ["fast", "system", "sys6", "reliability", "fallback"]


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
            "hazard.thermal.overheat": 790,
            "hazard.control.loss": 830,
        }
    )
    system_id = str((state.get("system_rows") or [])[0].get("system_id", "")).strip()

    health_result = execute_health_tick(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}

    reliability_result = execute_reliability_tick(
        repo_root=repo_root,
        state=state,
        inputs={"denied_expand_system_ids": [system_id]},
    )
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick failed"}

    fallback_rows = [
        dict(row)
        for row in list(state.get("system_reliability_safe_fallback_rows") or [])
        if isinstance(row, dict)
    ]
    if not fallback_rows:
        return {"status": "fail", "message": "safe fallback rows missing when forced expand denied"}

    decision_rows = [dict(row) for row in list(state.get("control_decision_log") or []) if isinstance(row, dict)]
    if not any(str(row.get("reason_code", "")).strip() == "refusal.system.reliability.expand_denied" for row in decision_rows):
        return {"status": "fail", "message": "expand denial was not logged in control_decision_log"}
    return {"status": "pass", "message": "SYS-6 safe fallback on denied expand is deterministic and logged"}

