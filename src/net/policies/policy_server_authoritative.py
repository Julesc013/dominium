"""Deterministic server-authoritative replication policy (PerceivedModel-only transport)."""

from __future__ import annotations

import copy
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.common import norm, refusal, write_canonical_json
from tools.xstack.sessionx.observation import build_truth_model, observe_truth
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.sessionx.srz import (
    DEFAULT_SHARD_ID,
    build_single_shard,
    composite_hash,
    per_tick_hash,
)


POLICY_ID_SERVER_AUTHORITATIVE = "policy.net.server_authoritative"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _state_tick(state: dict) -> int:
    sim = state.get("simulation_time")
    if not isinstance(sim, dict):
        return 0
    return max(0, _as_int(sim.get("tick", 0), 0))


def _zero_hash() -> str:
    return "0" * 64


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


def _module_enabled(runtime: dict, module_id: str) -> bool:
    anti = dict(runtime.get("anti_cheat") or {})
    modules = _sorted_tokens(list(anti.get("modules_enabled") or []))
    return str(module_id).strip() in modules


def _module_action(runtime: dict, module_id: str, fallback: str = "audit") -> str:
    anti = dict(runtime.get("anti_cheat") or {})
    defaults = anti.get("default_actions")
    if isinstance(defaults, dict):
        token = str(defaults.get(module_id, "")).strip()
        if token:
            return token
    return str(fallback)


def _emit_anti_cheat_event(
    repo_root: str,
    runtime: dict,
    tick: int,
    peer_id: str,
    module_id: str,
    severity: str,
    reason_code: str,
    evidence: List[str],
    default_action: str,
) -> dict:
    if not _module_enabled(runtime, module_id):
        return {}
    server = dict(runtime.get("server") or {})
    rows = list(server.get("anti_cheat_events") or [])
    event_index = len(rows) + 1
    bounded_evidence = [str(item)[:240] for item in list(evidence or []) if str(item).strip()]
    action = _module_action(runtime, module_id=module_id, fallback=default_action)
    fingerprint_payload = {
        "tick": int(tick),
        "peer_id": str(peer_id),
        "module_id": str(module_id),
        "severity": str(severity),
        "reason_code": str(reason_code),
        "evidence": bounded_evidence,
        "recommended_action": action,
    }
    event = {
        "schema_version": "1.0.0",
        "event_id": "ac.{}.tick.{}.seq.{}".format(str(peer_id), int(tick), str(event_index).zfill(4)),
        "tick": int(tick),
        "peer_id": str(peer_id),
        "module_id": str(module_id),
        "severity": str(severity),
        "reason_code": str(reason_code),
        "evidence": bounded_evidence,
        "recommended_action": action,
        "deterministic_fingerprint": canonical_sha256(fingerprint_payload),
        "extensions": {},
    }
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_anti_cheat_event",
        payload=event,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return {}
    rows.append(event)
    server["anti_cheat_events"] = sorted(rows, key=lambda row: str(row.get("event_id", "")))
    runtime["server"] = server
    return event


def _policy_row(registry_payload: dict, policy_id: str, key: str = "policies") -> dict:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
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


def _snapshot_cadence(replication_policy: dict, explicit: int) -> int:
    if int(explicit) > 0:
        return max(1, int(explicit))
    ext = replication_policy.get("extensions")
    if isinstance(ext, dict):
        value = _as_int(ext.get("snapshot_cadence_ticks", 0), 0)
        if value > 0:
            return int(value)
    return 2


def _register_client(
    runtime: dict,
    peer_id: str,
    authority_context: dict,
    law_profile: dict,
    lens_profile: dict,
) -> None:
    clients = dict(runtime.get("clients") or {})
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
        "last_anchor_hash": "",
        "last_applied_tick": int((runtime.get("server") or {}).get("network_tick", 0)),
        "joined": True,
        "received_delta_ids": [],
        "resync_count": 0,
    }
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))


