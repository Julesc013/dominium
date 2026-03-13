"""FAST test: DIST-5 refusal surfaces always include remediation guidance."""

from __future__ import annotations


TEST_ID = "test_refusal_contains_remediation"
TEST_TAGS = ["fast", "dist", "release", "ux", "refusal"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist5_testlib import load_report, refusal_rows

    report = load_report(repo_root)
    rows = refusal_rows(report)
    if not rows:
        return {"status": "fail", "message": "DIST-5 refusal rows are missing"}
    for row in rows:
        if str(row.get("result", "")).strip() != "refused":
            return {"status": "fail", "message": "surface {} did not refuse".format(str(row.get("surface_id", "")).strip())}
        if not str(row.get("refusal_code", "")).strip():
            return {"status": "fail", "message": "surface {} omitted refusal code".format(str(row.get("surface_id", "")).strip())}
        if not str(row.get("remediation_hint", "")).strip():
            return {"status": "fail", "message": "surface {} omitted remediation hint".format(str(row.get("surface_id", "")).strip())}
    return {"status": "pass", "message": "DIST-5 refusal surfaces include stable remediation guidance"}
