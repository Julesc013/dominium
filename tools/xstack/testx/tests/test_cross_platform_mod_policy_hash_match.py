"""FAST test: mod policy proof hashes remain deterministic across repeated compiles."""

from __future__ import annotations


TEST_ID = "test_cross_platform_mod_policy_hash_match"
TEST_TAGS = ["fast", "modding", "policy", "hash"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mod_policy0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        load_fixture_lockfile,
        make_temp_mod_policy_repo,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_mod_policy_repo(repo_root)
    try:
        first = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(first.get("result", "")) != "complete":
            return {"status": "fail", "message": "first fixture compile failed"}
        first_lock = load_fixture_lockfile(temp_repo)
        second = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "second fixture compile failed"}
        second_lock = load_fixture_lockfile(temp_repo)
        first_hash = str(dict(first.get("mod_policy_proof_bundle") or {}).get("mod_policy_proof_hash", "")).strip()
        second_hash = str(dict(second.get("mod_policy_proof_bundle") or {}).get("mod_policy_proof_hash", "")).strip()
        if not first_hash or first_hash != second_hash:
            return {"status": "fail", "message": "mod policy proof hash drifted across repeated compiles"}
        if str(first_lock.get("mod_policy_proof_hash", "")).strip() != str(second_lock.get("mod_policy_proof_hash", "")).strip():
            return {"status": "fail", "message": "lockfile mod policy proof hash drifted across repeated compiles"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "mod policy proof hashes remain deterministic across repeated compiles"}
