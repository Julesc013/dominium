"""FAST test: SERVER-MVP-1 ready handshake uses bounded deterministic polling."""

from __future__ import annotations


TEST_ID = "test_ready_handshake_no_wallclock"
TEST_TAGS = ["fast", "server", "singleplayer"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp1_testlib import run_window

    report = run_window(repo_root, suffix="ready_handshake", ticks=3)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "local singleplayer window did not complete"}
    readiness = dict(report.get("readiness") or {})
    if str(readiness.get("strategy", "")).strip() != "bounded_poll_iterations":
        return {"status": "fail", "message": "ready handshake must use bounded_poll_iterations"}
    if int(readiness.get("iterations_used", 0) or 0) < 1:
        return {"status": "fail", "message": "ready handshake should consume at least one deterministic poll iteration"}
    if str(report.get("ack_payload_schema_id", "")).strip() != "server.loopback.ack.v1":
        return {"status": "fail", "message": "expected deterministic loopback ack payload"}
    return {"status": "pass", "message": "SERVER-MVP-1 ready handshake avoids wall-clock timeouts"}
