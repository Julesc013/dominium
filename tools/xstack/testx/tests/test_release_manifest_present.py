"""FAST test: DIST-1 bundle ships a verifiable release manifest."""

from __future__ import annotations


TEST_ID = "test_release_manifest_present"
TEST_TAGS = ["fast", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist1_testlib import release_manifest_verification

    result = release_manifest_verification(repo_root)
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-1 release manifest did not verify offline"}
    return {"status": "pass", "message": "DIST-1 release manifest is present and verifies offline"}
