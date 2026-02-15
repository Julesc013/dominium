"""Shared helpers for deterministic MP-2 handshake tests."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Tuple


REGISTRY_FILE_MAP = {
    "net_replication_policy_registry_hash": "net_replication_policy.registry.json",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy.registry.json",
    "net_server_policy_registry_hash": "net_server_policy.registry.json",
    "securex_policy_registry_hash": "securex_policy.registry.json",
    "server_profile_registry_hash": "server_profile.registry.json",
}


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_lock_and_registries(repo_root: str, lock_payload: dict) -> Tuple[dict, dict, dict, dict, dict]:
    registry_hashes = dict(lock_payload.get("registries") or {})
    payloads = {}
    for hash_key, filename in sorted(REGISTRY_FILE_MAP.items(), key=lambda item: item[0]):
        payload = _read_json(os.path.join(repo_root, "build", "registries", filename))
        expected = str(registry_hashes.get(hash_key, "")).strip()
        actual = str(payload.get("registry_hash", "")).strip()
        if expected != actual:
            raise RuntimeError("registry hash mismatch for '{}'".format(filename))
        payloads[hash_key] = payload
    return (
        payloads["net_replication_policy_registry_hash"],
        payloads["anti_cheat_policy_registry_hash"],
        payloads["net_server_policy_registry_hash"],
        payloads["securex_policy_registry_hash"],
        payloads["server_profile_registry_hash"],
    )


def prepare_handshake_fixture(
    repo_root: str,
    *,
    save_id: str,
    requested_replication_policy_id: str,
    anti_cheat_policy_id: str,
    server_policy_id: str,
    server_profile_id: str = "",
    securex_policy_id: str = "",
    desired_law_profile_id: str = "",
):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec

    created = create_session_spec(
        repo_root=repo_root,
        save_id=str(save_id),
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.mp2.handshake.fixture",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.mp2.handshake.universe",
        universe_id="",
        entitlements=["session.boot", "entitlement.inspect", "entitlement.teleport"],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        net_endpoint="loopback://mp2.handshake.fixture",
        net_transport_id="transport.loopback",
        net_client_peer_id="peer.client.alpha",
        net_server_peer_id="peer.server.lab",
        net_replication_policy_id=str(requested_replication_policy_id),
        net_anti_cheat_policy_id=str(anti_cheat_policy_id),
        net_server_profile_id=str(server_profile_id),
        net_server_policy_id=str(server_policy_id),
        net_securex_policy_id=str(securex_policy_id),
        net_desired_law_profile_id=str(desired_law_profile_id),
        net_schema_versions=[],
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        raise RuntimeError("create_session_spec refused")

    session_spec_path = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    session_spec = _read_json(session_spec_path)
    lock_payload = _read_json(os.path.join(repo_root, "build", "lockfile.json"))
    (
        replication_registry,
        anti_cheat_registry,
        server_policy_registry,
        securex_policy_registry,
        server_profile_registry,
    ) = _load_lock_and_registries(repo_root, lock_payload)
    authority_context = dict(session_spec.get("authority_context") or {})
    return {
        "session_spec": session_spec,
        "lock_payload": lock_payload,
        "replication_registry": replication_registry,
        "anti_cheat_registry": anti_cheat_registry,
        "server_policy_registry": server_policy_registry,
        "securex_policy_registry": securex_policy_registry,
        "server_profile_registry": server_profile_registry,
        "authority_context": authority_context,
    }
