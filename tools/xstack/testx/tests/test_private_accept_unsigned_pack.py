"""STRICT test: private relaxed profile accepts unsigned pack posture by policy."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.private_accept_unsigned_pack"
TEST_TAGS = ["strict", "net", "security"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.private_accept_unsigned_pack",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.private_relaxed",
        server_profile_id="server.profile.private_relaxed",
        server_policy_id="server.policy.private.default",
        securex_policy_id="securex.policy.private_relaxed",
    )
    lock_payload = copy.deepcopy(dict(fixture["lock_payload"]))
    resolved = list(lock_payload.get("resolved_packs") or [])
    if not resolved:
        return {"status": "fail", "message": "lockfile resolved_packs is empty for private unsigned-pack acceptance test"}
    first = dict(resolved[0] or {})
    first["signature_status"] = "unsigned"
    resolved[0] = first
    lock_payload["resolved_packs"] = resolved

    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=lock_payload,
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(result.get("result", "")) != "complete":
        refusal_payload = dict(result.get("refusal") or {})
        return {
            "status": "fail",
            "message": "private relaxed handshake refused unexpectedly ({})".format(
                str(refusal_payload.get("reason_code", ""))
            ),
        }
    return {"status": "pass", "message": "private relaxed profile accepts unsigned packs by policy"}

