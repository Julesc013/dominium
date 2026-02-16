"""STRICT test: ranked handshake acceptance/refusal matrix remains deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.handshake_matrix_ranked"
TEST_TAGS = ["strict", "net", "security", "multiplayer"]


def _run_case(repo_root: str, fixture: dict, lock_payload: dict):
    from tools.xstack.sessionx.net_handshake import run_loopback_handshake

    return run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=dict(lock_payload),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake_matrix_ranked",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.rank_strict",
        server_profile_id="server.profile.rank_strict",
        server_policy_id="server.policy.ranked.strict",
        securex_policy_id="securex.policy.rank_strict",
    )
    signed_lock = copy.deepcopy(dict(fixture["lock_payload"]))
    signed_lock["resolved_packs"] = [
        dict(dict(row or {}), signature_status="signed")
        for row in list(signed_lock.get("resolved_packs") or [])
        if isinstance(row, dict)
    ]
    accept = _run_case(repo_root=repo_root, fixture=fixture, lock_payload=signed_lock)
    if str(accept.get("result", "")) != "complete":
        return {"status": "fail", "message": "ranked matrix expected signed acceptance but handshake refused"}

    unsigned_lock = copy.deepcopy(dict(signed_lock))
    rows = list(unsigned_lock.get("resolved_packs") or [])
    if not rows:
        return {"status": "fail", "message": "ranked handshake matrix fixture has empty resolved_packs"}
    rows[0] = dict(dict(rows[0] or {}), signature_status="unsigned")
    unsigned_lock["resolved_packs"] = rows
    refused_unsigned = _run_case(repo_root=repo_root, fixture=fixture, lock_payload=unsigned_lock)
    if str((refused_unsigned.get("refusal") or {}).get("reason_code", "")) != "refusal.net.handshake_securex_denied":
        return {"status": "fail", "message": "ranked matrix unsigned-pack refusal code mismatch"}

    observer_fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.handshake_matrix_ranked.observer_refusal",
        requested_replication_policy_id="policy.net.lockstep",
        anti_cheat_policy_id="policy.ac.rank_strict",
        server_profile_id="server.profile.rank_strict",
        server_policy_id="server.policy.ranked.strict",
        securex_policy_id="securex.policy.rank_strict",
        desired_law_profile_id="law.lab.observe_only",
    )
    observer_lock = copy.deepcopy(dict(observer_fixture["lock_payload"]))
    observer_lock["resolved_packs"] = [
        dict(dict(row or {}), signature_status="signed")
        for row in list(observer_lock.get("resolved_packs") or [])
        if isinstance(row, dict)
    ]
    refused_observer = _run_case(repo_root=repo_root, fixture=observer_fixture, lock_payload=observer_lock)
    if str((refused_observer.get("refusal") or {}).get("reason_code", "")) != "refusal.net.handshake_policy_not_allowed":
        return {"status": "fail", "message": "ranked matrix observer-law refusal code mismatch"}

    return {"status": "pass", "message": "ranked handshake matrix acceptance/refusal is deterministic"}
