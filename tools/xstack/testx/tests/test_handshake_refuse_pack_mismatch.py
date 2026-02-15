"""STRICT test: handshake refuses deterministic pack_lock hash mismatch."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_refuse_pack_mismatch"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake.pack_mismatch",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.casual_default",
        server_policy_id="server.policy.private.default",
        securex_policy_id="",
    )
    bad_hash = "0" * 64
    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=dict(fixture["lock_payload"]),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        authority_context=dict(fixture["authority_context"]),
        client_pack_lock_hash=bad_hash,
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "handshake unexpectedly accepted mismatched client pack_lock_hash"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.net.handshake_pack_lock_mismatch":
        return {"status": "fail", "message": "unexpected refusal code for pack_lock mismatch"}
    return {"status": "pass", "message": "pack_lock mismatch refusal is deterministic"}
