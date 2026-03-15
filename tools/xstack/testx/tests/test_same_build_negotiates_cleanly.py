"""FAST test: DIST-6 same-build interop negotiates without refusal."""

from __future__ import annotations


TEST_ID = "test_same_build_negotiates_cleanly"
TEST_TAGS = ["fast", "dist", "interop", "compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist6_testlib import load_case

    report = load_case(repo_root, "same_build_same_build")
    negotiation = dict(report.get("negotiation") or {})
    if not report:
        return {"status": "fail", "message": "DIST-6 same-build report is missing"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-6 same-build interop did not complete"}
    if str(negotiation.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "same-build negotiation did not complete"}
    if str(negotiation.get("refusal_code", "")).strip():
        return {"status": "fail", "message": "same-build negotiation refused unexpectedly"}
    return {"status": "pass", "message": "same-build client/server interop negotiated cleanly"}
