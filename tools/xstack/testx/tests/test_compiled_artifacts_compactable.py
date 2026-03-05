"""FAST test: COMPILE-0 derived compile artifacts compact deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_compiled_artifacts_compactable"
TEST_TAGS = ["fast", "meta", "compile0", "compaction"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.provenance import compact_provenance_window
    from tools.xstack.testx.tests.compile0_testlib import (
        cloned_state,
        compile_request_fixture,
        execute_compile_request,
        policy_context,
    )
    from tools.xstack.testx.tests.provenance_compaction_testlib import (
        read_provenance_classification_rows,
    )

    state = cloned_state()
    compile_result = execute_compile_request(
        repo_root=repo_root,
        state=state,
        compile_request=compile_request_fixture(request_id="compile_request.test.compaction"),
        inputs={"compile_policy_id": "compile.default"},
        policy_ctx=policy_context(repo_root),
    )
    if str(compile_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compile process did not complete"}

    expected_compactable_keys = (
        "compiled_model_rows",
        "equivalence_proof_rows",
        "validity_domain_rows",
        "compile_result_rows",
    )
    for key in expected_compactable_keys:
        if not list(state.get(key) or []):
            return {"status": "fail", "message": "missing {} before compaction".format(key)}

    compaction = compact_provenance_window(
        state_payload=state,
        classification_rows=read_provenance_classification_rows(repo_root),
        shard_id="shard.compile0",
        start_tick=0,
        end_tick=0,
    )
    if str(compaction.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compaction run failed for compile artifacts"}

    out_state = dict(compaction.get("state") or {})
    for key in expected_compactable_keys:
        if list(out_state.get(key) or []):
            return {"status": "fail", "message": "{} were not compacted from the selected window".format(key)}

    removed_by_key = dict(compaction.get("removed_by_key") or {})
    missing_removed_markers = [key for key in expected_compactable_keys if int(removed_by_key.get(key, 0) or 0) <= 0]
    if missing_removed_markers:
        return {
            "status": "fail",
            "message": "compaction did not report removed rows for keys: {}".format(
                ", ".join(sorted(missing_removed_markers))
            ),
        }
    return {"status": "pass", "message": "compile artifacts compacted deterministically"}

