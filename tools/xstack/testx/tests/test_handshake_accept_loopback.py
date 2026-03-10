"""STRICT test: deterministic loopback handshake accepts valid matching contracts."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_accept_loopback"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake.accept",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.casual_default",
        server_policy_id="server.policy.private.default",
        securex_policy_id="",
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
    if str(result.get("result", "")) != "complete":
        reason = str(((result.get("refusal") or {}).get("reason_code", "")) if isinstance(result, dict) else "")
        return {"status": "fail", "message": "loopback handshake refused unexpectedly ({})".format(reason)}
    if str(result.get("negotiated_replication_policy_id", "")) != "policy.net.lockstep":
        return {"status": "fail", "message": "unexpected negotiated replication policy id"}
    if str(result.get("server_law_profile_id", "")) != "law.lab.unrestricted":
        return {"status": "fail", "message": "unexpected server law profile id"}
    if not str(result.get("negotiation_record_hash", "")).strip():
        return {"status": "fail", "message": "negotiation record hash is missing from handshake output"}
    if not str(result.get("handshake_artifact_hash", "")).strip():
        return {"status": "fail", "message": "handshake artifact hash is missing"}
    return {"status": "pass", "message": "loopback handshake accepted deterministically"}
