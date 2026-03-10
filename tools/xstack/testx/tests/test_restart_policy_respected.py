"""FAST test: APPSHELL-6 restart policy is enforced deterministically."""

from __future__ import annotations


TEST_ID = "test_restart_policy_respected"
TEST_TAGS = ["fast", "appshell", "supervisor", "restart_policy"]


def _process_row(state_payload, product_id: str):
    for row in list(dict(state_payload or {}).get("processes") or []):
        row_map = dict(row)
        if str(row_map.get("product_id", "")).strip() == str(product_id).strip():
            return row_map
    return {}


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import run_local_engine

    lab_run_spec, lab_engine, started = run_local_engine(repo_root, seed="seed.appshell6.restart.lab", policy_id="supervisor.policy.lab", topology="server_only")
    if str(started.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "lab supervisor engine failed to start"}
    try:
        process = lab_engine._process_handles.get("server")
        if process is None or process.stdin is None:
            return {"status": "fail", "message": "lab supervisor did not retain a writable child stdin handle"}
        process.stdin.write("crash\n")
        process.stdin.flush()
        lab_engine.refresh()
        lab_state = dict(lab_engine.status().get("state") or {})
        lab_row = _process_row(lab_state, "server")
        if int(lab_row.get("restart_count", 0) or 0) < 1 or str(lab_row.get("status", "")).strip() != "running":
            return {"status": "fail", "message": "lab supervisor did not restart the crashed child"}
    finally:
        lab_engine.stop()

    default_run_spec, default_engine, default_started = run_local_engine(repo_root, seed="seed.appshell6.restart.default", policy_id="supervisor.policy.default", topology="server_only")
    if str(default_started.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "default supervisor engine failed to start"}
    try:
        process = default_engine._process_handles.get("server")
        if process is None or process.stdin is None:
            return {"status": "fail", "message": "default supervisor did not retain a writable child stdin handle"}
        process.stdin.write("crash\n")
        process.stdin.flush()
        default_engine.refresh()
        default_state = dict(default_engine.status().get("state") or {})
        default_row = _process_row(default_state, "server")
        if int(default_row.get("restart_count", 0) or 0) != 0:
            return {"status": "fail", "message": "default supervisor restarted a child despite max_restarts=0"}
    finally:
        default_engine.stop()
    return {"status": "pass", "message": "supervisor restart policy is respected deterministically"}
