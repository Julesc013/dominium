"""STRICT test: identical handshake inputs produce identical deterministic handshake artifacts."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.handshake_deterministic_outputs"
TEST_TAGS = ["strict", "net", "determinism", "session"]


def _fingerprint(result: dict) -> dict:
    return {
        "result": str(result.get("result", "")),
        "handshake_id": str(result.get("handshake_id", "")),
        "handshake_artifact_hash": str(result.get("handshake_artifact_hash", "")),
        "request_proto_hash": str(((result.get("proto_hashes") or {}).get("request_proto_hash", ""))),
        "response_proto_hash": str(((result.get("proto_hashes") or {}).get("response_proto_hash", ""))),
        "negotiated_replication_policy_id": str(result.get("negotiated_replication_policy_id", "")),
        "server_law_profile_id": str(result.get("server_law_profile_id", "")),
        "anti_cheat_policy_id": str(result.get("anti_cheat_policy_id", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake.deterministic",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.casual_default",
        server_policy_id="server.policy.private.default",
        securex_policy_id="",
    )
    first = run_loopback_handshake(
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
    second = run_loopback_handshake(
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
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "deterministic handshake test requires two accepted handshakes"}
    if _fingerprint(first) != _fingerprint(second):
        return {"status": "fail", "message": "handshake deterministic fingerprint mismatch across repeated runs"}
    return {"status": "pass", "message": "handshake deterministic outputs are stable across repeated runs"}
