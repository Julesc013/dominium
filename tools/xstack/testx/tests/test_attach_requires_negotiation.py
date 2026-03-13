"""FAST test: supervisor attach still requires negotiated IPC."""

from __future__ import annotations


TEST_ID = "test_attach_requires_negotiation"
TEST_TAGS = ["fast", "appshell", "supervisor", "ipc"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="supervisor_attach_requires_negotiation")
    payload_ref = dict(dict(report.get("missing_negotiation") or {}).get("payload_ref") or {})
    message = dict(payload_ref.get("payload_ref") or {})
    refusal = dict(message.get("refusal") or {})
    if str(refusal.get("refusal_code", "")).strip() != "refusal.connection.no_negotiation":
        return {"status": "fail", "message": "skipped negotiation did not refuse with refusal.connection.no_negotiation"}
    return {"status": "pass", "message": "supervisor attach discipline still requires negotiated IPC"}