def initialize_authoritative_runtime(
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
    replication_policy_registry: dict | None = None,
    registry_payloads: dict | None = None,
    snapshot_cadence_ticks: int = 0,
) -> Dict[str, object]:
    network = dict(session_spec.get("network") or {})
    if not network:
        return refusal(
            "refusal.net.join_policy_mismatch",
            "server-authoritative runtime requires SessionSpec.network payload",
            "Provide SessionSpec.network fields before initializing multiplayer runtime.",
            {"schema_id": "session_spec"},
            "$.network",
        )
    requested_policy = str(network.get("requested_replication_policy_id", "")).strip()
    if requested_policy != POLICY_ID_SERVER_AUTHORITATIVE:
        return refusal(
            "refusal.net.join_policy_mismatch",
            "SessionSpec requested replication policy '{}' is not server-authoritative".format(requested_policy or "<empty>"),
            "Set requested_replication_policy_id to policy.net.server_authoritative.",
            {"requested_replication_policy_id": requested_policy or "<empty>"},
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

    replication_policy_row = {}
    if isinstance(replication_policy_registry, dict):
        replication_policy_row = _policy_row(replication_policy_registry, POLICY_ID_SERVER_AUTHORITATIVE)

    cadence = _snapshot_cadence(replication_policy_row, explicit=int(snapshot_cadence_ticks))
    registry_hashes = _registry_hashes(lock_payload)
    artifacts_rel = norm(os.path.join("build", "net", "authoritative", str(save_id)))

    runtime = {
        "schema_version": "1.0.0",
        "policy_id": POLICY_ID_SERVER_AUTHORITATIVE,
        "repo_root": norm(repo_root),
        "save_id": str(save_id),
        "artifacts_rel": artifacts_rel,
        "session_spec": copy.deepcopy(session_spec if isinstance(session_spec, dict) else {}),
        "lock_payload": copy.deepcopy(lock_payload if isinstance(lock_payload, dict) else {}),
        "registry_payloads": copy.deepcopy(registry_payloads if isinstance(registry_payloads, dict) else {}),
        "universe_identity": copy.deepcopy(universe_identity if isinstance(universe_identity, dict) else {}),
        "identity_ref": norm(os.path.join("saves", str(save_id), "universe_identity.json")),
        "state_ref": norm(os.path.join("saves", str(save_id), "universe_state.json")),
        "anti_cheat": {
            "policy_id": anti_cheat_policy_id,
            "modules_enabled": _sorted_tokens(list(anti_cheat_policy.get("modules_enabled") or [])),
            "default_actions": dict(anti_cheat_policy.get("default_actions") or {}),
            "module_registry_map": module_map,
        },
        "server": {
            "peer_id": str(network.get("server_peer_id", "")).strip(),
            "network_tick": max(0, _state_tick(universe_state)),
            "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
            "registry_hashes": registry_hashes,
            "universe_state": copy.deepcopy(universe_state if isinstance(universe_state, dict) else {}),
            "intent_queue": [],
            "last_sequence_by_peer": {},
            "seen_envelope_ids": [],
            "last_tick_hash": "",
            "last_composite_hash": _zero_hash(),
            "hash_anchor_frames": [],
            "snapshots": [],
            "snapshot_peer_models": {},
            "snapshot_peer_memory": {},
            "snapshot_cadence_ticks": int(cadence),
            "baseline_snapshot_id": "",
            "anti_cheat_events": [],
            "perceived_deltas": [],
            "refusals": [],
        },
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
        "snapshot_cadence_ticks": int(cadence),
        "initial_peer_id": initial_peer_id,
    }


def build_client_intent_envelope(
    runtime: dict,
    peer_id: str,
    intent_id: str,
    process_id: str,
    inputs: dict,
    submission_tick: int | None = None,
    target_shard_id: str = DEFAULT_SHARD_ID,
) -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    next_sequence = _as_int((server.get("last_sequence_by_peer") or {}).get(str(peer_id), 0), 0) + 1
    target_tick = _as_int(submission_tick if submission_tick is not None else server.get("network_tick", 0), 0) + (
        0 if submission_tick is not None else 1
    )
    clients = dict(runtime.get("clients") or {})
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
        "target_shard_id": str(target_shard_id or DEFAULT_SHARD_ID),
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


def _queue_sort_key(envelope: dict) -> Tuple[int, str, str, int, str]:
    return (
        _as_int(envelope.get("submission_tick", 0), 0),
        str(envelope.get("target_shard_id", "")),
        str(envelope.get("source_peer_id", "")),
        _as_int(envelope.get("deterministic_sequence_number", 0), 0),
        str(envelope.get("intent_id", "")),
    )


def queue_intent_envelope(repo_root: str, runtime: dict, envelope: dict) -> Dict[str, object]:
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_intent_envelope",
        payload=dict(envelope if isinstance(envelope, dict) else {}),
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int((runtime.get("server") or {}).get("network_tick", 0), 0),
            peer_id=str((envelope or {}).get("source_peer_id", "peer.unknown")),
            module_id="ac.module.input_integrity",
            severity="warn",
            reason_code="refusal.net.envelope_invalid",
            evidence=["intent envelope schema validation failed"],
            default_action="refuse",
        )
        return refusal(
            "refusal.net.envelope_invalid",
            "intent envelope failed net_intent_envelope schema validation",
            "Fix envelope fields and retry submission.",
            {"schema_id": "net_intent_envelope"},
            "$.intent_envelope",
        )

    server = dict(runtime.get("server") or {})
    peer_id = str(envelope.get("source_peer_id", "")).strip()
    clients = dict(runtime.get("clients") or {})
    if peer_id not in clients:
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            module_id="ac.module.authority_integrity",
            severity="violation",
            reason_code="refusal.net.authority_violation",
            evidence=["source peer is not joined to authoritative runtime"],
            default_action="refuse",
        )
        return refusal(
            "refusal.net.authority_violation",
            "source peer is not joined to server-authoritative runtime",
            "Join peer via baseline snapshot before submitting intents.",
            {"peer_id": peer_id or "<empty>"},
            "$.source_peer_id",
        )

    target_shard_id = str(envelope.get("target_shard_id", "")).strip()
    if target_shard_id != DEFAULT_SHARD_ID:
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            module_id="ac.module.authority_integrity",
            severity="violation",
            reason_code="refusal.net.shard_target_invalid",
            evidence=["target_shard_id must be shard.0 for current authoritative runtime"],
            default_action="refuse",
        )
        return refusal(
            "refusal.net.shard_target_invalid",
            "target_shard_id '{}' is invalid for current authoritative runtime".format(target_shard_id or "<empty>"),
            "Route envelopes to shard.0 until distributed SRZ replication is enabled.",
            {"target_shard_id": target_shard_id or "<empty>"},
            "$.target_shard_id",
        )

    expected_pack_lock = str(server.get("pack_lock_hash", "")).strip()
    if str(envelope.get("pack_lock_hash", "")).strip() != expected_pack_lock:
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            module_id="ac.module.input_integrity",
            severity="violation",
            reason_code="refusal.net.handshake_pack_lock_mismatch",
            evidence=["envelope pack_lock_hash mismatches server lock hash"],
            default_action="refuse",
        )
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
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            module_id="ac.module.replay_protection",
            severity="violation",
            reason_code="refusal.net.replay_detected",
            evidence=["duplicate envelope_id detected"],
            default_action="refuse",
        )
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
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            module_id="ac.module.sequence_integrity",
            severity="violation",
            reason_code="refusal.net.sequence_violation",
            evidence=[
                "expected deterministic_sequence_number={} got={}".format(expected_next, sequence),
            ],
            default_action="refuse",
        )
        return refusal(
            "refusal.net.sequence_violation",
            "deterministic_sequence_number is non-monotonic for peer '{}'".format(peer_id),
            "Submit envelope sequence numbers monotonically per peer.",
            {"peer_id": peer_id, "expected_sequence": str(expected_next), "received_sequence": str(sequence)},
            "$.deterministic_sequence_number",
        )

    queue_rows = list(server.get("intent_queue") or [])
    queue_rows.append(copy.deepcopy(envelope))
    queue_rows = sorted(queue_rows, key=_queue_sort_key)
    seen.append(envelope_id)
    last_seq_map[peer_id] = int(sequence)
    server["intent_queue"] = queue_rows
    server["seen_envelope_ids"] = seen
    server["last_sequence_by_peer"] = dict((key, int(last_seq_map[key])) for key in sorted(last_seq_map.keys()))
    runtime["server"] = server
    return {
        "result": "complete",
        "queue_size": len(queue_rows),
        "peer_id": peer_id,
    }


