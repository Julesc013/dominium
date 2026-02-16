"""Shared helpers for deterministic MP-4 server-authoritative tests."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Dict, Tuple


REGISTRY_FILE_MAP = {
    "law_registry_hash": "law.registry.json",
    "experience_registry_hash": "experience.registry.json",
    "lens_registry_hash": "lens.registry.json",
    "view_mode_registry_hash": "view_mode.registry.json",
    "render_proxy_registry_hash": "render_proxy.registry.json",
    "cosmetic_registry_hash": "cosmetic.registry.json",
    "cosmetic_policy_registry_hash": "cosmetic_policy.registry.json",
    "net_replication_policy_registry_hash": "net_replication_policy.registry.json",
    "net_server_policy_registry_hash": "net_server_policy.registry.json",
    "server_profile_registry_hash": "server_profile.registry.json",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy.registry.json",
    "anti_cheat_module_registry_hash": "anti_cheat_module.registry.json",
    "astronomy_catalog_index_hash": "astronomy.catalog.index.json",
    "site_registry_index_hash": "site.registry.index.json",
    "ephemeris_registry_hash": "ephemeris.registry.json",
    "terrain_tile_registry_hash": "terrain.tile.registry.json",
    "activation_policy_registry_hash": "activation_policy.registry.json",
    "budget_policy_registry_hash": "budget_policy.registry.json",
    "fidelity_policy_registry_hash": "fidelity_policy.registry.json",
    "perception_interest_policy_registry_hash": "perception_interest_policy.registry.json",
    "epistemic_policy_registry_hash": "epistemic_policy.registry.json",
    "retention_policy_registry_hash": "retention_policy.registry.json",
    "decay_model_registry_hash": "decay_model.registry.json",
    "eviction_rule_registry_hash": "eviction_rule.registry.json",
}


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_lock_and_registries(repo_root: str, lock_payload: dict) -> Dict[str, dict]:
    registry_hashes = dict(lock_payload.get("registries") or {})
    payloads: Dict[str, dict] = {}
    for hash_key, filename in sorted(REGISTRY_FILE_MAP.items(), key=lambda item: item[0]):
        payload = _read_json(os.path.join(repo_root, "build", "registries", filename))
        expected = str(registry_hashes.get(hash_key, "")).strip()
        actual = str(payload.get("registry_hash", "")).strip()
        if expected != actual:
            raise RuntimeError("registry hash mismatch for '{}'".format(filename))
        payloads[hash_key] = payload
    return payloads


def _select_law_profile(payloads: Dict[str, dict], law_profile_id: str) -> dict:
    rows = list((payloads.get("law_registry_hash") or {}).get("law_profiles") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("law_profile_id", ""))):
        if str(row.get("law_profile_id", "")).strip() == str(law_profile_id).strip():
            return dict(row)
    raise RuntimeError("law profile '{}' not found".format(law_profile_id))


def _select_lens_profile(payloads: Dict[str, dict], experience_id: str, law_profile: dict) -> dict:
    experience_rows = list((payloads.get("experience_registry_hash") or {}).get("experience_profiles") or [])
    default_lens_id = ""
    for row in sorted((item for item in experience_rows if isinstance(item, dict)), key=lambda item: str(item.get("experience_id", ""))):
        if str(row.get("experience_id", "")).strip() == str(experience_id).strip():
            default_lens_id = str(row.get("default_lens_id", "")).strip()
            break
    if not default_lens_id:
        allowed = sorted(
            set(str(item).strip() for item in (law_profile.get("allowed_lenses") or []) if str(item).strip())
        )
        if allowed:
            default_lens_id = allowed[0]
    if not default_lens_id:
        raise RuntimeError("unable to resolve lens for experience '{}'".format(experience_id))

    lens_rows = list((payloads.get("lens_registry_hash") or {}).get("lenses") or [])
    for row in sorted((item for item in lens_rows if isinstance(item, dict)), key=lambda item: str(item.get("lens_id", ""))):
        if str(row.get("lens_id", "")).strip() == default_lens_id:
            return dict(row)
    raise RuntimeError("lens '{}' not found".format(default_lens_id))


def _registry_payloads_for_runtime(payloads: Dict[str, dict]) -> Dict[str, dict]:
    return {
        "view_mode_registry": dict(payloads.get("view_mode_registry_hash") or {}),
        "render_proxy_registry": dict(payloads.get("render_proxy_registry_hash") or {}),
        "cosmetic_registry": dict(payloads.get("cosmetic_registry_hash") or {}),
        "cosmetic_policy_registry": dict(payloads.get("cosmetic_policy_registry_hash") or {}),
        "server_profile_registry": dict(payloads.get("server_profile_registry_hash") or {}),
        "net_server_policy_registry": dict(payloads.get("net_server_policy_registry_hash") or {}),
        "astronomy_catalog_index": dict(payloads.get("astronomy_catalog_index_hash") or {}),
        "site_registry_index": dict(payloads.get("site_registry_index_hash") or {}),
        "ephemeris_registry": dict(payloads.get("ephemeris_registry_hash") or {}),
        "terrain_tile_registry": dict(payloads.get("terrain_tile_registry_hash") or {}),
        "activation_policy_registry": dict(payloads.get("activation_policy_registry_hash") or {}),
        "budget_policy_registry": dict(payloads.get("budget_policy_registry_hash") or {}),
        "fidelity_policy_registry": dict(payloads.get("fidelity_policy_registry_hash") or {}),
        "perception_interest_policy_registry": dict(payloads.get("perception_interest_policy_registry_hash") or {}),
        "epistemic_policy_registry": dict(payloads.get("epistemic_policy_registry_hash") or {}),
        "retention_policy_registry": dict(payloads.get("retention_policy_registry_hash") or {}),
        "decay_model_registry": dict(payloads.get("decay_model_registry_hash") or {}),
        "eviction_rule_registry": dict(payloads.get("eviction_rule_registry_hash") or {}),
    }


def prepare_authoritative_runtime_fixture(
    repo_root: str,
    *,
    save_id: str,
    client_peer_id: str = "peer.client.alpha",
) -> Dict[str, object]:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_server_authoritative import initialize_authoritative_runtime
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
        rng_seed_string="seed.mp4.authoritative.fixture",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.mp4.authoritative.universe",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.inspect",
            "entitlement.teleport",
            "entitlement.camera_control",
            "entitlement.time_control",
            "entitlement.agent.move",
            "entitlement.agent.rotate",
            "ui.window.lab.nav",
            "lens.nondiegetic.access",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        net_endpoint="loopback://mp4.authoritative.fixture",
        net_transport_id="transport.loopback",
        net_client_peer_id=str(client_peer_id),
        net_server_peer_id="peer.server.authoritative",
        net_replication_policy_id="policy.net.server_authoritative",
        net_anti_cheat_policy_id="policy.ac.casual_default",
        net_server_policy_id="server.policy.private.default",
        net_securex_policy_id="",
        net_desired_law_profile_id="law.lab.unrestricted",
        net_schema_versions=[],
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        raise RuntimeError("create_session_spec refused")

    session_spec_path = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    session_spec = _read_json(session_spec_path)
    lock_payload = _read_json(os.path.join(repo_root, "build", "lockfile.json"))
    payloads = _load_lock_and_registries(repo_root, lock_payload)

    save_root = os.path.join(repo_root, "saves", str(save_id))
    universe_identity = _read_json(os.path.join(save_root, "universe_identity.json"))
    universe_state = _read_json(os.path.join(save_root, "universe_state.json"))
    authority_context = dict(session_spec.get("authority_context") or {})
    law_profile = _select_law_profile(payloads, str(authority_context.get("law_profile_id", "")))
    lens_profile = _select_lens_profile(payloads, str(session_spec.get("experience_id", "")), law_profile)
    initialized = initialize_authoritative_runtime(
        repo_root=repo_root,
        save_id=str(save_id),
        session_spec=session_spec,
        lock_payload=lock_payload,
        universe_identity=universe_identity,
        universe_state=universe_state,
        law_profile=law_profile,
        lens_profile=lens_profile,
        authority_context=authority_context,
        anti_cheat_policy_registry=dict(payloads.get("anti_cheat_policy_registry_hash") or {}),
        anti_cheat_module_registry=dict(payloads.get("anti_cheat_module_registry_hash") or {}),
        replication_policy_registry=dict(payloads.get("net_replication_policy_registry_hash") or {}),
        registry_payloads=_registry_payloads_for_runtime(payloads),
        snapshot_cadence_ticks=0,
    )
    if str(initialized.get("result", "")) != "complete":
        reason = str(((initialized.get("refusal") or {}).get("reason_code", "")) if isinstance(initialized, dict) else "")
        raise RuntimeError("initialize_authoritative_runtime refused ({})".format(reason))

    return {
        "session_spec": session_spec,
        "lock_payload": lock_payload,
        "payloads": payloads,
        "authority_context": authority_context,
        "law_profile": law_profile,
        "lens_profile": lens_profile,
        "runtime": dict(initialized.get("runtime") or {}),
    }


def clone_runtime(fixture: Dict[str, object]) -> dict:
    return copy.deepcopy(dict(fixture.get("runtime") or {}))
