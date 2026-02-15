"""STRICT test: handshake refuses disallowed replication policy under server policy matrix."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_refuse_policy_not_allowed"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake.policy_not_allowed",
        requested_replication_policy_id="policy.net.srz_hybrid",
        anti_cheat_policy_id="policy.ac.rank_strict",
        server_policy_id="server.policy.ranked.strict",
        securex_policy_id="securex.rank.require_signed",
    )
    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=dict(fixture["lock_payload"]),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "handshake unexpectedly accepted disallowed replication policy"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.net.handshake_policy_not_allowed":
        return {"status": "fail", "message": "unexpected refusal code for disallowed replication policy"}
    return {"status": "pass", "message": "disallowed replication policy refusal is deterministic"}