def _derive_perceived_for_peer(
    runtime: dict,
    peer_id: str,
) -> Dict[str, object]:
    clients = dict(runtime.get("clients") or {})
    client_entry = dict(clients.get(str(peer_id)) or {})
    if not client_entry:
        return refusal(
            "refusal.net.authority_violation",
            "peer is not joined for perceived-state derivation",
            "Join peer before deriving perceived deltas.",
            {"peer_id": str(peer_id)},
            "$.peer_id",
        )
    server = dict(runtime.get("server") or {})
    lock_payload = dict(runtime.get("lock_payload") or {})
    truth_model = build_truth_model(
        universe_identity=dict(runtime.get("universe_identity") or {}),
        universe_state=dict(server.get("universe_state") or {}),
        lockfile_payload=lock_payload,
        identity_path=str(runtime.get("identity_ref", "")),
        state_path=str(runtime.get("state_ref", "")),
        registry_payloads=dict(runtime.get("registry_payloads") or {}),
    )
    observed = observe_truth(
        truth_model=truth_model,
        lens=dict(client_entry.get("lens_profile") or {}),
        law_profile=dict(client_entry.get("law_profile") or {}),
        authority_context=dict(client_entry.get("authority_context") or {}),
        viewpoint_id="viewpoint.peer.{}".format(str(peer_id)),
        memory_state=dict(client_entry.get("memory_state") or {}),
    )
    if str(observed.get("result", "")) != "complete":
        return observed
    return {
        "result": "complete",
        "perceived_model": dict(observed.get("perceived_model") or {}),
        "perceived_hash": str(observed.get("perceived_model_hash", "")),
        "memory_state": dict(observed.get("memory_state") or {}),
        "epistemic_policy_id": str(observed.get("epistemic_policy_id", "")),
        "retention_policy_id": str(observed.get("retention_policy_id", "")),
    }


