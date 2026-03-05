"""FAST test: COMPILE-0 recompile from source snapshot matches stored compiled hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_recompile_matches_hash"
TEST_TAGS = ["fast", "meta", "compile0", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.meta.tool_verify_compiled_model import verify_compiled_model
    from tools.xstack.testx.tests.compile0_testlib import (
        cloned_state,
        compile_request_fixture,
        execute_compile_request,
        policy_context,
    )

    state = cloned_state()
    result = execute_compile_request(
        repo_root=repo_root,
        state=state,
        compile_request=compile_request_fixture(request_id="compile_request.test.recompile"),
        inputs={"compile_policy_id": "compile.default"},
        policy_ctx=policy_context(repo_root),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compile process did not complete"}

    model_rows = list(state.get("compiled_model_rows") or [])
    if not model_rows:
        return {"status": "fail", "message": "missing compiled_model_rows after compile"}
    model_id = str(dict(model_rows[0]).get("compiled_model_id", "")).strip()
    if not model_id:
        return {"status": "fail", "message": "compiled_model_id missing after compile"}

    verify = verify_compiled_model(
        repo_root=repo_root,
        state_payload=state,
        compiled_model_id=model_id,
    )
    if str(verify.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "recompile verification failed: {}".format(
                str(verify.get("reason_code", "unknown")).strip()
            ),
        }
    if not bool(verify.get("payload_match", False)):
        return {"status": "fail", "message": "recompiled payload hash did not match stored payload hash"}
    if not bool(verify.get("proof_match", False)):
        return {"status": "fail", "message": "recompiled proof metadata did not match stored proof metadata"}
    return {"status": "pass", "message": "recompile verification matches stored hashes"}

