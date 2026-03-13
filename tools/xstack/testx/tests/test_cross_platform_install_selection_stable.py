"""FAST test: install discovery report fingerprint matches the committed baseline."""

from __future__ import annotations


TEST_ID = "test_cross_platform_install_selection_stable"
TEST_TAGS = ["fast", "install", "cross_platform", "baseline"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import baseline_fingerprint, build_report

    report = build_report(repo_root)
    try:
        expected = baseline_fingerprint(repo_root)
    except ValueError as exc:
        return {"status": "fail", "message": str(exc)}
    if str(report.get("deterministic_fingerprint", "")).strip() != expected:
        return {"status": "fail", "message": "install discovery baseline fingerprint drifted from the committed report"}
    return {"status": "pass", "message": "install discovery baseline fingerprint matches the committed report"}
