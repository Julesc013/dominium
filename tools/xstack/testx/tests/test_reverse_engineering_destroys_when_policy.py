"""FAST test: PROC-7 reverse engineering destruction follows policy."""

from __future__ import annotations

import sys


TEST_ID = "test_reverse_engineering_destroys_when_policy"
TEST_TAGS = ["fast", "proc", "proc7", "reverse_engineering", "policy"]


def _last_reverse_record(state: dict) -> dict:
    rows = [
        dict(row)
        for row in list(state.get("reverse_engineering_record_rows") or [])
        if isinstance(row, dict)
    ]
    return rows[-1] if rows else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc7_testlib import (
        cloned_state,
        disallow_destructive_policy_context,
        execute_process,
        run_reverse_action,
    )

    allow_state = cloned_state(repo_root)
    allow_result = run_reverse_action(
        repo_root=repo_root,
        state=allow_state,
        target_item_id="item.proc7.destroy.allowed",
        method="disassemble",
        research_policy_id="research.default",
    )
    if str(allow_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "allowed-policy reverse engineering did not complete"}
    if "item.proc7.destroy.allowed" not in list(allow_state.get("destroyed_item_ids") or []):
        return {"status": "fail", "message": "allowed policy should destroy disassembled target"}
    if not bool(_last_reverse_record(allow_state).get("destroyed", False)):
        return {"status": "fail", "message": "reverse record should mark destroyed=true under allowed policy"}

    deny_state = cloned_state(repo_root)
    deny_result = execute_process(
        repo_root=repo_root,
        state=deny_state,
        process_id="process.reverse_engineering_action",
        inputs={
            "target_item_id": "item.proc7.destroy.blocked",
            "method": "disassemble",
            "subject_id": "subject.proc7.researcher",
            "research_policy_id": "research.no_destroy",
            "destroyed": True,
        },
        policy_context=disallow_destructive_policy_context(),
    )
    if str(deny_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "policy-context reverse engineering did not complete"}
    if "item.proc7.destroy.blocked" in list(deny_state.get("destroyed_item_ids") or []):
        return {"status": "fail", "message": "blocked policy should prevent target destruction"}
    if bool(_last_reverse_record(deny_state).get("destroyed", True)):
        return {"status": "fail", "message": "reverse record should mark destroyed=false when policy blocks destruction"}

    return {"status": "pass", "message": "PROC-7 reverse engineering destruction follows policy"}

