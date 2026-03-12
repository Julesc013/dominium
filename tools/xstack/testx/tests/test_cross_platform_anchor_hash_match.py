"""FAST test: cross-platform anchor hashes agree canonically."""

from __future__ import annotations


TEST_ID = "test_cross_platform_anchor_hash_match"
TEST_TAGS = ["fast", "time", "anchor", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.time_anchor_testlib import load_verify_report

    report, error = load_verify_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    checks = dict(report.get("checks") or {})
    if not bool(checks.get("cross_platform_anchor_hash_match", False)):
        return {"status": "fail", "message": "verify report did not confirm cross-platform anchor hash agreement"}
    hashes = dict(report.get("cross_platform_anchor_hashes") or {})
    values = [str(hashes.get(platform, "")).strip() for platform in ("windows", "macos", "linux")]
    if any(not value for value in values):
        return {"status": "fail", "message": "cross-platform anchor hash set is incomplete"}
    if len(set(values)) != 1:
        return {"status": "fail", "message": "cross-platform anchor hashes diverged"}
    return {"status": "pass", "message": "cross-platform anchor hashes match canonically"}
