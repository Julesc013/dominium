"""FAST test: GEO-10 overlays preserve stable object identity across all topology suites."""

from __future__ import annotations


TEST_ID = "test_overlay_identity_stable"
TEST_TAGS = ["fast", "geo", "overlay", "identity"]


def run(repo_root: str):
    from tools.xstack.testx.tests.geo10_testlib import geo10_overlay_identity_report

    report = geo10_overlay_identity_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GEO-10 overlay identity verification did not complete"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "GEO-10 overlay identity verification drifted"}
    suite_rows = list(report.get("suite_snapshots") or [])
    if not suite_rows:
        return {"status": "fail", "message": "GEO-10 overlay identity verification produced no suite snapshots"}
    if not all(bool(dict(row).get("stable_identity_under_overlay", False)) for row in suite_rows):
        return {"status": "fail", "message": "one or more topology suites lost stable identity under overlays"}
    return {"status": "pass", "message": "GEO-10 overlays preserve stable identity across topology suites"}
