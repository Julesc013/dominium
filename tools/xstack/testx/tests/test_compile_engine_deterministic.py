"""FAST test: COMPILE-0 evaluate_compile_request is deterministic for equal inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_compile_engine_deterministic"
TEST_TAGS = ["fast", "meta", "compile0", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.compile import evaluate_compile_request
    from tools.xstack.testx.tests.compile0_testlib import compile_request_fixture, policy_context

    request = compile_request_fixture(request_id="compile_request.test.deterministic")
    policies = policy_context(repo_root)
    eval_a = evaluate_compile_request(
        current_tick=42,
        compile_request=request,
        compiled_type_registry_payload=policies.get("compiled_type_registry"),
        verification_procedure_registry_payload=policies.get("verification_procedure_registry"),
        compile_policy_registry_payload=policies.get("compile_policy_registry"),
        compile_policy_id="compile.default",
    )
    eval_b = evaluate_compile_request(
        current_tick=42,
        compile_request=request,
        compiled_type_registry_payload=policies.get("compiled_type_registry"),
        verification_procedure_registry_payload=policies.get("verification_procedure_registry"),
        compile_policy_registry_payload=policies.get("compile_policy_registry"),
        compile_policy_id="compile.default",
    )
    if str(eval_a.get("deterministic_fingerprint", "")).strip() != str(
        eval_b.get("deterministic_fingerprint", "")
    ).strip():
        return {"status": "fail", "message": "evaluate_compile_request fingerprint differs across equal runs"}
    if str(dict(eval_a.get("compiled_model_row") or {}).get("compiled_model_id", "")).strip() != str(
        dict(eval_b.get("compiled_model_row") or {}).get("compiled_model_id", "")
    ).strip():
        return {"status": "fail", "message": "compiled_model_id differs across equal runs"}
    return {"status": "pass", "message": "compile engine deterministic fingerprint stable"}
