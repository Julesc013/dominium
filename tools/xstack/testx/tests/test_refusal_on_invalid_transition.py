"""FAST test: SYS-3 invalid expand transitions are refused and logged."""

from __future__ import annotations

import sys


TEST_ID = "test_refusal_on_invalid_transition"
TEST_TAGS = ["fast", "system", "sys3", "safety"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import REFUSAL_SYSTEM_EXPAND_INVALID_INTERFACE
    from tools.xstack.testx.tests.sys3_testlib import (
        base_state_two_systems,
        execute_system_roi_tick,
    )

    state = base_state_two_systems()
    interface_rows = [
        dict(row)
        for row in list(state.get("system_interface_signature_rows") or [])
        if isinstance(row, dict)
    ]
    for row in interface_rows:
        if str(row.get("system_id", "")).strip() != "system.engine.beta":
            continue
        row["interface_signature_id"] = "iface.system.engine.beta.changed"
    state["system_interface_signature_rows"] = interface_rows

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
        return {"status": "fail", "message": "system ROI tick failed unexpectedly for invalid-expand scenario"}

    refusal_rows = [
        dict(row)
        for row in list(state.get("system_tier_change_event_rows") or [])
        if isinstance(row, dict)
        and str(row.get("system_id", "")).strip() == "system.engine.beta"
        and str(row.get("result", "")).strip() == "denied"
    ]
    if not refusal_rows:
        return {"status": "fail", "message": "missing denied SYS-3 tier transition row for invalid expand"}
    reason_codes = set(str(row.get("reason_code", "")).strip() for row in refusal_rows)
    if str(REFUSAL_SYSTEM_EXPAND_INVALID_INTERFACE) not in reason_codes:
        return {"status": "fail", "message": "invalid expand refusal reason did not preserve interface-mismatch code"}

    explain_rows = [dict(row) for row in list(state.get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if not explain_rows:
        return {"status": "fail", "message": "invalid transition refusal did not emit explain artifact"}
    return {"status": "pass", "message": "invalid SYS-3 transition refusal is deterministic and explained"}

