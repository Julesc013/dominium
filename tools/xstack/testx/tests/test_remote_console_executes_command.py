"""FAST test: APPSHELL-4 remote console executes registry-backed commands."""

from __future__ import annotations


TEST_ID = "test_remote_console_executes_command"
TEST_TAGS = ["fast", "appshell", "ipc", "console"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="console")
    console = dict(report.get("console") or {})
    stdout = str(console.get("stdout", "")).strip()
    dispatch = dict(console.get("dispatch") or {})
    exit_code = dispatch.get("exit_code")
    if exit_code is None or int(exit_code) != 0:
        return {"status": "fail", "message": "remote console command returned non-zero exit code"}
    if '"product_id":"server"' not in stdout.replace(" ", ""):
        return {"status": "fail", "message": "remote console command did not return the server version payload"}
    return {"status": "pass", "message": "remote console executes registry-backed commands over IPC"}
