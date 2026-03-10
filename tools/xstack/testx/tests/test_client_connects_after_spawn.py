"""FAST test: SERVER-MVP-1 client connects after local authority boot."""

from __future__ import annotations


TEST_ID = "test_client_connects_after_spawn"
TEST_TAGS = ["fast", "server", "singleplayer"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp1_testlib import run_window

    report = run_window(repo_root, suffix="client_connect", ticks=4)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "local client/server window did not complete"}
    if str(report.get("launch_mode", "")).strip() != "inproc_loopback_stub":
        return {"status": "fail", "message": "expected inproc loopback local-authority launch mode"}
    response_kinds = list(report.get("control_response_kinds") or [])
    if response_kinds[:2] != ["status", "save_snapshot"]:
        return {"status": "fail", "message": "expected deterministic status/save_snapshot control responses"}
    if not bool(report.get("snapshot_output_exists", False)):
        return {"status": "fail", "message": "control-channel save_snapshot output was not produced"}
    return {"status": "pass", "message": "SERVER-MVP-1 client connects and services control stubs after spawn"}
