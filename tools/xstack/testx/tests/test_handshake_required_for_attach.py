"""FAST test: APPSHELL-4 refuses attach attempts that skip negotiation."""

from __future__ import annotations


TEST_ID = "test_handshake_required_for_attach"
TEST_TAGS = ["fast", "appshell", "ipc", "handshake"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="missing_negotiation")
    payload_ref = dict(dict(report.get("missing_negotiation") or {}).get("payload_ref") or {})
    message = dict(payload_ref.get("payload_ref") or {})
    refusal = dict(message.get("refusal") or {})
    refusal_code = str(refusal.get("refusal_code", "")).strip()
    if refusal_code != "refusal.connection.no_negotiation":
        return {"status": "fail", "message": "missing negotiation did not yield refusal.connection.no_negotiation"}
    return {"status": "pass", "message": "missing negotiation is refused explicitly"}
