"""FAST test: offline verification report/lock hashes are stable across repeated runs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_verification_hash_match"
TEST_TAGS = ["fast", "packs", "compat", "verification", "hash"]


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
            return {"status": "fail", "message": "verification run failed for cross-platform hash check"}
        first_report = dict(first.get("report") or {})
        second_report = dict(second.get("report") or {})
        first_lock = dict(first.get("pack_lock") or {})
        second_lock = dict(second.get("pack_lock") or {})
        if str(first_report.get("deterministic_fingerprint", "")).strip() != str(second_report.get("deterministic_fingerprint", "")).strip():
            return {"status": "fail", "message": "verification report fingerprint drifted"}
        if str(first_lock.get("pack_lock_hash", "")).strip() != str(second_lock.get("pack_lock_hash", "")).strip():
            return {"status": "fail", "message": "verification pack lock hash drifted"}
        if canonical_json_text(first_report) != canonical_json_text(second_report):
            return {"status": "fail", "message": "verification report payload drifted"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "offline verification hashes remain stable across repeated runs"}
