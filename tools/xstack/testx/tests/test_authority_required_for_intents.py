"""FAST test: SERVER-MVP-0 requires authority context for incoming intents."""

from __future__ import annotations


TEST_ID = "test_authority_required_for_intents"
TEST_TAGS = ["fast", "server", "authority"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import unauthorized_report

    report = unauthorized_report(repo_root)
    if str(report.get("result", "")) != "refused":
        return {"status": "fail", "message": "unauthorized client intent should be refused"}
    reason_code = str(report.get("reason_code", "")).strip()
    if reason_code != "refusal.client.unauthorized":
        return {
            "status": "fail",
            "message": "expected refusal.client.unauthorized, got '{}'".format(reason_code),
        }
    return {"status": "pass", "message": "server requires authority context for incoming intents"}
