"""FAST test: denied pack capabilities refuse deterministically under mod policy."""

from __future__ import annotations


TEST_ID = "test_capability_denied_refusal"
TEST_TAGS = ["fast", "modding", "policy", "capabilities"]


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
        rewrite_pack_capabilities(temp_repo, "pack.test.base", ["cap.add_contracts"])
        result = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.strict")
        if str(result.get("result", "")) != "refused":
            return {"status": "fail", "message": "strict mod policy accepted a denied capability declaration"}
        if str(result.get("refusal_code", "")) != "refusal.mod.capability_denied":
            return {"status": "fail", "message": "wrong refusal code for denied capability declaration"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "denied capability declarations refuse deterministically"}
