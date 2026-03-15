"""FAST test: latest-compatible policy excludes yanked descriptors and logs the skip."""

from __future__ import annotations


TEST_ID = "test_yanked_excluded_from_latest"
TEST_TAGS = ["fast", "release", "release-index-policy", "yank"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release_index_policy_testlib import build_report

    report = build_report(repo_root)
    latest = dict(report.get("latest_fixture") or {})
    if list(latest.get("selected_yanked_component_ids") or []):
        return {"status": "fail", "message": "latest-compatible selected a yanked component"}
    if int(latest.get("skipped_yanked_count", 0) or 0) < 1:
        return {"status": "fail", "message": "latest-compatible did not log the skipped yanked candidate"}
    return {"status": "pass", "message": "yanked candidates are excluded from latest-compatible resolution"}
