"""FAST test: COMPILE-0 successful compile results always carry equivalence proof linkage."""

from __future__ import annotations

import sys


TEST_ID = "test_equivalence_proof_required"
TEST_TAGS = ["fast", "meta", "compile0", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

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
        compile_request=compile_request_fixture(request_id="compile_request.test.proof_required"),
        inputs={"compile_policy_id": "compile.default"},
        policy_ctx=policy_context(repo_root),
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compile process did not complete"}
    success = bool(result.get("success", False))
    if not success:
        return {"status": "fail", "message": "compile process did not produce a successful result for proof check fixture"}
    proof_rows = list(state.get("equivalence_proof_rows") or [])
    model_rows = list(state.get("compiled_model_rows") or [])
    if not proof_rows:
        return {"status": "fail", "message": "successful compile missing equivalence_proof_rows"}
    if not model_rows:
        return {"status": "fail", "message": "successful compile missing compiled_model_rows"}
    proof_ids = set(str(row.get("proof_id", "")).strip() for row in proof_rows if str(row.get("proof_id", "")).strip())
    model_proof_ref = str(dict(model_rows[0]).get("equivalence_proof_ref", "")).strip()
    if (not model_proof_ref) or model_proof_ref not in proof_ids:
        return {"status": "fail", "message": "compiled model row missing valid equivalence_proof_ref linkage"}
    return {"status": "pass", "message": "equivalence proof linkage required and present"}
