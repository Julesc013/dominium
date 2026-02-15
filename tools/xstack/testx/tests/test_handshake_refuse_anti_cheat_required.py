"""STRICT test: ranked server policy anti-cheat requirement is enforced deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_refuse_anti_cheat_required"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake.anti_cheat_required",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.casual_default",
        server_profile_id="server.profile.rank_strict",
        server_policy_id="server.policy.ranked.strict",
        securex_policy_id="securex.policy.rank_strict",
    )
    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=dict(fixture["lock_payload"]),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "handshake unexpectedly accepted when ranked anti-cheat policy was not satisfied"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.net.handshake_policy_not_allowed":
        return {"status": "fail", "message": "unexpected refusal code for ranked anti-cheat requirement"}
    message = str(refusal_payload.get("message", "")).lower()
    if "anti-cheat" not in message:
        return {"status": "fail", "message": "ranked anti-cheat refusal message is missing anti-cheat context"}
    return {"status": "pass", "message": "ranked anti-cheat requirement refusal is deterministic"}
