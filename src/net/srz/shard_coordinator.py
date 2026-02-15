"""Deterministic SRZ hybrid shard coordinator (single-process multi-shard)."""

from __future__ import annotations

import copy
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import norm, refusal, write_canonical_json
from tools.xstack.sessionx.observation import build_truth_model, observe_truth
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.sessionx.srz import simulation_tick

from .routing import DEFAULT_SHARD_ID, route_intent_envelope, shard_index


PROCESS_SCOPE_BY_ID = {
    "process.region_management_tick": "region.state",
    "process.time_control_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.camera_teleport": "camera.transform",
    "process.camera_move": "camera.transform",
}

PROCESS_OWNER_OBJECT = {
    "process.region_management_tick": "camera.main",
    "process.time_control_set_rate": "camera.main",
    "process.time_pause": "camera.main",
    "process.time_resume": "camera.main",
    "process.camera_teleport": "camera.main",
    "process.camera_move": "camera.main",
}

PROCESS_PRIORITY = {
    "process.region_management_tick": 10,
    "process.time_control_set_rate": 20,
    "process.time_pause": 20,
    "process.time_resume": 20,
    "process.camera_teleport": 30,
    "process.camera_move": 40,
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_float(value: object, default_value: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _queue_sort_key(envelope: dict) -> Tuple[int, str, str, int, str]:
    return (
        _as_int(envelope.get("submission_tick", 0), 0),
        str(envelope.get("target_shard_id", "")),
        str(envelope.get("source_peer_id", "")),
        _as_int(envelope.get("deterministic_sequence_number", 0), 0),
        str(envelope.get("intent_id", "")),
    )


def _proposal_sort_key(proposal: dict) -> Tuple[int, str, str, str, int, str]:
    return (
        _as_int(proposal.get("priority", 0), 0),
        str(proposal.get("target_shard_id", "")),
        str(proposal.get("source_shard_id", "")),
        str(proposal.get("process_id", "")),
        _as_int(proposal.get("deterministic_sequence_number", 0), 0),
        str(proposal.get("envelope_id", "")),
    )


def _runtime_server(runtime: dict) -> dict:
    payload = runtime.get("server")
    if isinstance(payload, dict):
        return payload
    payload = {}
    runtime["server"] = payload
    return payload


def _runtime_clients(runtime: dict) -> dict:
    payload = runtime.get("clients")
    if isinstance(payload, dict):
        return payload
    payload = {}
    runtime["clients"] = payload
    return payload


def _runtime_shards(runtime: dict) -> List[dict]:
    rows = runtime.get("shards")
    if not isinstance(rows, list):
        rows = []
        runtime["shards"] = rows
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(row)
    return sorted(
        out,
        key=lambda item: (
            _as_int(item.get("priority", 0), 0),
            str(item.get("shard_id", "")),
        ),
    )


def _registry_hashes(lock_payload: dict) -> dict:
    rows = lock_payload.get("registries")
    if not isinstance(rows, dict):
        return {}
    out = {}
    for key in sorted(rows.keys()):
        token = str(rows.get(key, "")).strip()
        if token:
            out[str(key)] = token
    return out


def _runtime_paths(runtime: dict) -> Tuple[str, str]:
    repo_root = str(runtime.get("repo_root", "")).strip()
    artifacts_rel = str(runtime.get("artifacts_rel", "")).strip()
    artifacts_abs = os.path.join(repo_root, artifacts_rel.replace("/", os.sep))
    if not os.path.isdir(artifacts_abs):
        os.makedirs(artifacts_abs, exist_ok=True)
    return repo_root, artifacts_abs


def _write_runtime_artifact(runtime: dict, rel_path: str, payload: dict) -> str:
    repo_root, artifacts_abs = _runtime_paths(runtime)
    abs_path = os.path.join(artifacts_abs, rel_path.replace("/", os.sep))
    write_canonical_json(abs_path, payload)
    return norm(os.path.relpath(abs_path, repo_root))


def _policy_row(registry_payload: dict, policy_id: str, key: str = "policies") -> dict:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {}


def _shard_map_row(registry_payload: dict, shard_map_id: str) -> dict:
    rows = registry_payload.get("shard_maps")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("shard_map_id", ""))):
        if str(row.get("shard_map_id", "")).strip() == str(shard_map_id).strip():
            return dict(row)
    return {}


def _module_registry_map(module_registry_payload: dict) -> Dict[str, dict]:
    rows = module_registry_payload.get("modules")
    if not isinstance(rows, list):
        return {}
    out = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("module_id", ""))):
        token = str(row.get("module_id", "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _perception_policy(runtime: dict) -> dict:
    payload = runtime.get("perception_interest_policy")
    if isinstance(payload, dict):
        return payload
    return {}


def _perception_limit(policy: dict, lens_type: str) -> int:
    max_objects = max(1, _as_int(policy.get("max_objects_per_tick", 1), 1))
    multiplier = 1.0
    rows = policy.get("lens_visibility_rules")
    if isinstance(rows, list):
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("lens_type", ""))):
            if str(row.get("lens_type", "")).strip() != str(lens_type).strip():
                continue
            multiplier = max(0.1, _as_float(row.get("max_objects_multiplier", 1.0), 1.0))
            break
    return max(1, int(round(float(max_objects) * float(multiplier))))


def _distance_bands(policy: dict) -> List[dict]:
    rows = policy.get("distance_bands")
    if not isinstance(rows, list):
        return []
    out = [dict(row) for row in rows if isinstance(row, dict)]
    return sorted(out, key=lambda row: (_as_float(row.get("max_distance", 0.0), 0.0), str(row.get("band_id", ""))))


def _interest_sort_key(token: str, band_rows: List[dict]) -> Tuple[int, str]:
    if not band_rows:
        return (0, str(token))
    digest = canonical_sha256({"object_id": str(token)})
    bucket = int(digest[:8], 16) % max(1, len(band_rows))
    return (int(bucket), str(token))


