"""FAST test: pack compatibility hashes are stable across repeated compiles."""

from __future__ import annotations


TEST_ID = "test_cross_platform_pack_compat_hash_match"
TEST_TAGS = ["fast", "packs", "compat", "hash"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        load_fixture_lockfile,
        make_temp_pack_compat_repo,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        first = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(first.get("result", "")) != "complete":
            return {"status": "fail", "message": "first compat compile failed"}
        first_lock = load_fixture_lockfile(temp_repo)
        second = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "second compat compile failed"}
        second_lock = load_fixture_lockfile(temp_repo)
        if str(first_lock.get("pack_lock_hash", "")).strip() != str(second_lock.get("pack_lock_hash", "")).strip():
            return {"status": "fail", "message": "pack lock hash drifted across repeated compiles"}
        first_rows = list(first_lock.get("resolved_packs") or [])
        second_rows = list(second_lock.get("resolved_packs") or [])
        if first_rows != second_rows:
            return {"status": "fail", "message": "resolved pack compat rows drifted across repeated compiles"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "pack compatibility hashes remain stable across repeated compiles"}
