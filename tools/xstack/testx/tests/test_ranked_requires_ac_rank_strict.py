"""STRICT test: ranked profile requires policy.ac.rank_strict and refuses mismatches."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ranked_requires_ac_rank_strict"
TEST_TAGS = ["strict", "net", "security"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ranked_requires_ac_rank_strict",
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
        return {"status": "fail", "message": "ranked handshake unexpectedly accepted non-strict anti-cheat policy"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.net.handshake_policy_not_allowed":
        return {"status": "fail", "message": "unexpected refusal code for ranked anti-cheat mismatch"}
    return {"status": "pass", "message": "ranked profile enforces policy.ac.rank_strict deterministically"}