def _filter_perceived_model(perceived_model: dict, policy: dict) -> dict:
    out = copy.deepcopy(dict(perceived_model or {}))
    observed = _sorted_tokens(list(out.get("observed_entities") or []))
    lens_type = str(((out.get("metadata") or {}).get("lens_type", ""))).strip()
    limit = _perception_limit(policy=policy, lens_type=lens_type)
    bands = _distance_bands(policy=policy)
    observed_sorted = sorted(observed, key=lambda token: _interest_sort_key(token, bands))
    selected_entities = observed_sorted[:limit]
    selected_set = set(selected_entities)
    out["observed_entities"] = list(selected_entities)

    navigation = out.get("navigation")
    if isinstance(navigation, dict):
        hierarchy = navigation.get("hierarchy")
        if isinstance(hierarchy, list):
            filtered = []
            for row in hierarchy:
                if not isinstance(row, dict):
                    continue
                object_id = str(row.get("object_id", "")).strip()
                parent_id = str(row.get("parent_id", "")).strip()
                if object_id in selected_set or parent_id in selected_set:
                    filtered.append(dict(row))
            navigation["hierarchy"] = sorted(
                filtered,
                key=lambda row: (
                    str(row.get("kind", "")),
                    str(row.get("object_id", "")),
                ),
            )
        out["navigation"] = navigation

    sites = out.get("sites")
    if isinstance(sites, dict):
        rows = sites.get("entries")
        if isinstance(rows, list):
            filtered_sites = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if str(row.get("object_id", "")).strip() in selected_set:
                    filtered_sites.append(dict(row))
            sites["entries"] = sorted(
                filtered_sites,
                key=lambda row: (
                    str(row.get("object_id", "")),
                    str(row.get("site_id", "")),
                ),
            )
        out["sites"] = sites

    interest = {
        "policy_id": str(policy.get("policy_id", "")),
        "ordering_rule_id": str(policy.get("deterministic_ordering_rule_id", "")),
        "selected_count": int(len(selected_entities)),
        "max_objects": int(limit),
    }
    metadata = dict(out.get("metadata") or {})
    metadata["network_interest"] = interest
    out["metadata"] = metadata
    return out


def _truth_model(runtime: dict, state: dict) -> dict:
    return build_truth_model(
        universe_identity=dict(runtime.get("universe_identity") or {}),
        universe_state=dict(state),
        lockfile_payload=dict(runtime.get("lock_payload") or {}),
        identity_path=str(runtime.get("identity_ref", "")),
        state_path=str(runtime.get("state_ref", "")),
        registry_payloads=dict(runtime.get("registry_payloads") or {}),
    )


def _derive_perceived_for_peer(runtime: dict, peer_id: str) -> Dict[str, object]:
    clients = _runtime_clients(runtime)
    client = dict(clients.get(str(peer_id)) or {})
    if not client:
        return refusal(
            "refusal.net.authority_violation",
            "peer '{}' is not joined to SRZ hybrid runtime".format(str(peer_id)),
            "Join peer before requesting perceived deltas.",
            {"peer_id": str(peer_id)},
            "$.peer_id",
        )
    state = dict(runtime.get("global_state") or {})
    observed = observe_truth(
        truth_model=_truth_model(runtime=runtime, state=state),
        lens=dict(client.get("lens_profile") or {}),
        law_profile=dict(client.get("law_profile") or {}),
        authority_context=dict(client.get("authority_context") or {}),
        viewpoint_id="viewpoint.client.{}".format(str(peer_id)),
        memory_state=dict(client.get("memory_state") or {}),
    )
    if str(observed.get("result", "")) != "complete":
        return observed
    policy = _perception_policy(runtime=runtime)
    if not policy:
        return refusal(
            "refusal.net.perception_policy_missing",
            "SRZ hybrid runtime is missing perception-interest policy",
            "Configure server policy extensions.perception_interest_policy_id and rebuild registries.",
            {"policy_id": "<missing>"},
            "$.perception_interest_policy",
        )
    perceived = _filter_perceived_model(
        perceived_model=dict(observed.get("perceived_model") or {}),
        policy=policy,
    )
    return {
        "result": "complete",
        "perceived_model": perceived,
        "perceived_hash": canonical_sha256(perceived),
        "memory_state": dict(observed.get("memory_state") or {}),
        "epistemic_policy_id": str(observed.get("epistemic_policy_id", "")),
        "retention_policy_id": str(observed.get("retention_policy_id", "")),
    }


def _entity_owner_shard(shard_map: dict, entity_id: str) -> str:
    index = shard_index(shard_map)
    owner = str((index.get("object_owner") or {}).get(str(entity_id).strip(), "")).strip()
    if owner:
        return owner
    shard_ids = list(index.get("shard_ids") or [])
    if DEFAULT_SHARD_ID in shard_ids:
        return DEFAULT_SHARD_ID
    if shard_ids:
        return str(shard_ids[0])
    return DEFAULT_SHARD_ID


def _register_client(runtime: dict, peer_id: str, authority_context: dict, law_profile: dict, lens_profile: dict) -> None:
    clients = _runtime_clients(runtime)
    token = str(peer_id).strip()
    if not token:
        return
    clients[token] = {
        "peer_id": token,
        "authority_context": copy.deepcopy(authority_context if isinstance(authority_context, dict) else {}),
        "law_profile": copy.deepcopy(law_profile if isinstance(law_profile, dict) else {}),
        "lens_profile": copy.deepcopy(lens_profile if isinstance(lens_profile, dict) else {}),
        "last_perceived_model": {},
        "last_perceived_hash": "",
        "memory_state": {},
        "last_applied_tick": int((_runtime_server(runtime).get("network_tick", 0) or 0)),
        "joined": True,
        "received_delta_ids": [],
        "resync_count": 0,
    }
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))