def _build_anchor_frame(repo_root: str, runtime: dict, tick: int) -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    state = dict(server.get("universe_state") or {})
    shard = build_single_shard(
        universe_state=state,
        authority_origin="server",
        compatibility_version="1.0.0",
        last_hash_anchor=str(server.get("last_tick_hash", "")),
    )
    tick_hash = per_tick_hash(
        universe_state=state,
        shards=[shard],
        pack_lock_hash=str(server.get("pack_lock_hash", "")),
        registry_hashes=dict(server.get("registry_hashes") or {}),
        last_tick_hash=str(server.get("last_tick_hash", "")),
    )
    shard["last_hash_anchor"] = tick_hash
    composite = composite_hash([shard])
    previous_composite = str(server.get("last_composite_hash", "")).strip() or _zero_hash()
    cadence = max(1, _as_int(server.get("snapshot_cadence_ticks", 1), 1))
    checkpoint_id = ""
    if int(tick) % cadence == 0:
        checkpoint_id = "checkpoint.tick.{}".format(int(tick))
    frame = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "shard_hashes": [
            {
                "shard_id": DEFAULT_SHARD_ID,
                "hash": str(tick_hash),
            }
        ],
        "composite_hash": str(composite),
        "previous_composite_hash": previous_composite,
        "checkpoint_id": checkpoint_id,
        "extensions": {},
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
            "hash anchor frame failed schema validation",
            "Fix net_hash_anchor_frame payload generation and retry tick advance.",
            {"schema_id": "net_hash_anchor_frame"},
            "$.hash_anchor_frame",
        )
    server["last_tick_hash"] = str(tick_hash)
    server["last_composite_hash"] = str(composite)
    runtime["server"] = server
    return {
        "result": "complete",
        "frame": frame,
    }


def _snapshot_for_tick(repo_root: str, runtime: dict, tick: int) -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    snapshot_id = "snapshot.{}.tick.{}".format(DEFAULT_SHARD_ID, int(tick))
    rows = list(server.get("snapshots") or [])
    for row in rows:
        if isinstance(row, dict) and str(row.get("snapshot_id", "")).strip() == snapshot_id:
            return {"result": "complete", "snapshot": dict(row)}

    clients = dict(runtime.get("clients") or {})
    peer_hashes = {}
    peer_models = {}
    peer_memory_hashes = {}
    peer_memory = {}
    for peer_id in sorted(clients.keys()):
        client = dict(clients.get(peer_id) or {})
        peer_hashes[peer_id] = str(client.get("last_perceived_hash", ""))
        peer_models[peer_id] = copy.deepcopy(client.get("last_perceived_model") or {})
        memory_state = dict(client.get("memory_state") or {})
        peer_memory[peer_id] = memory_state
        peer_memory_hashes[peer_id] = canonical_sha256(memory_state)

    payload_rel = norm(os.path.join("snapshots", "{}.payload.json".format(snapshot_id)))
    payload = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "tick": int(tick),
        "peer_hashes": dict((key, peer_hashes[key]) for key in sorted(peer_hashes.keys())),
        "peer_memory_hashes": dict((key, peer_memory_hashes[key]) for key in sorted(peer_memory_hashes.keys())),
        "extensions": {},
    }
    payload_ref = _write_runtime_artifact(runtime=runtime, rel_path=payload_rel, payload=payload)
    network_payload = dict(((runtime.get("session_spec") or {}).get("network") or {}))
    schema_versions = dict((network_payload.get("schema_versions") or {}))
    if not schema_versions:
        schema_versions = {"session_spec": "1.0.0"}
    snapshot = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id,
        "tick": int(tick),
        "shard_id": DEFAULT_SHARD_ID,
        "pack_lock_hash": str(server.get("pack_lock_hash", "")),
        "registry_hashes": dict(server.get("registry_hashes") or {}),
        "truth_snapshot_hash": canonical_sha256(dict(server.get("universe_state") or {})),
        "payload_ref": str(payload_ref),
        "schema_versions": dict((key, str(schema_versions[key])) for key in sorted(schema_versions.keys())),
        "extensions": {},
    }
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="net_snapshot",
        payload=snapshot,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return refusal(
            "refusal.net.resync_snapshot_missing",
            "snapshot artifact failed schema validation",
            "Fix net_snapshot payload generation before retrying baseline/resync.",
            {"schema_id": "net_snapshot"},
            "$.snapshot",
        )

    rows.append(snapshot)
    rows = sorted(rows, key=lambda row: str(row.get("snapshot_id", "")))
    server["snapshots"] = rows
    snapshot_models = dict(server.get("snapshot_peer_models") or {})
    snapshot_models[snapshot_id] = peer_models
    server["snapshot_peer_models"] = snapshot_models
    snapshot_memory = dict(server.get("snapshot_peer_memory") or {})
    snapshot_memory[snapshot_id] = peer_memory
    server["snapshot_peer_memory"] = snapshot_memory
    if int(tick) == _as_int(server.get("network_tick", 0), 0):
        server["baseline_snapshot_id"] = snapshot_id
    runtime["server"] = server
    return {"result": "complete", "snapshot": snapshot}


