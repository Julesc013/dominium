"""FAST test: strict mod policy forbids explicit nondeterministic allowances."""

from __future__ import annotations


TEST_ID = "test_nondeterminism_forbidden_blocks_pack"
TEST_TAGS = ["fast", "modding", "policy", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mod_policy0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        make_temp_mod_policy_repo,
        rewrite_pack_capabilities,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_mod_policy_repo(repo_root)
    try:
        rewrite_pack_capabilities(
            temp_repo,
            "pack.test.base",
            [],
            extensions={
                "official.requests_nondeterministic_allowance": True,
                "official.source": "MOD-POLICY-0",
            },
        )
        result = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.strict")
        if str(result.get("result", "")) != "refused":
            return {"status": "fail", "message": "strict mod policy accepted nondeterministic allowance metadata"}
        if str(result.get("refusal_code", "")) != "refusal.mod.nondeterminism_forbidden":
            return {"status": "fail", "message": "wrong refusal code for nondeterministic allowance metadata"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "strict mod policy blocks explicit nondeterministic allowances"}
