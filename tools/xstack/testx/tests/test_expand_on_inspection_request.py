"""FAST test: SYS-2 inspection requests trigger forced-expand pathway."""

from __future__ import annotations

import sys


TEST_ID = "test_expand_on_inspection_request"
TEST_TAGS = ["fast", "system", "sys2", "control"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys2_testlib import (
        base_state,
        execute_macro_tick,
        policy_context_for_macro,
    )

    state = base_state()
    result = execute_macro_tick(
        state=state,
        repo_root=repo_root,
        inputs={
            "inspection_capsule_ids": ["capsule.system.engine.alpha"],
            "max_forced_expand_approvals_per_tick": 1,
        },
        policy_context=policy_context_for_macro(repo_root=repo_root),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "macro tick execution failed for inspection request scenario"}
    forced_rows = [dict(row) for row in list(state.get("system_forced_expand_event_rows") or []) if isinstance(row, dict)]
    if not forced_rows:
        return {"status": "fail", "message": "inspection request did not trigger forced expand event"}
    if "inspection_request" not in set(str(row.get("reason_code", "")).strip() for row in forced_rows):
        return {"status": "fail", "message": "forced expand reason did not include inspection_request"}
    metadata = dict(result.get("metadata") or result)
    approved = set(str(item).strip() for item in list(metadata.get("approved_forced_expand_ids") or []) if str(item).strip())
    if not approved:
        return {"status": "fail", "message": "no approved forced expand ids were reported"}
    return {"status": "pass", "message": "inspection-triggered forced expand path is deterministic and logged"}
