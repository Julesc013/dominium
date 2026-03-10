"""FAST test: strict mod policy refuses unsigned packs deterministically."""

from __future__ import annotations


TEST_ID = "test_unsigned_pack_denied_in_strict"
TEST_TAGS = ["fast", "modding", "policy", "trust"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mod_policy0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        make_temp_mod_policy_repo,
        rewrite_pack_trust,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_mod_policy_repo(repo_root)
    try:
        rewrite_pack_trust(temp_repo, "pack.test.base", "trust.unsigned")
        result = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.strict")
        if str(result.get("result", "")) != "refused":
            return {"status": "fail", "message": "strict mod policy accepted an unsigned pack"}
        if str(result.get("refusal_code", "")) != "refusal.mod.trust_denied":
            return {"status": "fail", "message": "strict mod policy returned the wrong refusal code for unsigned pack"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "strict mod policy refuses unsigned packs deterministically"}
