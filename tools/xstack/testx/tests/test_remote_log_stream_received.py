"""FAST test: APPSHELL-4 remote log stream returns structured events."""

from __future__ import annotations


TEST_ID = "test_remote_log_stream_received"
TEST_TAGS = ["fast", "appshell", "ipc", "logs"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import run_probe

    report = run_probe(repo_root, suffix="logs")
    keys = [str(dict(row).get("message_key", "")).strip() for row in list(report.get("log_events") or [])]
    if not keys:
        return {"status": "fail", "message": "remote IPC log query returned no events"}
    if "ipc.endpoint.started" not in keys and "ipc.attach.accepted" not in keys:
        return {"status": "fail", "message": "remote log stream did not include expected IPC lifecycle markers"}
    return {"status": "pass", "message": "remote IPC log stream returns structured lifecycle events"}
