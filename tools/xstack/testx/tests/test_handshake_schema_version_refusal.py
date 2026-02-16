"""STRICT test: handshake schema-version mismatch refusal is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.handshake_schema_version_refusal"
TEST_TAGS = ["strict", "net", "security", "multiplayer"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake_schema_version_refusal",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.casual_default",
        server_profile_id="server.profile.private_relaxed",
        server_policy_id="server.policy.private.default",
        securex_policy_id="securex.policy.private_relaxed",
    )
    session_spec = copy.deepcopy(dict(fixture["session_spec"]))
    network = dict(session_spec.get("network") or {})
    schema_versions = dict(network.get("schema_versions") or {})
    schema_versions["session_spec"] = "9.9.9"
    network["schema_versions"] = schema_versions
    session_spec["network"] = network

    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=session_spec,
        lock_payload=dict(fixture["lock_payload"]),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "handshake unexpectedly accepted incompatible schema version"}
    refusal_code = str(((result.get("refusal") or {}).get("reason_code", "")))
    if refusal_code != "refusal.net.handshake_schema_version_mismatch":
        return {"status": "fail", "message": "unexpected refusal code for schema version mismatch"}
    return {"status": "pass", "message": "schema version mismatch refusal is deterministic"}
