"""FAST test: AppShell IPC attach refuses when negotiation is skipped."""

from __future__ import annotations


TEST_ID = "test_unnegotiated_attach_refused"
TEST_TAGS = ["fast", "appshell", "ipc", "handshake"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="ipc_unify_missing_negotiation")
    payload_ref = dict(dict(report.get("missing_negotiation") or {}).get("payload_ref") or {})
    message = dict(payload_ref.get("payload_ref") or {})
    refusal = dict(message.get("refusal") or {})
    refusal_code = str(refusal.get("refusal_code", "")).strip()
    if refusal_code != "refusal.connection.no_negotiation":
        return {"status": "fail", "message": "expected refusal.connection.no_negotiation for skipped IPC negotiation"}
    return {"status": "pass", "message": "skipped IPC negotiation is refused explicitly"}
