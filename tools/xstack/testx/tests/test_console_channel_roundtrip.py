"""FAST test: AppShell IPC console channel round-trips through the canonical client/server stack."""

from __future__ import annotations


TEST_ID = "test_console_channel_roundtrip"
TEST_TAGS = ["fast", "appshell", "ipc", "console"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="ipc_unify_console")
    console = dict(report.get("console") or {})
    dispatch = dict(console.get("dispatch") or {})
    exit_code = dispatch.get("exit_code")
    stdout = str(console.get("stdout", "")).strip()
    if exit_code is None or int(exit_code) != 0:
        return {"status": "fail", "message": "console channel roundtrip returned non-zero exit code"}
    if '"product_id":"server"' not in stdout.replace(" ", ""):
        return {"status": "fail", "message": "console channel roundtrip did not return the server version payload"}
    return {"status": "pass", "message": "console channel roundtrip succeeds over the canonical IPC stack"}
