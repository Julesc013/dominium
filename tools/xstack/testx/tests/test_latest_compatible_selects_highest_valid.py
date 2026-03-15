"""FAST test: latest-compatible policy selects the highest valid non-yanked descriptor."""

from __future__ import annotations


TEST_ID = "test_latest_compatible_selects_highest_valid"
TEST_TAGS = ["fast", "release", "release-index-policy", "selection"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release_index_policy_testlib import build_report

    report = build_report(repo_root)
    latest = dict(report.get("latest_fixture") or {})
    if report.get("result") != "complete":
        return {"status": "fail", "message": "release-index policy baseline must complete"}
    if str(latest.get("selected_client_version", "")).strip() != "0.0.1":
        return {"status": "fail", "message": "latest-compatible did not select the highest valid client version"}
    if str(latest.get("selected_client_build_id", "")).strip() != "build.latest.compatible":
        return {"status": "fail", "message": "latest-compatible did not select the expected highest-ranked client build"}
    return {"status": "pass", "message": "latest-compatible selects the highest valid non-yanked descriptor"}