def initialize_hybrid_runtime(
    repo_root: str,
    save_id: str,
    session_spec: dict,
    lock_payload: dict,
    universe_identity: dict,
    universe_state: dict,
    law_profile: dict,
    lens_profile: dict,
    authority_context: dict,
    anti_cheat_policy_registry: dict,
    anti_cheat_module_registry: dict,
    replication_policy_registry: dict,
    server_policy_registry: dict,
    shard_map_registry: dict,
    perception_interest_policy_registry: dict,
    registry_payloads: dict | None = None,
) -> Dict[str, object]:
    network = dict(session_spec.get("network") or {})
    if not network:
        return refusal(
            "refusal.net.join_policy_mismatch",
            "SRZ hybrid runtime requires SessionSpec.network payload",
            "Provide SessionSpec.network fields before initializing multiplayer runtime.",
            {"schema_id": "session_spec"},
            "$.network",
        )
    requested_policy = str(network.get("requested_replication_policy_id", "")).strip()
    if requested_policy != "policy.net.srz_hybrid":
        return refusal(
            "refusal.net.join_policy_mismatch",
            "SessionSpec requested replication policy '{}' is not srz_hybrid".format(requested_policy or "<empty>"),
            "Set requested_replication_policy_id to policy.net.srz_hybrid.",
            {"requested_replication_policy_id": requested_policy or "<empty>"},
            "$.network.requested_replication_policy_id",
        )

    replication_policy = _policy_row(replication_policy_registry, requested_policy)
    if not replication_policy:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "replication policy '{}' is not available in compiled registry".format(requested_policy),
            "Rebuild net_replication_policy.registry and retry.",
            {"policy_id": requested_policy},
            "$.network.requested_replication_policy_id",
        )

    anti_cheat_policy_id = str(network.get("anti_cheat_policy_id", "")).strip()
    anti_cheat_policy = _policy_row(anti_cheat_policy_registry, anti_cheat_policy_id)
    if not anti_cheat_policy:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "anti-cheat policy '{}' is not available in compiled registry".format(anti_cheat_policy_id or "<empty>"),
            "Select anti_cheat_policy_id from anti_cheat_policy.registry.json.",
            {"anti_cheat_policy_id": anti_cheat_policy_id or "<empty>"},
            "$.network.anti_cheat_policy_id",
        )

    module_map = _module_registry_map(anti_cheat_module_registry)
    missing_modules = [
        token
        for token in _sorted_tokens(list(anti_cheat_policy.get("modules_enabled") or []))
        if token not in module_map
    ]
    if missing_modules:
        return refusal(
            "refusal.ac.policy_violation",
            "anti-cheat policy references missing modules",
            "Rebuild anti-cheat module registry and retry runtime initialization.",
            {"missing_module_ids": ",".join(missing_modules)},
            "$.network.anti_cheat_policy_id",
        )

    server_policy_id = str(network.get("server_policy_id", "")).strip()
    server_policy = _policy_row(server_policy_registry, server_policy_id)
    if not server_policy:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "server policy '{}' is not available in compiled registry".format(server_policy_id or "<empty>"),
            "Select a server_policy_id from net_server_policy.registry.json.",
            {"server_policy_id": server_policy_id or "<empty>"},
            "$.network.server_policy_id",
        )
    allowed_replication = _sorted_tokens(list(server_policy.get("allowed_replication_policy_ids") or []))
    if requested_policy not in allowed_replication:
        return refusal(
            "refusal.net.handshake_policy_not_allowed",
            "server policy does not allow replication policy '{}'".format(requested_policy),
            "Use a server policy that allows policy.net.srz_hybrid.",
            {"server_policy_id": server_policy_id, "policy_id": requested_policy},
            "$.network.server_policy_id",
        )

    server_ext = dict(server_policy.get("extensions") or {})
    shard_map_id = str(server_ext.get("default_shard_map_id", "shard_map.default.single_shard")).strip() or "shard_map.default.single_shard"
    shard_map = _shard_map_row(shard_map_registry, shard_map_id)
    if not shard_map:
        return refusal(
            "refusal.net.shard_target_invalid",
            "server policy references missing shard_map_id '{}'".format(shard_map_id),
            "Add shard map to shard_map.registry or update server policy extensions.",
            {"server_policy_id": server_policy_id, "shard_map_id": shard_map_id},
            "$.network.server_policy_id",
        )

    perception_policy_id = str(server_ext.get("perception_interest_policy_id", "")).strip()
    if not perception_policy_id:
        return refusal(
            "refusal.net.perception_policy_missing",
            "server policy is missing perception_interest_policy_id extension",
            "Set extensions.perception_interest_policy_id on the selected server policy.",
            {"server_policy_id": server_policy_id},
            "$.network.server_policy_id",
        )
    perception_policy = _policy_row(perception_interest_policy_registry, perception_policy_id)
    if not perception_policy:
        return refusal(
            "refusal.net.perception_policy_missing",
            "perception interest policy '{}' is not available in compiled registry".format(perception_policy_id),
            "Rebuild perception_interest_policy.registry and retry runtime initialization.",
            {"policy_id": perception_policy_id},
            "$.perception_interest_policy",
        )

    shard_rows = []
    for row in sorted((shard_map.get("shards") or []), key=lambda item: (_as_int((item or {}).get("priority", 0), 0), str((item or {}).get("shard_id", "")))):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).strip()
        if status != "active":
            continue
        region_scope = row.get("region_scope")
        if not isinstance(region_scope, dict):
            region_scope = {"object_ids": [], "spatial_bounds": None}
        shard_rows.append(
            {
                "shard_id": str(row.get("shard_id", "")),
                "priority": int(_as_int(row.get("priority", 0), 0)),
                "status": status,
                "authority_endpoint": str(row.get("authority_endpoint", "")),
                "region_scope": {
                    "object_ids": _sorted_tokens(list(region_scope.get("object_ids") or [])),
                    "spatial_bounds": region_scope.get("spatial_bounds"),
                },
                "owned_entities": _sorted_tokens(list(region_scope.get("object_ids") or [])),
                "owned_regions": [],
                "process_queue": [],
                "last_hash_anchor": "0" * 64,
            }
        )
    if not shard_rows:
        return refusal(
            "refusal.net.shard_target_invalid",
            "selected shard map does not define active shards",
            "Activate at least one shard in shard_map registry.",
            {"shard_map_id": shard_map_id},
            "$.shard_map.shards",
        )

    registry_hashes = _registry_hashes(lock_payload)
    artifacts_rel = norm(os.path.join("build", "net", "srz_hybrid", str(save_id)))
    runtime = {
        "schema_version": "1.0.0",
        "policy_id": "policy.net.srz_hybrid",
        "repo_root": norm(repo_root),
        "save_id": str(save_id),
        "artifacts_rel": artifacts_rel,
        "session_spec": copy.deepcopy(session_spec if isinstance(session_spec, dict) else {}),
        "lock_payload": copy.deepcopy(lock_payload if isinstance(lock_payload, dict) else {}),
        "registry_payloads": copy.deepcopy(registry_payloads if isinstance(registry_payloads, dict) else {}),
        "universe_identity": copy.deepcopy(universe_identity if isinstance(universe_identity, dict) else {}),
        "identity_ref": norm(os.path.join("saves", str(save_id), "universe_identity.json")),
        "state_ref": norm(os.path.join("saves", str(save_id), "universe_state.json")),
        "global_state": copy.deepcopy(universe_state if isinstance(universe_state, dict) else {}),
        "shard_map_id": shard_map_id,
        "shard_map": shard_map,
        "perception_interest_policy": perception_policy,
        "anti_cheat": {
            "policy_id": anti_cheat_policy_id,
            "modules_enabled": _sorted_tokens(list(anti_cheat_policy.get("modules_enabled") or [])),
            "default_actions": dict(anti_cheat_policy.get("default_actions") or {}),
            "module_registry_map": module_map,
        },
        "server": {
            "peer_id": str(network.get("server_peer_id", "")).strip(),
            "network_tick": max(0, simulation_tick(dict(universe_state or {}))),
            "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
            "registry_hashes": registry_hashes,
            "queued_envelopes": [],
            "last_sequence_by_peer": {},
            "seen_envelope_ids": [],
            "last_tick_hash": "",
            "last_composite_hash": "0" * 64,
            "hash_anchor_frames": [],
            "snapshots": [],
            "baseline_snapshot_id": "",
            "baseline_snapshot_ids": [],
            "perceived_deltas": [],
            "refusals": [],
        },
        "shards": shard_rows,
        "clients": {},
    }

    initial_peer_id = str(network.get("client_peer_id", "")).strip()
    _register_client(
        runtime=runtime,
        peer_id=initial_peer_id,
        authority_context=authority_context,
        law_profile=law_profile,
        lens_profile=lens_profile,
    )
    return {
        "result": "complete",
        "runtime": runtime,
        "shard_map_id": shard_map_id,
        "perception_interest_policy_id": perception_policy_id,
        "initial_peer_id": initial_peer_id,
    }


