"""FAST test: APPSHELL-6 supervisor auto-attaches child IPC sessions."""

from __future__ import annotations


TEST_ID = "test_auto_attach_ipc_sessions"
TEST_TAGS = ["fast", "appshell", "supervisor", "ipc"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import run_probe

    report = run_probe(repo_root, suffix="auto_attach")
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor probe failed"}
    attachments = list(dict(report.get("attachments") or {}).get("attachments") or [])
    if not attachments:
        return {"status": "fail", "message": "supervisor probe produced no IPC attachments"}
    failed = [row for row in attachments if str(dict(row).get("result", "")).strip() != "complete"]
    if failed:
        return {"status": "fail", "message": "one or more supervised child IPC attaches failed"}
    return {"status": "pass", "message": "supervisor auto-attached all child IPC endpoints"}
