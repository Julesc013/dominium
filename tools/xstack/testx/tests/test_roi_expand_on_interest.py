"""FAST test: SYS-3 ROI interest expands macro systems deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_roi_expand_on_interest"
TEST_TAGS = ["fast", "system", "sys3", "roi"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys3_testlib import (
        base_state_two_systems,
        execute_system_roi_tick,
    )

    state = base_state_two_systems()
    result = execute_system_roi_tick(
        repo_root=repo_root,
        state=state,
        inputs={
            "roi_system_ids": ["system.engine.beta"],
            "max_expands_per_tick": 8,
            "max_collapses_per_tick": 8,
        },
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "system ROI tick did not complete for ROI expand scenario"}

    system_rows = {
        str(row.get("system_id", "")).strip(): dict(row)
        for row in list(state.get("system_rows") or [])
        if isinstance(row, dict) and str(row.get("system_id", "")).strip()
    }
    beta_row = dict(system_rows.get("system.engine.beta") or {})
    if str(beta_row.get("current_tier", "")).strip() != "micro":
        return {"status": "fail", "message": "ROI-marked macro system was not expanded to micro tier"}

    tier_rows = [
        dict(row)
        for row in list(state.get("system_tier_change_event_rows") or [])
        if isinstance(row, dict)
        and str(row.get("system_id", "")).strip() == "system.engine.beta"
        and str(row.get("transition_kind", "")).strip() == "expand"
    ]
    if not tier_rows:
        return {"status": "fail", "message": "missing tier-change event row for ROI-driven expand"}
    if not any(str(row.get("result", "")).strip() == "complete" for row in tier_rows):
        return {"status": "fail", "message": "ROI-driven expand was not logged as complete"}
    return {"status": "pass", "message": "ROI interest expansion path is deterministic and logged"}

