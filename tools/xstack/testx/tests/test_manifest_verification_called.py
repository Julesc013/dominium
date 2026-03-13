"""FAST test: DIST-2 verifier runs offline release-manifest verification."""

from __future__ import annotations


TEST_ID = "test_manifest_verification_called"
TEST_TAGS = ["fast", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist2_testlib import load_report

    report = load_report(repo_root)
    verify_row = dict(report.get("release_manifest_verification") or {})
    if str(verify_row.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-2 verifier did not complete release-manifest verification"}
    if int(verify_row.get("verified_artifact_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "release-manifest verification did not verify any artifacts"}
    return {"status": "pass", "message": "DIST-2 verifier runs offline release-manifest verification"}