def prepare_server_authoritative_baseline(repo_root: str, runtime: dict) -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    tick = _as_int(server.get("network_tick", 0), 0)
    clients = dict(runtime.get("clients") or {})
    for peer_id in sorted(clients.keys()):
        observed = _derive_perceived_for_peer(runtime=runtime, peer_id=peer_id)
        if str(observed.get("result", "")) != "complete":
            return observed
        client = dict(clients.get(peer_id) or {})
        client["last_perceived_model"] = dict(observed.get("perceived_model") or {})
        client["last_perceived_hash"] = str(observed.get("perceived_hash", ""))
        client["memory_state"] = dict(observed.get("memory_state") or {})
        client["last_applied_tick"] = int(tick)
        clients[peer_id] = client
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))

    if not list(server.get("hash_anchor_frames") or []):
        anchor_result = _build_anchor_frame(repo_root=repo_root, runtime=runtime, tick=int(tick))
        if str(anchor_result.get("result", "")) != "complete":
            return anchor_result
        frame = dict(anchor_result.get("frame") or {})
        server = dict(runtime.get("server") or {})
        anchor_rows = list(server.get("hash_anchor_frames") or [])
        anchor_rows.append(frame)
        server["hash_anchor_frames"] = sorted(anchor_rows, key=lambda row: int(row.get("tick", 0) or 0))
        runtime["server"] = server

    snapshot_result = _snapshot_for_tick(repo_root=repo_root, runtime=runtime, tick=int(tick))
    if str(snapshot_result.get("result", "")) != "complete":
        return snapshot_result
    snapshot = dict(snapshot_result.get("snapshot") or {})
    summary = {
        "schema_version": "1.0.0",
        "policy_id": POLICY_ID_SERVER_AUTHORITATIVE,
        "baseline_tick": int(tick),
        "snapshot_id": str(snapshot.get("snapshot_id", "")),
        "snapshot_ref": str(snapshot.get("payload_ref", "")),
        "hash_anchor_frame": dict(((runtime.get("server") or {}).get("hash_anchor_frames") or [{}])[-1] or {}),
        "peer_ids": sorted((runtime.get("clients") or {}).keys()),
        "extensions": {},
    }
    baseline_rel = norm(os.path.join("baseline", "baseline.tick.{}.json".format(int(tick))))
    baseline_path = _write_runtime_artifact(runtime=runtime, rel_path=baseline_rel, payload=summary)
    return {
        "result": "complete",
        "baseline": summary,
        "baseline_path": baseline_path,
        "snapshot": snapshot,
    }


def _apply_delta(client_entry: dict, delta_payload: dict, expected_hash: str) -> Dict[str, object]:
    replace_payload = delta_payload.get("replace")
    if not isinstance(replace_payload, dict):
        return refusal(
            "refusal.net.resync_required",
            "perceived delta payload is missing replace object",
            "Request authoritative snapshot resync and retry.",
            {"field": "replace"},
            "$.perceived_delta",
        )
    next_model = dict(replace_payload)
    actual_hash = canonical_sha256(next_model)
    if str(expected_hash).strip() != actual_hash:
        return refusal(
            "refusal.net.resync_required",
            "perceived delta hash mismatch detected",
            "Request authoritative snapshot resync before continuing.",
            {"expected_hash": str(expected_hash), "actual_hash": actual_hash},
            "$.perceived_delta.perceived_hash",
        )
    client_entry["last_perceived_model"] = next_model
    client_entry["last_perceived_hash"] = actual_hash
    return {"result": "complete"}


