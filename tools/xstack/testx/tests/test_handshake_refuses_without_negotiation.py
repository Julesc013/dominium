"""FAST test: CAP-NEG-2 intent submission refuses when negotiation metadata is missing."""

from __future__ import annotations


TEST_ID = "test_handshake_refuses_without_negotiation"
TEST_TAGS = ["fast", "compat", "cap_neg", "server"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import boot_fixture, ensure_repo_on_path

    ensure_repo_on_path(repo_root)

    from src.server.server_boot import submit_client_intent
    from tools.server.server_mvp0_probe import connect_loopback_client

    fixture = boot_fixture(repo_root, suffix="cap_neg2_missing_negotiation")
    boot = dict(fixture.get("boot") or {})
    if str(boot.get("result", "")) != "complete":
        return {"status": "fail", "message": "server boot fixture failed for handshake refusal test"}
    handshake = connect_loopback_client(boot)
    if str(handshake.get("result", "")) != "complete":
        return {"status": "fail", "message": "loopback handshake fixture failed before negotiation-removal test"}

    runtime = boot.get("runtime")
    if not isinstance(runtime, dict):
        return {"status": "fail", "message": "server runtime missing from boot payload"}
    connections = dict(runtime.get("server_mvp_connections") or {})
    connection_id = str((dict(handshake.get("accepted") or {})).get("connection_id", "")).strip()
    row = dict(connections.get(connection_id) or {})
    if not row:
        return {"status": "fail", "message": "loopback connection row missing from runtime"}
    row.pop("negotiation_record_hash", None)
    row["compatibility_mode_id"] = ""
    connections[connection_id] = row
    runtime["server_mvp_connections"] = dict((key, connections[key]) for key in sorted(connections.keys()))

    result = submit_client_intent(
        boot,
        connection_id=connection_id,
        intent={
            "intent_id": "intent.cap_neg2.no_negotiation",
            "target": "body.emb.test",
            "process_id": "process.agent_move",
        },
    )
    refusal = dict(result.get("refusal") or {})
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "intent submission did not refuse without negotiation metadata"}
    if str(refusal.get("reason_code", "")) != "refusal.connection.no_negotiation":
        return {"status": "fail", "message": "unexpected refusal code when negotiation metadata is missing"}
    return {"status": "pass", "message": "intent submission refuses without negotiation metadata"}