def build_client_intent_envelope(
    runtime: dict,
    peer_id: str,
    intent_id: str,
    process_id: str,
    inputs: dict,
    submission_tick: int | None = None,
    target_shard_id: str = "auto",
) -> Dict[str, object]:
    server = _runtime_server(runtime)
    next_sequence = _as_int((server.get("last_sequence_by_peer") or {}).get(str(peer_id), 0), 0) + 1
    target_tick = _as_int(submission_tick if submission_tick is not None else server.get("network_tick", 0), 0) + (
        0 if submission_tick is not None else 1
    )
    clients = _runtime_clients(runtime)
    client_entry = dict(clients.get(str(peer_id)) or {})
    authority_context = dict(client_entry.get("authority_context") or {})
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": "env.{}.tick.{}.seq.{}".format(str(peer_id), int(target_tick), str(next_sequence).zfill(4)),
        "authority_summary": {
            "authority_origin": str(authority_context.get("authority_origin", "client")),
            "law_profile_id": str((client_entry.get("law_profile") or {}).get("law_profile_id", "")),
        },
        "source_peer_id": str(peer_id),
        "source_shard_id": DEFAULT_SHARD_ID,
        "target_shard_id": str(target_shard_id or "auto"),
        "submission_tick": int(max(0, target_tick)),
        "deterministic_sequence_number": int(max(0, next_sequence)),
        "intent_id": str(intent_id),
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": str(process_id),
            "inputs": dict(inputs if isinstance(inputs, dict) else {}),
        },
        "pack_lock_hash": str(server.get("pack_lock_hash", "")),
        "registry_hashes": dict(server.get("registry_hashes") or {}),
        "signature": "",
        "extensions": {},
    }
    return {"result": "complete", "envelope": envelope}


def queue_intent_envelope(repo_root: str, runtime: dict, envelope: dict) -> Dict[str, object]:
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_intent_envelope",
        payload=dict(envelope if isinstance(envelope, dict) else {}),
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return refusal(
            "refusal.net.envelope_invalid",
            "intent envelope failed net_intent_envelope schema validation",
            "Fix envelope fields and retry submission.",
            {"schema_id": "net_intent_envelope"},
            "$.intent_envelope",
        )

    server = _runtime_server(runtime)
    peer_id = str(envelope.get("source_peer_id", "")).strip()
    clients = _runtime_clients(runtime)
    if peer_id not in clients:
        return refusal(
            "refusal.net.authority_violation",
            "source peer is not joined to SRZ hybrid runtime",
            "Join peer via baseline sync before submitting intents.",
            {"peer_id": peer_id or "<empty>"},
            "$.source_peer_id",
        )

    expected_pack_lock = str(server.get("pack_lock_hash", "")).strip()
    if str(envelope.get("pack_lock_hash", "")).strip() != expected_pack_lock:
        return refusal(
            "refusal.net.handshake_pack_lock_mismatch",
            "intent envelope pack_lock_hash does not match server lock hash",
            "Reconnect using matching bundle lockfile and retry intent submission.",
            {"peer_id": peer_id},
            "$.pack_lock_hash",
        )

    seen = _sorted_tokens(list(server.get("seen_envelope_ids") or []))
    envelope_id = str(envelope.get("envelope_id", "")).strip()
    if envelope_id in seen:
        return refusal(
            "refusal.net.replay_detected",
            "intent envelope replay detected",
            "Generate a new deterministic envelope sequence and retry submission.",
            {"envelope_id": envelope_id},
            "$.envelope_id",
        )

    sequence = _as_int(envelope.get("deterministic_sequence_number", 0), 0)
    last_seq_map = dict(server.get("last_sequence_by_peer") or {})
    expected_next = _as_int(last_seq_map.get(peer_id, 0), 0) + 1
    if sequence != expected_next:
        return refusal(
            "refusal.net.sequence_violation",
            "deterministic_sequence_number is out of order for peer '{}'".format(peer_id),
            "Submit envelopes with monotonic deterministic_sequence_number values.",
            {"peer_id": peer_id, "expected_sequence": str(expected_next), "actual_sequence": str(sequence)},
            "$.deterministic_sequence_number",
        )

    site_registry = dict((runtime.get("registry_payloads") or {}).get("site_registry_index") or {})
    routed = route_intent_envelope(
        envelope=dict(envelope),
        shard_map=dict(runtime.get("shard_map") or {}),
        site_registry=site_registry,
    )
    if str(routed.get("result", "")) != "complete":
        return routed

    shard_ids = _sorted_tokens([str(row.get("shard_id", "")) for row in _runtime_shards(runtime)])
    queued = list(server.get("queued_envelopes") or [])
    queued_ids = []
    for routed_envelope in sorted((dict(row) for row in (routed.get("routed_envelopes") or []) if isinstance(row, dict)), key=_queue_sort_key):
        target = str(routed_envelope.get("target_shard_id", "")).strip()
        if target not in shard_ids:
            return refusal(
                "refusal.net.shard_target_invalid",
                "routed envelope target_shard_id '{}' is not active".format(target or "<empty>"),
                "Route to an active shard declared by shard_map registry.",
                {"target_shard_id": target or "<empty>"},
                "$.target_shard_id",
            )
        queued.append(routed_envelope)
        queued_ids.append(str(routed_envelope.get("envelope_id", "")))

    seen.extend(queued_ids)
    server["queued_envelopes"] = sorted((dict(row) for row in queued if isinstance(row, dict)), key=_queue_sort_key)
    server["seen_envelope_ids"] = _sorted_tokens(seen)
    last_seq_map[peer_id] = int(sequence)
    server["last_sequence_by_peer"] = dict((key, int(last_seq_map[key])) for key in sorted(last_seq_map.keys()))
    runtime["server"] = server
    return {
        "result": "complete",
        "queued_envelope_ids": queued_ids,
    }