def advance_authoritative_tick(repo_root: str, runtime: dict) -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    server_tick = _as_int(server.get("network_tick", 0), 0) + 1
    queue_rows = list(server.get("intent_queue") or [])
    ready = [row for row in queue_rows if _as_int((row or {}).get("submission_tick", 0), 0) <= int(server_tick)]
    pending = [row for row in queue_rows if row not in ready]
    ready = sorted((dict(item) for item in ready if isinstance(item, dict)), key=_queue_sort_key)
    processed_rows = []

    clients = dict(runtime.get("clients") or {})
    state = dict(server.get("universe_state") or {})
    for envelope in ready:
        peer_id = str(envelope.get("source_peer_id", "")).strip()
        client = dict(clients.get(peer_id) or {})
        payload = dict(envelope.get("payload") or {})
        process_id = str(payload.get("process_id", "")).strip()
        inputs = payload.get("inputs")
        if not process_id or not isinstance(inputs, dict):
            refusal_payload = refusal(
                "refusal.net.envelope_invalid",
                "intent envelope payload must contain process_id and inputs",
                "Fix envelope payload structure and resend.",
                {"envelope_id": str(envelope.get("envelope_id", ""))},
                "$.payload",
            )
            processed_rows.append(
                {
                    "envelope_id": str(envelope.get("envelope_id", "")),
                    "peer_id": peer_id,
                    "result": "refused",
                    "refusal": dict(refusal_payload.get("refusal") or {}),
                }
            )
            _emit_anti_cheat_event(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                module_id="ac.module.input_integrity",
                severity="warn",
                reason_code="refusal.net.envelope_invalid",
                evidence=["intent envelope payload shape invalid"],
                default_action="refuse",
            )
            continue

        executed = execute_intent(
            state=state,
            intent={
                "intent_id": str(envelope.get("intent_id", "")),
                "process_id": process_id,
                "inputs": dict(inputs),
            },
            law_profile=dict(client.get("law_profile") or {}),
            authority_context=dict(client.get("authority_context") or {}),
            navigation_indices=dict(runtime.get("registry_payloads") or {}),
            policy_context=dict(runtime.get("registry_payloads") or {}),
        )
        if str(executed.get("result", "")) != "complete":
            processed_rows.append(
                {
                    "envelope_id": str(envelope.get("envelope_id", "")),
                    "peer_id": peer_id,
                    "result": "refused",
                    "refusal": dict(executed.get("refusal") or {}),
                }
            )
            _emit_anti_cheat_event(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                module_id="ac.module.authority_integrity",
                severity="violation",
                reason_code=str(((executed.get("refusal") or {}).get("reason_code", "refusal.net.authority_violation"))),
                evidence=["authoritative process execution refused submitted envelope"],
                default_action="refuse",
            )
            server_refusals = list((runtime.get("server") or {}).get("refusals") or [])
            server_refusals.append(
                {
                    "tick": int(server_tick),
                    "peer_id": peer_id,
                    "envelope_id": str(envelope.get("envelope_id", "")),
                    "reason_code": str(((executed.get("refusal") or {}).get("reason_code", ""))),
                }
            )
            server_now = dict(runtime.get("server") or {})
            server_now["refusals"] = sorted(
                server_refusals,
                key=lambda row: (
                    int(row.get("tick", 0)),
                    str(row.get("peer_id", "")),
                    str(row.get("envelope_id", "")),
                ),
            )
            runtime["server"] = server_now
            continue

        processed_rows.append(
            {
                "envelope_id": str(envelope.get("envelope_id", "")),
                "peer_id": peer_id,
                "result": "complete",
                "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            }
        )

    server = dict(runtime.get("server") or {})
    server["network_tick"] = int(server_tick)
    server["intent_queue"] = sorted((dict(row) for row in pending if isinstance(row, dict)), key=_queue_sort_key)
    server["universe_state"] = state
    runtime["server"] = server

    anchor_result = _build_anchor_frame(repo_root=repo_root, runtime=runtime, tick=int(server_tick))
    if str(anchor_result.get("result", "")) != "complete":
        return anchor_result
    frame = dict(anchor_result.get("frame") or {})
    server = dict(runtime.get("server") or {})
    anchor_rows = list(server.get("hash_anchor_frames") or [])
    anchor_rows.append(frame)
    server["hash_anchor_frames"] = sorted(anchor_rows, key=lambda row: int(row.get("tick", 0) or 0))
    runtime["server"] = server

    delta_rows = []
    clients = dict(runtime.get("clients") or {})
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
            "perceived_delta_id": "pdelta.{}.tick.{}".format(peer_id, int(server_tick)),
            "tick": int(server_tick),
            "replace": perceived_model,
            "previous_hash": str(client.get("last_perceived_hash", "")),
            "extensions": {},
        }
        delta_rel = norm(os.path.join("deltas", str(peer_id), "tick.{}.json".format(int(server_tick))))
        delta_ref = _write_runtime_artifact(runtime=runtime, rel_path=delta_rel, payload=delta_payload)
        delta_meta = {
            "schema_version": "1.0.0",
            "perceived_delta_id": str(delta_payload.get("perceived_delta_id", "")),
            "tick": int(server_tick),
            "peer_id": peer_id,
            "lens_id": str(perceived_model.get("lens_id", "")),
            "epistemic_scope_id": str(((perceived_model.get("epistemic_scope") or {}).get("scope_id", ""))),
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
            _emit_anti_cheat_event(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                module_id="ac.module.state_integrity",
                severity="violation",
                reason_code="refusal.net.resync_required",
                evidence=["perceived hash mismatch during delta apply"],
                default_action="audit",
            )
            return applied
        client["last_applied_tick"] = int(server_tick)
        received = _sorted_tokens(list(client.get("received_delta_ids") or []) + [str(delta_meta.get("perceived_delta_id", ""))])
        client["received_delta_ids"] = received
        clients[peer_id] = client
        delta_rows.append(delta_meta)

    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    server = dict(runtime.get("server") or {})
    perceived_rows = list(server.get("perceived_deltas") or [])
    perceived_rows.extend(delta_rows)
    server["perceived_deltas"] = sorted(
        perceived_rows,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("peer_id", "")),
            str(row.get("perceived_delta_id", "")),
        ),
    )
    runtime["server"] = server

    snapshot = {}
    cadence = max(1, _as_int(server.get("snapshot_cadence_ticks", 1), 1))
    if int(server_tick) % cadence == 0:
        snapshot_result = _snapshot_for_tick(repo_root=repo_root, runtime=runtime, tick=int(server_tick))
        if str(snapshot_result.get("result", "")) != "complete":
            return snapshot_result
        snapshot = dict(snapshot_result.get("snapshot") or {})

    _emit_anti_cheat_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(server_tick),
        peer_id=str(server.get("peer_id", "peer.server")),
        module_id="ac.module.behavioral_detection",
        severity="info",
        reason_code="ac.behavior.tick_complete",
        evidence=["server-authoritative tick completed"],
        default_action="audit",
    )
    return {
        "result": "complete",
        "tick": int(server_tick),
        "processed_envelopes": processed_rows,
        "hash_anchor_frame": frame,
        "perceived_deltas": delta_rows,
        "client_memory_hashes": dict(
            sorted(
                (
                    key,
                    canonical_sha256(dict((value or {}).get("memory_state") or {})),
                )
                for key, value in (runtime.get("clients") or {}).items()
            )
        ),
        "snapshot": snapshot,
    }


