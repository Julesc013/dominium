"""FAST test: SERVER-MVP-1 local singleplayer replay hash is stable."""

from __future__ import annotations


TEST_ID = "test_cross_platform_local_orch_hash_match"
TEST_TAGS = ["fast", "server", "singleplayer", "hash"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp1_testlib import verify_replay

    report = verify_replay(repo_root)
    if str(report.get("result", "")) != "complete" or not bool(report.get("stable", False)):
        return {"status": "fail", "message": "local singleplayer replay did not remain stable"}
    first = dict(report.get("first_report") or {})
    second = dict(report.get("second_report") or {})
    if str(first.get("cross_platform_local_orch_hash", "")) != str(second.get("cross_platform_local_orch_hash", "")):
        return {"status": "fail", "message": "cross-platform local orchestration hash drifted"}
    return {"status": "pass", "message": "SERVER-MVP-1 local orchestration hash is stable"}
