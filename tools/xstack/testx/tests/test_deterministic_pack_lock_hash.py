"""FAST test: verified pack lock hashes are stable across repeated verification runs."""

from __future__ import annotations


TEST_ID = "test_deterministic_pack_lock_hash"
TEST_TAGS = ["fast", "packs", "compat", "hash"]


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_json_text
    from tools.xstack.testx.tests.pack_compat1_testlib import (
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        verify_fixture_pack_set,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        first = verify_fixture_pack_set(repo_root, temp_repo)
        second = verify_fixture_pack_set(repo_root, temp_repo)
        if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
            return {"status": "fail", "message": "verification run failed for deterministic pack-lock test"}
        first_lock = dict(first.get("pack_lock") or {})
        second_lock = dict(second.get("pack_lock") or {})
        if str(first_lock.get("pack_lock_hash", "")).strip() != str(second_lock.get("pack_lock_hash", "")).strip():
            return {"status": "fail", "message": "verified pack_lock_hash drifted across repeated verification"}
        if canonical_json_text(first_lock) != canonical_json_text(second_lock):
            return {"status": "fail", "message": "verified pack lock payload drifted across repeated verification"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "verified pack lock hash remains stable across repeated verification"}
