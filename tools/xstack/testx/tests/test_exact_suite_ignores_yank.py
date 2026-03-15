"""FAST test: exact-suite keeps the pinned descriptor even when it is yanked."""

from __future__ import annotations


TEST_ID = "test_exact_suite_ignores_yank"
TEST_TAGS = ["fast", "release", "release-index-policy", "yank"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release_index_policy_testlib import build_report

    report = build_report(repo_root)
    latest = dict(report.get("latest_fixture") or {})
    exact = dict(report.get("exact_fixture") or {})
    if str(exact.get("selected_client_build_id", "")).strip() == str(latest.get("selected_client_build_id", "")).strip():
        return {"status": "fail", "message": "exact-suite drifted to the latest-compatible client build instead of the pinned descriptor"}
    if "binary.client" not in list(exact.get("selected_yanked_component_ids") or []):
        return {"status": "fail", "message": "exact-suite did not surface the pinned yanked client descriptor"}
    if "warn.update.yanked_component" not in set(exact.get("warning_codes") or []):
        return {"status": "fail", "message": "exact-suite did not warn about the pinned yanked descriptor"}
    return {"status": "pass", "message": "exact-suite retains the pinned descriptor and warns when it is yanked"}
