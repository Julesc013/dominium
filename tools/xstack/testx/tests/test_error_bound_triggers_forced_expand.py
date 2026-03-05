"""FAST test: SYS-2 error-bound overflow triggers forced-expand canonical events."""

from __future__ import annotations

import sys


TEST_ID = "test_error_bound_triggers_forced_expand"
TEST_TAGS = ["fast", "system", "sys2", "forced-expand"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys2_testlib import (
        base_state,
        execute_macro_tick,
        macro_model_set_error_registry,
        policy_context_for_macro,
    )

    state = base_state(macro_model_set_id="macro.set.sys2.error", max_error_estimate=1)
    result = execute_macro_tick(
        state=state,
        repo_root=repo_root,
        inputs={},
        policy_context=policy_context_for_macro(
            repo_root=repo_root,
            macro_model_set_registry=macro_model_set_error_registry(),
        ),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "macro tick execution failed for error-bound scenario"}
    forced_rows = [
        dict(row)
        for row in list(state.get("system_forced_expand_event_rows") or [])
        if isinstance(row, dict)
    ]
    if not forced_rows:
        return {"status": "fail", "message": "forced expand event was not emitted"}
    reasons = set(str(row.get("reason_code", "")).strip() for row in forced_rows)
    if "error_bound_exceeded" not in reasons:
        return {
            "status": "fail",
            "message": "forced expand did not report error_bound_exceeded reason",
        }
    return {"status": "pass", "message": "error bound overflow deterministically triggers forced-expand event"}

