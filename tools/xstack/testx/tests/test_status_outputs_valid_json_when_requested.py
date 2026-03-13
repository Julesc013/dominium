"""FAST test: DIST-5 status surfaces remain JSON-readable when requested."""

from __future__ import annotations


TEST_ID = "test_status_outputs_valid_json_when_requested"
TEST_TAGS = ["fast", "dist", "release", "ux", "status"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist5_testlib import load_report, status_rows

    report = load_report(repo_root)
    rows = status_rows(report)
    if not rows:
        return {"status": "fail", "message": "DIST-5 status rows are missing"}
    requested_rows = [row for row in rows if bool(row.get("json_requested"))]
    if not requested_rows:
        return {"status": "fail", "message": "DIST-5 did not exercise any explicit --json status surfaces"}
    for row in requested_rows:
        if not bool(row.get("payload_present")):
            return {"status": "fail", "message": "status payload missing for {}".format(str(row.get("surface_id", "")).strip())}
        if not bool(row.get("has_summary")):
            return {"status": "fail", "message": "status summary missing for {}".format(str(row.get("surface_id", "")).strip())}
        if not str(row.get("message", "")).strip():
            return {"status": "fail", "message": "status message missing for {}".format(str(row.get("surface_id", "")).strip())}
    return {"status": "pass", "message": "DIST-5 status surfaces remain valid JSON when requested"}
