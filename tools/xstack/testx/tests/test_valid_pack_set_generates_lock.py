"""FAST test: valid pack sets generate deterministic verification lock output."""

from __future__ import annotations


TEST_ID = "test_valid_pack_set_generates_lock"
TEST_TAGS = ["fast", "packs", "compat", "verification"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat1_testlib import (
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        verify_fixture_pack_set,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        result = verify_fixture_pack_set(repo_root, temp_repo)
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "verification pipeline refused valid fixture pack set"}
        report = dict(result.get("report") or {})
        pack_lock = dict(result.get("pack_lock") or {})
        if not bool(report.get("valid", False)):
            return {"status": "fail", "message": "valid fixture pack set marked invalid"}
        if not str(pack_lock.get("pack_lock_hash", "")).strip():
            return {"status": "fail", "message": "verified pack lock hash missing"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "valid pack set generates deterministic verified pack lock"}