def _build_proposal(runtime: dict, envelope: dict, tick: int) -> Dict[str, object]:
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        return refusal(
            "refusal.net.envelope_invalid",
            "intent envelope payload must be an object",
            "Encode envelope payload as object with process_id and inputs fields.",
            {"envelope_id": str(envelope.get("envelope_id", ""))},
            "$.payload",
        )
    process_id = str(payload.get("process_id", "")).strip()
    inputs = payload.get("inputs")
    if not process_id or not isinstance(inputs, dict):
        return refusal(
            "refusal.net.envelope_invalid",
            "intent envelope payload must include process_id and inputs",
            "Fix envelope payload shape and retry submission.",
            {"envelope_id": str(envelope.get("envelope_id", ""))},
            "$.payload",
        )
    target_shard_id = str(envelope.get("target_shard_id", "")).strip()
    source_shard_id = str(envelope.get("source_shard_id", DEFAULT_SHARD_ID)).strip() or DEFAULT_SHARD_ID
    owner_object_id = str(PROCESS_OWNER_OBJECT.get(process_id, "camera.main"))
    owner_shard_id = _entity_owner_shard(dict(runtime.get("shard_map") or {}), owner_object_id)
    if owner_shard_id != target_shard_id:
        return refusal(
            "refusal.net.cross_shard_unsupported",
            "process '{}' owner '{}' resolves to shard '{}' but routed envelope targets '{}'".format(
                process_id,
                owner_object_id,
                owner_shard_id,
                target_shard_id or "<empty>",
            ),
            "Use deterministic routing so process owner and target shard match, or implement declared cross-shard process metadata.",
            {
                "process_id": process_id,
                "owner_object_id": owner_object_id,
                "owner_shard_id": owner_shard_id,
                "target_shard_id": target_shard_id or "<empty>",
            },
            "$.target_shard_id",
        )
    return {
        "result": "complete",
        "proposal": {
            "tick": int(tick),
            "envelope_id": str(envelope.get("envelope_id", "")),
            "parent_envelope_id": str(((envelope.get("extensions") or {}).get("parent_envelope_id", ""))),
            "intent_id": str(envelope.get("intent_id", "")),
            "process_id": process_id,
            "inputs": dict(inputs),
            "target_shard_id": target_shard_id,
            "source_shard_id": source_shard_id,
            "source_peer_id": str(envelope.get("source_peer_id", "")),
            "deterministic_sequence_number": _as_int(envelope.get("deterministic_sequence_number", 0), 0),
            "scope_key": "{}::{}".format(owner_object_id, str(PROCESS_SCOPE_BY_ID.get(process_id, "generic"))),
            "priority": _as_int(PROCESS_PRIORITY.get(process_id, 1000), 1000),
        },
    }


def _record_refusal(runtime: dict, tick: int, envelope_id: str, peer_id: str, refusal_payload: dict) -> None:
    server = _runtime_server(runtime)
    rows = list(server.get("refusals") or [])
    rows.append(
        {
            "tick": int(tick),
            "peer_id": str(peer_id),
            "envelope_id": str(envelope_id),
            "reason_code": str((refusal_payload or {}).get("reason_code", "")),
        }
    )
    server["refusals"] = sorted(
        rows,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("peer_id", "")),
            str(row.get("envelope_id", "")),
            str(row.get("reason_code", "")),
        ),
    )
    runtime["server"] = server


def _resolve_proposals(proposals: List[dict]) -> List[dict]:
    ordered = sorted((dict(row) for row in proposals if isinstance(row, dict)), key=_proposal_sort_key)
    chosen: List[dict] = []
    seen_scopes = set()
    for row in ordered:
        scope_key = str(row.get("scope_key", ""))
        if scope_key in seen_scopes:
            continue
        seen_scopes.add(scope_key)
        chosen.append(row)
    return chosen


def _state_tick_hash(runtime: dict, tick: int) -> str:
    server = _runtime_server(runtime)
    payload = {
        "tick": int(tick),
        "state_hash": canonical_sha256(dict(runtime.get("global_state") or {})),
        "pack_lock_hash": str(server.get("pack_lock_hash", "")),
        "registry_hashes": dict(server.get("registry_hashes") or {}),
        "previous_composite_hash": str(server.get("last_composite_hash", "0" * 64)),
    }
    return canonical_sha256(payload)


def _build_anchor_frame(repo_root: str, runtime: dict, tick: int) -> Dict[str, object]:
    state_tick_hash = _state_tick_hash(runtime=runtime, tick=tick)
    shard_rows = _runtime_shards(runtime)
    shard_hashes = []
    for shard in shard_rows:
        shard_id = str(shard.get("shard_id", ""))
        shard_hash = canonical_sha256(
            {
                "tick": int(tick),
                "state_tick_hash": state_tick_hash,
                "shard_id": shard_id,
                "owned_entities": _sorted_tokens(list(shard.get("owned_entities") or [])),
                "owned_regions": _sorted_tokens(list(shard.get("owned_regions") or [])),
            }
        )
        shard["last_hash_anchor"] = shard_hash
        shard_hashes.append({"shard_id": shard_id, "hash": shard_hash})
    runtime["shards"] = sorted(shard_rows, key=lambda item: (_as_int(item.get("priority", 0), 0), str(item.get("shard_id", ""))))

    server = _runtime_server(runtime)
    previous = str(server.get("last_composite_hash", "0" * 64)).strip() or ("0" * 64)
    composite_hash = canonical_sha256({"tick": int(tick), "state_tick_hash": state_tick_hash, "previous_composite_hash": previous})
    frame = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "shard_hashes": sorted(shard_hashes, key=lambda row: str(row.get("shard_id", ""))),
        "composite_hash": composite_hash,
        "previous_composite_hash": previous,
        "checkpoint_id": "",
        "extensions": {
            "state_tick_hash": state_tick_hash,
        },
    }
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_hash_anchor_frame",
        payload=frame,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return refusal(
            "refusal.net.envelope_invalid",
            "generated hash_anchor_frame failed schema validation",
            "Fix SRZ hash anchor payload generation and retry.",
            {"schema_id": "net_hash_anchor_frame"},
            "$.hash_anchor_frame",
        )
    server["last_tick_hash"] = state_tick_hash
    server["last_composite_hash"] = composite_hash
    rows = list(server.get("hash_anchor_frames") or [])
    rows.append(frame)
    server["hash_anchor_frames"] = sorted(rows, key=lambda row: int(row.get("tick", 0) or 0))
    runtime["server"] = server
    return {"result": "complete", "frame": frame}


