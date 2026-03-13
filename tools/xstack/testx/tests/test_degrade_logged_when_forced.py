"""FAST test: DIST-4 forced fallback rows emit deterministic degrade logs when required."""

from __future__ import annotations


TEST_ID = "test_degrade_logged_when_forced"
TEST_TAGS = ["fast", "dist", "release", "platform", "fallback"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist4_testlib import fallback_rows, load_report

    report = load_report(repo_root)
    rows = fallback_rows(report)
    if not rows:
        return {"status": "fail", "message": "DIST-4 fallback rows are missing"}
    for row in rows:
        if not bool(row.get("passed")):
            return {
                "status": "fail",
                "message": "DIST-4 forced fallback failed for {} {}".format(
                    str(row.get("product_id", "")).strip(),
                    str(row.get("requested_mode_id", "")).strip(),
                ),
            }
        if bool(row.get("degrade_expected")) and not bool(row.get("degrade_logged")):
            return {
                "status": "fail",
                "message": "DIST-4 forced fallback did not log degradation for {} {}".format(
                    str(row.get("product_id", "")).strip(),
                    str(row.get("requested_mode_id", "")).strip(),
                ),
            }
    return {"status": "pass", "message": "DIST-4 forced fallbacks log degradation deterministically"}
