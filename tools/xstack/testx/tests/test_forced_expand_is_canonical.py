"""FAST test: SYS-2 forced expand emits canonical RECORD artifacts."""

from __future__ import annotations

import sys


TEST_ID = "test_forced_expand_is_canonical"
TEST_TAGS = ["fast", "system", "sys2", "provenance"]


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
        return {"status": "fail", "message": "macro tick execution failed for canonicality check"}
    forced_rows = [dict(row) for row in list(state.get("system_forced_expand_event_rows") or []) if isinstance(row, dict)]
    if not forced_rows:
        return {"status": "fail", "message": "no forced expand events were persisted"}
    artifact_rows = [dict(row) for row in list(state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    forced_artifacts = [
        row
        for row in artifact_rows
        if str(row.get("artifact_family_id", "")).strip() == "RECORD"
        and str(dict(row.get("extensions") or {}).get("artifact_type_id", "")).strip()
        == "artifact.record.system_forced_expand"
    ]
    if not forced_artifacts:
        return {"status": "fail", "message": "forced expand canonical RECORD artifact missing"}
    if not str(state.get("system_forced_expand_event_hash_chain", "")).strip():
        return {"status": "fail", "message": "forced expand hash chain was not updated"}
    return {"status": "pass", "message": "forced expand events are canonical and artifact-backed"}

