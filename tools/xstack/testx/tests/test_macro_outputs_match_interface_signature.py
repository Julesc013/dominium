"""FAST test: SYS-2 macro outputs preserve interface-compatible validation outcomes."""

from __future__ import annotations

import sys


TEST_ID = "test_macro_outputs_match_interface_signature"
TEST_TAGS = ["fast", "system", "sys2", "validation"]


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
        inputs={},
        policy_context=policy_context_for_macro(repo_root=repo_root),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "macro tick execution failed"}
    metadata = dict(result.get("metadata") or result)
    validation_rows = [
        dict(row)
        for row in list(metadata.get("validation_rows") or [])
        if isinstance(row, dict)
    ]
    if not validation_rows:
        return {"status": "fail", "message": "no validation rows were returned for macro execution"}
    for row in validation_rows:
        if str(row.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "macro model/interface validation reported refusal"}
    flow_rows = [dict(row) for row in list(state.get("model_flow_adjustment_rows") or []) if isinstance(row, dict)]
    if not flow_rows:
        return {"status": "fail", "message": "macro execution did not emit any process.flow_adjust-compatible output"}
    return {"status": "pass", "message": "macro outputs validated against interface signature and produced flow output"}
