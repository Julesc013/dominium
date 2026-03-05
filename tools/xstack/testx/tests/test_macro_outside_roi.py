"""FAST test: SYS-3 systems outside ROI collapse to macro deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_macro_outside_roi"
TEST_TAGS = ["fast", "system", "sys3", "roi"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys3_testlib import (
        execute_system_roi_tick,
        micro_only_state,
    )

    state = micro_only_state()
    result = execute_system_roi_tick(
        repo_root=repo_root,
        state=state,
        inputs={
            "roi_system_ids": [],
            "max_expands_per_tick": 4,
            "max_collapses_per_tick": 4,
        },
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "system ROI tick did not complete for outside-ROI collapse scenario"}

    system_rows = [
        dict(row)
        for row in list(state.get("system_rows") or [])
        if isinstance(row, dict) and str(row.get("system_id", "")).strip() == "system.engine.alpha"
    ]
    if not system_rows:
        return {"status": "fail", "message": "fixture lost target system row after ROI tick"}
    alpha_row = dict(system_rows[0])
    if str(alpha_row.get("current_tier", "")).strip() != "macro":
        return {"status": "fail", "message": "outside-ROI system was not collapsed to macro"}
    if not str(alpha_row.get("active_capsule_id", "")).strip():
        return {"status": "fail", "message": "collapsed system missing active capsule reference"}

    tier_rows = [
        dict(row)
        for row in list(state.get("system_tier_change_event_rows") or [])
        if isinstance(row, dict)
        and str(row.get("system_id", "")).strip() == "system.engine.alpha"
        and str(row.get("transition_kind", "")).strip() == "collapse"
    ]
    if not tier_rows:
        return {"status": "fail", "message": "missing tier-change collapse event row"}
    return {"status": "pass", "message": "outside-ROI collapse path is deterministic and logged"}

