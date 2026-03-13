"""FAST test: offline release verification succeeds without signatures."""

from __future__ import annotations


TEST_ID = "test_offline_verification_succeeds_without_signature"
TEST_TAGS = ["fast", "release", "verification"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release2_testlib import release_fixture, verify_without_signature

    with release_fixture() as dist_root:
        report = verify_without_signature(dist_root)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "offline release verification failed without signatures"}
    if str(report.get("signature_status", "")) != "signature_missing":
        return {"status": "fail", "message": "verification did not report signature_missing for unsigned manifest"}
    return {"status": "pass", "message": "offline verification succeeds without signatures"}