def _snapshot_for_tick(repo_root: str, runtime: dict, tick: int) -> Dict[str, object]:
    server = _runtime_server(runtime)
    registry_hashes = dict(server.get("registry_hashes") or {})
    snapshots = []
    for shard in _runtime_shards(runtime):
        shard_id = str(shard.get("shard_id", "")).strip()
        snapshot_payload = {
            "schema_version": "1.0.0",
            "tick": int(tick),
            "shard_id": shard_id,
            "state": dict(runtime.get("global_state") or {}),
        }
        payload_ref = _write_runtime_artifact(
            runtime=runtime,
            rel_path=norm(os.path.join("snapshots", shard_id, "tick.{}.json".format(int(tick)))),
            payload=snapshot_payload,
        )
        snapshot = {
            "schema_version": "1.0.0",
            "snapshot_id": "snapshot.{}.tick.{}".format(shard_id, int(tick)),
            "tick": int(tick),
            "shard_id": shard_id,
            "pack_lock_hash": str(server.get("pack_lock_hash", "")),
            "registry_hashes": registry_hashes,
            "truth_snapshot_hash": canonical_sha256(snapshot_payload),
            "payload_ref": payload_ref,
            "schema_versions": {"session_spec": "1.0.0"},
            "extensions": {"snapshot_payload_hash": canonical_sha256(snapshot_payload)},
        }
        checked = validate_instance(
            repo_root=repo_root,
            schema_name="net_snapshot",
            payload=snapshot,
            strict_top_level=True,
        )
        if not bool(checked.get("valid", False)):
            return refusal(
                "refusal.net.envelope_invalid",
                "generated net snapshot failed schema validation",
                "Fix snapshot payload generation and retry.",
                {"schema_id": "net_snapshot", "shard_id": shard_id},
                "$.snapshot",
            )
        snapshots.append(snapshot)

    rows = list(server.get("snapshots") or [])
    rows.extend(snapshots)
    server["snapshots"] = sorted(
        rows,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("shard_id", "")),
            str(row.get("snapshot_id", "")),
        ),
    )
    runtime["server"] = server
    return {"result": "complete", "snapshots": snapshots}


def _apply_delta(client_entry: dict, delta_payload: dict, expected_hash: str) -> Dict[str, object]:
    replace_payload = delta_payload.get("replace")
    if not isinstance(replace_payload, dict):
        return refusal(
            "refusal.net.resync_required",
            "perceived delta payload is missing replace object",
            "Request hybrid snapshot resync and retry.",
            {"field": "replace"},
            "$.perceived_delta",
        )
    next_model = dict(replace_payload)
    actual_hash = canonical_sha256(next_model)
    if str(expected_hash).strip() != actual_hash:
        return refusal(
            "refusal.net.resync_required",
            "perceived delta hash mismatch detected",
            "Request hybrid snapshot resync before continuing.",
            {"expected_hash": str(expected_hash), "actual_hash": actual_hash},
            "$.perceived_delta.perceived_hash",
        )
    client_entry["last_perceived_model"] = next_model
    client_entry["last_perceived_hash"] = actual_hash
    return {"result": "complete"}


def _emit_client_deltas(repo_root: str, runtime: dict, tick: int) -> Dict[str, object]:
    server = _runtime_server(runtime)
    clients = _runtime_clients(runtime)
    delta_rows = []
    for peer_id in sorted(clients.keys()):
        observed = _derive_perceived_for_peer(runtime=runtime, peer_id=peer_id)
        if str(observed.get("result", "")) != "complete":
            return observed
        client = dict(clients.get(peer_id) or {})
        perceived_model = dict(observed.get("perceived_model") or {})
        perceived_hash = str(observed.get("perceived_hash", ""))
        client["memory_state"] = dict(observed.get("memory_state") or {})
        delta_payload = {
            "schema_version": "1.0.0",
            "perceived_delta_id": "pdelta.{}.tick.{}".format(peer_id, int(tick)),
            "tick": int(tick),
            "replace": perceived_model,
            "previous_hash": str(client.get("last_perceived_hash", "")),
            "extensions": {},
        }
        delta_ref = _write_runtime_artifact(
            runtime=runtime,
            rel_path=norm(os.path.join("deltas", peer_id, "tick.{}.json".format(int(tick)))),
            payload=delta_payload,
        )
        epistemic_scope = dict(perceived_model.get("epistemic_scope") or {})
        delta_meta = {
            "schema_version": "1.0.0",
            "perceived_delta_id": str(delta_payload.get("perceived_delta_id", "")),
            "tick": int(tick),
            "peer_id": peer_id,
            "lens_id": str(perceived_model.get("lens_id", "")) or "lens.diegetic.sensor",
            "epistemic_scope_id": str(epistemic_scope.get("scope_id", "")) or "epistemic.unknown",
            "payload_ref": delta_ref,
            "perceived_hash": perceived_hash,
            "extensions": {
                "delta_hash": canonical_sha256(delta_payload),
                "epistemic_policy_id": str(observed.get("epistemic_policy_id", "")),
                "retention_policy_id": str(observed.get("retention_policy_id", "")),
            },
        }
        checked = validate_instance(
            repo_root=repo_root,
            schema_name="net_perceived_delta",
            payload=delta_meta,
            strict_top_level=True,
        )
        if not bool(checked.get("valid", False)):
            return refusal(
                "refusal.net.envelope_invalid",
                "perceived_delta artifact failed schema validation",
                "Fix net_perceived_delta payload generation and retry.",
                {"schema_id": "net_perceived_delta", "peer_id": peer_id},
                "$.perceived_delta",
            )
        applied = _apply_delta(client_entry=client, delta_payload=delta_payload, expected_hash=perceived_hash)
        if str(applied.get("result", "")) != "complete":
            return applied
        client["last_applied_tick"] = int(tick)
        client["received_delta_ids"] = _sorted_tokens(list(client.get("received_delta_ids") or []) + [str(delta_meta.get("perceived_delta_id", ""))])
        clients[peer_id] = client
        delta_rows.append(delta_meta)

    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    existing = list(server.get("perceived_deltas") or [])
    existing.extend(delta_rows)
    server["perceived_deltas"] = sorted(
        existing,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("peer_id", "")),
            str(row.get("perceived_delta_id", "")),
        ),
    )
    runtime["server"] = server
    return {"result": "complete", "perceived_deltas": delta_rows}