def run_authoritative_simulation(
    repo_root: str,
    runtime: dict,
    envelopes: List[dict],
    ticks: int,
) -> Dict[str, object]:
    queued = []
    for envelope in sorted((dict(row) for row in (envelopes or []) if isinstance(row, dict)), key=_queue_sort_key):
        queued_result = queue_intent_envelope(repo_root=repo_root, runtime=runtime, envelope=envelope)
        queued.append(
            {
                "envelope_id": str(envelope.get("envelope_id", "")),
                "result": str(queued_result.get("result", "")),
                "reason_code": str(((queued_result.get("refusal") or {}).get("reason_code", ""))),
            }
        )
        if str(queued_result.get("result", "")) != "complete":
            return {
                "result": "refused",
                "queue_results": queued,
                "refusal": dict(queued_result.get("refusal") or {}),
            }

    steps = []
    for _ in range(max(0, _as_int(ticks, 0))):
        step = advance_authoritative_tick(repo_root=repo_root, runtime=runtime)
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
                "queue_results": queued,
                "steps": steps,
                "refusal": dict(step.get("refusal") or {}),
            }

    server = dict(runtime.get("server") or {})
    frames = list(server.get("hash_anchor_frames") or [])
    return {
        "result": "complete",
        "queue_results": queued,
        "steps": steps,
        "final_tick": int(server.get("network_tick", 0) or 0),
        "final_composite_hash": str((frames[-1] if frames else {}).get("composite_hash", "")),
    }


