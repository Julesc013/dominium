"""FAST test: DIST-6 cross-platform interop remains deterministic."""

from __future__ import annotations


TEST_ID = "test_cross_platform_negotiation_consistent"
TEST_TAGS = ["fast", "dist", "interop", "platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist6_testlib import load_case

    report = load_case(repo_root, "same_version_cross_platform")
    negotiation = dict(report.get("negotiation") or {})
    client_descriptor = dict(report.get("client_descriptor") or {})
    server_descriptor = dict(report.get("server_descriptor") or {})
    if not report:
        return {"status": "fail", "message": "DIST-6 cross-platform report is missing"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-6 cross-platform case did not complete"}
    if str(negotiation.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "cross-platform negotiation did not complete"}
    if not str(negotiation.get("negotiation_record_hash", "")).strip():
        return {"status": "fail", "message": "cross-platform negotiation record hash is missing"}
    if str(client_descriptor.get("platform_id", "")).strip() == str(server_descriptor.get("platform_id", "")).strip():
        return {"status": "fail", "message": "cross-platform case did not project a distinct platform id"}
    return {"status": "pass", "message": "cross-platform interop remains deterministic and platform-aware"}
