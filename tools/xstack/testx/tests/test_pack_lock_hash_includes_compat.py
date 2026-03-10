"""FAST test: pack lock identity changes when compatibility sidecars change."""

from __future__ import annotations


TEST_ID = "test_pack_lock_hash_includes_compat"
TEST_TAGS = ["fast", "packs", "compat", "lockfile"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        load_fixture_lockfile,
        make_temp_pack_compat_repo,
        mutate_pack_compat,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        first = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(first.get("result", "")) != "complete":
            return {"status": "fail", "message": "first compat-aware compile failed"}
        first_lock = load_fixture_lockfile(temp_repo)
        first_hash = str(first_lock.get("pack_lock_hash", "")).strip()
        first_row = next(
            (row for row in list(first_lock.get("resolved_packs") or []) if str(row.get("pack_id", "")) == "pack.test.base"),
            {},
        )

        mutate_pack_compat(
            temp_repo,
            "pack.test.base",
            lambda payload: {
                **payload,
                "degrade_mode_id": "pack.degrade.best_effort",
            },
        )
        second = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "second compat-aware compile failed"}
        second_lock = load_fixture_lockfile(temp_repo)
        second_hash = str(second_lock.get("pack_lock_hash", "")).strip()
        second_row = next(
            (row for row in list(second_lock.get("resolved_packs") or []) if str(row.get("pack_id", "")) == "pack.test.base"),
            {},
        )
        if not first_hash or first_hash == second_hash:
            return {"status": "fail", "message": "pack_lock_hash did not change after compat manifest mutation"}
        if str(first_row.get("compat_manifest_hash", "")).strip() == str(second_row.get("compat_manifest_hash", "")).strip():
            return {"status": "fail", "message": "resolved pack compat hash did not change after compat mutation"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "pack lock identity includes compatibility sidecars"}
