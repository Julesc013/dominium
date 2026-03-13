"""FAST test: committed virtual path baseline fingerprint matches the generated report."""

from __future__ import annotations


TEST_ID = "test_cross_platform_vpath_behavior_consistent"
TEST_TAGS = ["fast", "appshell", "paths", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout0_testlib import baseline_fingerprint, build_report

    report = build_report(repo_root)
    try:
        expected = baseline_fingerprint(repo_root)
    except ValueError as exc:
        return {"status": "fail", "message": str(exc)}
    if str(report.get("deterministic_fingerprint", "")).strip() != expected:
        return {"status": "fail", "message": "virtual path baseline fingerprint drifted from the committed report"}
    return {"status": "pass", "message": "virtual path report fingerprint matches the committed baseline"}