def advance_hybrid_tick(repo_root: str, runtime: dict) -> Dict[str, object]:
    server = _runtime_server(runtime)
    tick = _as_int(server.get("network_tick", 0), 0) + 1
    queued = list(server.get("queued_envelopes") or [])
    ready = [dict(row) for row in queued if isinstance(row, dict) and _as_int(row.get("submission_tick", 0), 0) <= int(tick)]
    pending = [dict(row) for row in queued if isinstance(row, dict) and _as_int(row.get("submission_tick", 0), 0) > int(tick)]
    ready = sorted(ready, key=_queue_sort_key)

    proposals = []
    processed = []
    for envelope in ready:
        built = _build_proposal(runtime=runtime, envelope=envelope, tick=int(tick))
        if str(built.get("result", "")) != "complete":
            refusal_payload = dict(built.get("refusal") or {})
            processed.append(
                {
                    "envelope_id": str(envelope.get("envelope_id", "")),
                    "peer_id": str(envelope.get("source_peer_id", "")),
                    "result": "refused",
                    "refusal": refusal_payload,
                }
            )
            _record_refusal(
                runtime=runtime,
                tick=int(tick),
                envelope_id=str(envelope.get("envelope_id", "")),
                peer_id=str(envelope.get("source_peer_id", "")),
                refusal_payload=refusal_payload,
            )
            continue
        proposals.append(dict(built.get("proposal") or {}))

    resolved = _resolve_proposals(proposals)
    state = dict(runtime.get("global_state") or {})
    clients = _runtime_clients(runtime)
    for proposal in resolved:
        peer_id = str(proposal.get("source_peer_id", "")).strip()
        client = dict(clients.get(peer_id) or {})
        executed = execute_intent(
            state=state,
            intent={
                "intent_id": str(proposal.get("intent_id", "")),
                "process_id": str(proposal.get("process_id", "")),
                "inputs": dict(proposal.get("inputs") or {}),
            },
            law_profile=dict(client.get("law_profile") or {}),
            authority_context=dict(client.get("authority_context") or {}),
            navigation_indices=dict(runtime.get("registry_payloads") or {}),
            policy_context=dict(runtime.get("registry_payloads") or {}),
        )
        if str(executed.get("result", "")) != "complete":
            refusal_payload = dict(executed.get("refusal") or {})
            processed.append(
                {
                    "envelope_id": str(proposal.get("envelope_id", "")),
                    "peer_id": peer_id,
                    "result": "refused",
                    "refusal": refusal_payload,
                }
            )
            _record_refusal(
                runtime=runtime,
                tick=int(tick),
                envelope_id=str(proposal.get("envelope_id", "")),
                peer_id=peer_id,
                refusal_payload=refusal_payload,
            )
            continue
        processed.append(
            {
                "envelope_id": str(proposal.get("envelope_id", "")),
                "peer_id": peer_id,
                "result": "complete",
                "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            }
        )

    runtime["global_state"] = state
    server["network_tick"] = int(tick)
    server["queued_envelopes"] = sorted(pending, key=_queue_sort_key)
    runtime["server"] = server

    anchor = _build_anchor_frame(repo_root=repo_root, runtime=runtime, tick=int(tick))
    if str(anchor.get("result", "")) != "complete":
        return anchor
    frame = dict(anchor.get("frame") or {})

    deltas = _emit_client_deltas(repo_root=repo_root, runtime=runtime, tick=int(tick))
    if str(deltas.get("result", "")) != "complete":
        return deltas

    return {
        "result": "complete",
        "tick": int(tick),
        "processed_envelopes": processed,
        "resolved_proposals": resolved,
        "hash_anchor_frame": frame,
        "perceived_deltas": list(deltas.get("perceived_deltas") or []),
    }


def run_hybrid_simulation(repo_root: str, runtime: dict, envelopes: List[dict], ticks: int) -> Dict[str, object]:
    queue_results = []
    for envelope in sorted((dict(row) for row in (envelopes or []) if isinstance(row, dict)), key=_queue_sort_key):
        queued = queue_intent_envelope(repo_root=repo_root, runtime=runtime, envelope=envelope)
        queue_results.append(
            {
                "envelope_id": str(envelope.get("envelope_id", "")),
                "result": str(queued.get("result", "")),
                "reason_code": str(((queued.get("refusal") or {}).get("reason_code", ""))),
            }
        )
        if str(queued.get("result", "")) != "complete":
            return {
                "result": "refused",
                "queue_results": queue_results,
                "refusal": dict(queued.get("refusal") or {}),
            }

    steps = []
    for _ in range(max(0, _as_int(ticks, 0))):
        step = advance_hybrid_tick(repo_root=repo_root, runtime=runtime)
        steps.append(
            {
                "tick": int(step.get("tick", 0) or 0),
                "result": str(step.get("result", "")),
                "composite_hash": str(((step.get("hash_anchor_frame") or {}).get("composite_hash", ""))),
            }
        )
        if str(step.get("result", "")) != "complete":
            return {
                "result": str(step.get("result", "")),
                "queue_results": queue_results,
                "steps": steps,
                "refusal": dict(step.get("refusal") or {}),
            }

    server = _runtime_server(runtime)
    frames = list(server.get("hash_anchor_frames") or [])
    return {
        "result": "complete",
        "queue_results": queue_results,
        "steps": steps,
        "final_tick": int(server.get("network_tick", 0) or 0),
        "final_composite_hash": str((frames[-1] if frames else {}).get("composite_hash", "")),
    }


def prepare_hybrid_baseline(repo_root: str, runtime: dict) -> Dict[str, object]:
    server = _runtime_server(runtime)
    tick = _as_int(server.get("network_tick", 0), 0)
    frames = list(server.get("hash_anchor_frames") or [])
    if not frames:
        built = _build_anchor_frame(repo_root=repo_root, runtime=runtime, tick=int(tick))
        if str(built.get("result", "")) != "complete":
            return built
        frames = list((_runtime_server(runtime).get("hash_anchor_frames") or []))

    snap_result = _snapshot_for_tick(repo_root=repo_root, runtime=runtime, tick=int(tick))
    if str(snap_result.get("result", "")) != "complete":
        return snap_result
    snapshots = list(snap_result.get("snapshots") or [])
    if not snapshots:
        return refusal(
            "refusal.net.resync_required",
            "baseline sync could not produce shard snapshots",
            "Ensure at least one active shard exists before baseline sync.",
            {"tick": str(tick)},
            "$.snapshot",
        )
    primary = {}
    for row in snapshots:
        if str((row or {}).get("shard_id", "")) == DEFAULT_SHARD_ID:
            primary = dict(row)
            break
    if not primary:
        primary = dict(sorted((dict(row) for row in snapshots if isinstance(row, dict)), key=lambda row: str(row.get("snapshot_id", "")))[0])

    snapshot_ids = sorted(str((row or {}).get("snapshot_id", "")) for row in snapshots if str((row or {}).get("snapshot_id", "")))
    server = _runtime_server(runtime)
    server["baseline_snapshot_id"] = str(primary.get("snapshot_id", ""))
    server["baseline_snapshot_ids"] = snapshot_ids
    runtime["server"] = server

    latest_frame = dict(sorted((dict(row) for row in frames if isinstance(row, dict)), key=lambda row: int(row.get("tick", 0) or 0))[-1])
    summary = {
        "schema_version": "1.0.0",
        "policy_id": str(runtime.get("policy_id", "")),
        "shard_map_id": str(runtime.get("shard_map_id", "")),
        "perception_interest_policy_id": str((_perception_policy(runtime).get("policy_id", ""))),
        "baseline_tick": int(tick),
        "snapshot_id": str(primary.get("snapshot_id", "")),
        "snapshot_ids": snapshot_ids,
        "hash_anchor_frame": latest_frame,
        "peer_ids": sorted((_runtime_clients(runtime)).keys()),
        "extensions": {},
    }
    baseline_path = _write_runtime_artifact(
        runtime=runtime,
        rel_path=norm(os.path.join("baseline", "hybrid.baseline.tick.{}.json".format(int(tick)))),
        payload=summary,
    )
    return {
        "result": "complete",
        "baseline": summary,
        "baseline_path": baseline_path,
        "snapshot": primary,
        "snapshots": snapshots,
    }


def request_hybrid_resync(repo_root: str, runtime: dict, peer_id: str, snapshot_id: str = "") -> Dict[str, object]:
    del repo_root
    server = _runtime_server(runtime)
    snapshots = list(server.get("snapshots") or [])
    if not snapshots:
        return refusal(
            "refusal.net.resync_required",
            "SRZ hybrid runtime has no snapshots available for resync",
            "Run stage.net_sync_baseline to produce deterministic shard snapshots.",
            {"peer_id": str(peer_id)},
            "$.snapshot",
        )
    selected = {}
    requested = str(snapshot_id).strip()
    if requested:
        for row in snapshots:
            if isinstance(row, dict) and str(row.get("snapshot_id", "")).strip() == requested:
                selected = dict(row)
                break
    if not selected:
        selected = dict(sorted((dict(row) for row in snapshots if isinstance(row, dict)), key=lambda row: str(row.get("snapshot_id", "")))[-1])

    clients = _runtime_clients(runtime)
    if str(peer_id) not in clients:
        return refusal(
            "refusal.net.authority_violation",
            "peer is not joined to SRZ hybrid runtime",
            "Join peer before requesting snapshot resync.",
            {"peer_id": str(peer_id)},
            "$.peer_id",
        )
    observed = _derive_perceived_for_peer(runtime=runtime, peer_id=str(peer_id))
    if str(observed.get("result", "")) != "complete":
        return observed
    client = dict(clients.get(str(peer_id)) or {})
    client["last_perceived_model"] = dict(observed.get("perceived_model") or {})
    client["last_perceived_hash"] = str(observed.get("perceived_hash", ""))
    client["memory_state"] = dict(observed.get("memory_state") or {})
    client["last_applied_tick"] = int(selected.get("tick", 0) or 0)
    client["resync_count"] = _as_int(client.get("resync_count", 0), 0) + 1
    clients[str(peer_id)] = client
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    return {
        "result": "complete",
        "snapshot": selected,
        "peer_id": str(peer_id),
        "perceived_hash": str(client.get("last_perceived_hash", "")),
    }


def join_client_hybrid(
    repo_root: str,
    runtime: dict,
    peer_id: str,
    authority_context: dict,
    law_profile: dict,
    lens_profile: dict,
    negotiated_policy_id: str,
    snapshot_id: str = "",
) -> Dict[str, object]:
    if str(negotiated_policy_id).strip() != "policy.net.srz_hybrid":
        return refusal(
            "refusal.net.join_policy_mismatch",
            "net join requested policy '{}' but runtime policy is srz_hybrid".format(
                str(negotiated_policy_id).strip() or "<empty>"
            ),
            "Use negotiated policy policy.net.srz_hybrid for this join flow.",
            {"negotiated_policy_id": str(negotiated_policy_id).strip() or "<empty>"},
            "$.network.negotiated_replication_policy_id",
        )
    _register_client(
        runtime=runtime,
        peer_id=str(peer_id),
        authority_context=authority_context,
        law_profile=law_profile,
        lens_profile=lens_profile,
    )
    resynced = request_hybrid_resync(
        repo_root=repo_root,
        runtime=runtime,
        peer_id=str(peer_id),
        snapshot_id=str(snapshot_id),
    )
    if str(resynced.get("result", "")) != "complete":
        return resynced
    return {
        "result": "complete",
        "peer_id": str(peer_id),
        "snapshot_id": str(((resynced.get("snapshot") or {}).get("snapshot_id", ""))),
        "perceived_hash": str(resynced.get("perceived_hash", "")),
    }
