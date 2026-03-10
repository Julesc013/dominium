"""FAST test: SERVER-MVP-0 loopback handshake is deterministic."""

from __future__ import annotations


TEST_ID = "test_loopback_handshake_deterministic"
TEST_TAGS = ["fast", "server", "net"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import run_window

    first = run_window(repo_root, suffix="loopback_handshake", ticks=2)
    second = run_window(repo_root, suffix="loopback_handshake", ticks=2)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "server loopback handshake replay did not complete"}
    comparable_keys = (
        "connection_ids",
        "tick_stream_ticks",
        "proof_anchor_ticks",
        "cross_platform_server_hash",
    )
    for key in comparable_keys:
        if first.get(key) != second.get(key):
            return {"status": "fail", "message": "loopback handshake field '{}' drifted".format(key)}
    if dict(first.get("handshake") or {}) != dict(second.get("handshake") or {}):
        return {"status": "fail", "message": "loopback handshake payload drifted across repeated runs"}
    return {"status": "pass", "message": "server loopback handshake is deterministic"}
