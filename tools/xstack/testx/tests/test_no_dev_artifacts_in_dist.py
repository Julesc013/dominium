"""FAST test: DIST-1 bundle excludes development artifacts."""

from __future__ import annotations


TEST_ID = "test_no_dev_artifacts_in_dist"
TEST_TAGS = ["fast", "dist", "audit"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist1_testlib import minimize_report

    report = minimize_report(repo_root)
    if list(report.get("dev_artifacts") or []):
        return {"status": "fail", "message": "DIST-1 bundle still contains development artifacts"}
    if list(report.get("unexpected_top_level") or []):
        return {"status": "fail", "message": "DIST-1 bundle contains unexpected top-level entries"}
    if list(report.get("missing_pack_paths") or []):
        return {"status": "fail", "message": "DIST-1 bundle is missing required packs"}
    if list(report.get("unexpected_pack_paths") or []):
        return {"status": "fail", "message": "DIST-1 bundle contains unexpected extra packs"}
    return {"status": "pass", "message": "DIST-1 bundle excludes development artifacts and extra content"}
