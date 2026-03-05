"""FAST test: COMPILE-0 runtime hook enforces validity domain bounds."""

from __future__ import annotations

import sys


TEST_ID = "test_validity_domain_checked"
TEST_TAGS = ["fast", "meta", "compile0", "validity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.compile import compiled_model_is_valid
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
        compile_request=compile_request_fixture(request_id="compile_request.test.validity"),
        inputs={"compile_policy_id": "compile.default"},
        policy_ctx=policy_context(repo_root),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compile process did not complete"}
    model_rows = list(state.get("compiled_model_rows") or [])
    if not model_rows:
        return {"status": "fail", "message": "missing compiled_model_rows after compile"}
    model_id = str(dict(model_rows[0]).get("compiled_model_id", "")).strip()
    valid_eval = compiled_model_is_valid(
        compiled_model_id=model_id,
        current_inputs={"x": 50, "y": 50},
        compiled_model_rows=state.get("compiled_model_rows") or [],
        validity_domain_rows=state.get("validity_domain_rows") or [],
    )
    if not bool(valid_eval.get("valid", False)):
        return {"status": "fail", "message": "in-range runtime inputs rejected by validity check"}
    invalid_eval = compiled_model_is_valid(
        compiled_model_id=model_id,
        current_inputs={"x": 101, "y": 50},
        compiled_model_rows=state.get("compiled_model_rows") or [],
        validity_domain_rows=state.get("validity_domain_rows") or [],
    )
    if bool(invalid_eval.get("valid", True)):
        return {"status": "fail", "message": "out-of-range runtime input accepted by validity check"}
    return {"status": "pass", "message": "validity domain checks enforced"}
