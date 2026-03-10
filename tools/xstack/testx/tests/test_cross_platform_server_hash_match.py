"""FAST test: SERVER-MVP-0 replay hash is stable across repeated runs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_server_hash_match"
TEST_TAGS = ["fast", "server", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import verify_replay

    report = verify_replay(repo_root)
    if str(report.get("result", "")) != "complete" or not bool(report.get("stable")):
        return {"status": "fail", "message": "server replay fingerprint verification failed"}
    first = dict(report.get("first_report") or {})
    second = dict(report.get("second_report") or {})
    first_hash = str(first.get("cross_platform_server_hash", "")).strip()
    second_hash = str(second.get("cross_platform_server_hash", "")).strip()
    if (not first_hash) or first_hash != second_hash:
        return {"status": "fail", "message": "cross_platform_server_hash drifted across repeated runs"}
    return {"status": "pass", "message": "server replay hash is stable across repeated runs"}