def request_resync_snapshot(repo_root: str, runtime: dict, peer_id: str, snapshot_id: str = "") -> Dict[str, object]:
    server = dict(runtime.get("server") or {})
    snapshots = list(server.get("snapshots") or [])
    if not snapshots:
        return refusal(
            "refusal.net.resync_snapshot_missing",
            "authoritative runtime has no snapshots available for resync",
            "Enable snapshot cadence and regenerate baseline snapshot before resync.",
            {"peer_id": str(peer_id)},
            "$.snapshot",
        )
    selected_snapshot = {}
    requested = str(snapshot_id).strip()
    if requested:
        for row in snapshots:
            if isinstance(row, dict) and str(row.get("snapshot_id", "")).strip() == requested:
                selected_snapshot = dict(row)
                break
    if not selected_snapshot:
        selected_snapshot = dict(sorted((dict(row) for row in snapshots if isinstance(row, dict)), key=lambda row: str(row.get("snapshot_id", "")))[-1])
    snapshot_id_token = str(selected_snapshot.get("snapshot_id", "")).strip()
    snapshot_models = dict(server.get("snapshot_peer_models") or {})
    peer_models = dict(snapshot_models.get(snapshot_id_token) or {})
    snapshot_memory = dict(server.get("snapshot_peer_memory") or {})
    peer_memory = dict(snapshot_memory.get(snapshot_id_token) or {})
    peer_model = peer_models.get(str(peer_id))
    peer_memory_state = peer_memory.get(str(peer_id))
    if not isinstance(peer_model, dict):
        observed = _derive_perceived_for_peer(runtime=runtime, peer_id=str(peer_id))
        if str(observed.get("result", "")) != "complete":
            return refusal(
                "refusal.net.resync_snapshot_missing",
                "snapshot does not contain perceived model state for requested peer",
                "Regenerate snapshot after peer joins, then retry resync.",
                {"peer_id": str(peer_id), "snapshot_id": snapshot_id_token},
                "$.snapshot",
            )
        peer_model = dict(observed.get("perceived_model") or {})
        peer_memory_state = dict(observed.get("memory_state") or {})
        peer_models[str(peer_id)] = peer_model
        peer_memory[str(peer_id)] = dict(peer_memory_state)
        snapshot_models[snapshot_id_token] = peer_models
        server["snapshot_peer_models"] = snapshot_models
        snapshot_memory[snapshot_id_token] = peer_memory
        server["snapshot_peer_memory"] = snapshot_memory
        runtime["server"] = server

    clients = dict(runtime.get("clients") or {})
    if str(peer_id) not in clients:
        return refusal(
            "refusal.net.authority_violation",
            "peer is not joined to authoritative runtime",
            "Join peer before requesting snapshot resync.",
            {"peer_id": str(peer_id)},
            "$.peer_id",
        )
    client = dict(clients.get(str(peer_id)) or {})
    client["last_perceived_model"] = dict(peer_model)
    client["last_perceived_hash"] = canonical_sha256(peer_model)
    client["memory_state"] = dict(peer_memory_state if isinstance(peer_memory_state, dict) else {})
    client["last_applied_tick"] = int(selected_snapshot.get("tick", 0) or 0)
    client["resync_count"] = _as_int(client.get("resync_count", 0), 0) + 1
    clients[str(peer_id)] = client
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    return {
        "result": "complete",
        "snapshot": selected_snapshot,
        "peer_id": str(peer_id),
        "perceived_hash": str(client.get("last_perceived_hash", "")),
        "memory_state_hash": canonical_sha256(dict(client.get("memory_state") or {})),
    }


def validate_pipeline_join(
    runtime: dict,
    peer_id: str,
    negotiated_policy_id: str,
    snapshot_id: str,
) -> Dict[str, object]:
    if str(negotiated_policy_id).strip() != POLICY_ID_SERVER_AUTHORITATIVE:
        return refusal(
            "refusal.net.join_policy_mismatch",
            "net join requested policy '{}' but runtime policy is server-authoritative".format(
                str(negotiated_policy_id).strip() or "<empty>"
            ),
            "Use negotiated policy policy.net.server_authoritative for this join flow.",
            {"negotiated_policy_id": str(negotiated_policy_id).strip() or "<empty>"},
            "$.network.negotiated_replication_policy_id",
        )
    server = dict(runtime.get("server") or {})
    snapshots = list(server.get("snapshots") or [])
    snapshot_token = str(snapshot_id).strip()
    if not snapshot_token:
        snapshot_token = str(server.get("baseline_snapshot_id", "")).strip()
    if not snapshot_token:
        return refusal(
            "refusal.net.join_snapshot_invalid",
            "baseline snapshot is missing for authoritative join",
            "Run stage.net_sync_baseline to generate initial snapshot before join.",
            {"peer_id": str(peer_id)},
            "$.snapshot",
        )
    for row in snapshots:
        if isinstance(row, dict) and str(row.get("snapshot_id", "")).strip() == snapshot_token:
            return {"result": "complete", "snapshot_id": snapshot_token}
    return refusal(
        "refusal.net.join_snapshot_invalid",
        "requested join snapshot '{}' is not present".format(snapshot_token),
        "Request an available snapshot_id from authoritative baseline artifacts.",
        {"snapshot_id": snapshot_token},
        "$.snapshot_id",
    )


def join_client_midstream(
    repo_root: str,
    runtime: dict,
    peer_id: str,
    authority_context: dict,
    law_profile: dict,
    lens_profile: dict,
    negotiated_policy_id: str,
    snapshot_id: str = "",
) -> Dict[str, object]:
    join_check = validate_pipeline_join(
        runtime=runtime,
        peer_id=str(peer_id),
        negotiated_policy_id=str(negotiated_policy_id),
        snapshot_id=str(snapshot_id),
    )
    if str(join_check.get("result", "")) != "complete":
        return join_check
    _register_client(
        runtime=runtime,
        peer_id=str(peer_id),
        authority_context=authority_context,
        law_profile=law_profile,
        lens_profile=lens_profile,
    )
    resynced = request_resync_snapshot(
        repo_root=repo_root,
        runtime=runtime,
        peer_id=str(peer_id),
        snapshot_id=str(join_check.get("snapshot_id", "")),
    )
    if str(resynced.get("result", "")) != "complete":
        return resynced
    return {
        "result": "complete",
        "peer_id": str(peer_id),
        "snapshot_id": str(join_check.get("snapshot_id", "")),
        "perceived_hash": str(resynced.get("perceived_hash", "")),
    }
