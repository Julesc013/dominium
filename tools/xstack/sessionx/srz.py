"""SRZ v1 deterministic shard/envelope/hash helpers for single-shard runtime."""

from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance


DEFAULT_SHARD_ID = "shard.0"
DEFAULT_CHECKPOINT_INTERVAL_TICKS = 4


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _stable_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (items or []) if str(item).strip()))


def _stable_positive_int(token: str, modulo: int) -> int:
    digest = hashlib.sha256(str(token).encode("utf-8")).hexdigest()
    return int(int(digest[:16], 16) % max(1, int(modulo)))


def owned_entity_ids(universe_state: dict) -> List[str]:
    tokens: List[str] = []
    world = universe_state.get("world_assemblies")
    if isinstance(world, list):
        tokens.extend(str(item).strip() for item in world if str(item).strip())

    camera_rows = universe_state.get("camera_assemblies")
    if isinstance(camera_rows, list):
        for row in camera_rows:
            if not isinstance(row, dict):
                continue
            token = str(row.get("assembly_id", "")).strip()
            if token:
                tokens.append(token)

    agent_rows = universe_state.get("agent_states")
    if isinstance(agent_rows, list):
        for row in agent_rows:
            if not isinstance(row, dict):
                continue
            token = str(row.get("entity_id", "")).strip() or str(row.get("agent_id", "")).strip()
            if token:
                tokens.append(token)
    return _stable_tokens(tokens)


def owned_region_ids(universe_state: dict) -> List[str]:
    rows = universe_state.get("interest_regions")
    tokens: List[str] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            token = str(row.get("region_id", "")).strip()
            if token:
                tokens.append(token)
    return _stable_tokens(tokens)


def logical_partition_plan(entity_ids: List[str], shard_count: int) -> Dict[str, List[str]]:
    requested = max(1, _as_int(shard_count, 1))
    if requested == 1:
        return {DEFAULT_SHARD_ID: _stable_tokens(entity_ids)}
    partitions: Dict[str, List[str]] = {}
    for index in range(requested):
        partitions["shard.{}".format(index)] = []
    for entity_id in _stable_tokens(entity_ids):
        bucket = _stable_positive_int(entity_id, requested)
        partitions["shard.{}".format(bucket)].append(entity_id)
    for key in sorted(partitions.keys()):
        partitions[key] = _stable_tokens(partitions[key])
    return partitions


def build_single_shard(
    universe_state: dict,
    authority_origin: str = "server",
    compatibility_version: str = "1.0.0",
    last_hash_anchor: str = "",
) -> dict:
    entities = owned_entity_ids(universe_state)
    regions = owned_region_ids(universe_state)
    return {
        "schema_version": "1.0.0",
        "shard_id": DEFAULT_SHARD_ID,
        "authority_origin": str(authority_origin),
        "region_scope": {
            "object_ids": list(entities),
            "spatial_bounds": None,
        },
        "active": True,
        "parent_shard_id": None,
        "compatibility_version": str(compatibility_version),
        "owned_entities": list(entities),
        "owned_regions": list(regions),
        "process_queue": [],
        "last_hash_anchor": str(last_hash_anchor),
    }


def shard_schema_view(shard: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "shard_id": str(shard.get("shard_id", "")),
        "authority_origin": str(shard.get("authority_origin", "")),
        "region_scope": dict(shard.get("region_scope") or {"object_ids": [], "spatial_bounds": None}),
        "active": bool(shard.get("active", False)),
        "parent_shard_id": shard.get("parent_shard_id"),
        "compatibility_version": str(shard.get("compatibility_version", "")),
    }


def validate_srz_shard(repo_root: str, shard: dict) -> Dict[str, object]:
    return validate_instance(
        repo_root=repo_root,
        schema_name="srz_shard",
        payload=shard_schema_view(shard),
        strict_top_level=True,
    )


def _truth_hash_subset(universe_state: dict) -> dict:
    payload = dict(universe_state if isinstance(universe_state, dict) else {})
    return {
        "schema_version": str(payload.get("schema_version", "")),
        "simulation_time": dict(payload.get("simulation_time") or {}),
        "agent_states": list(payload.get("agent_states") or []),
        "world_assemblies": list(payload.get("world_assemblies") or []),
        "active_law_references": list(payload.get("active_law_references") or []),
        "session_references": list(payload.get("session_references") or []),
        "history_anchors": list(payload.get("history_anchors") or []),
        "camera_assemblies": list(payload.get("camera_assemblies") or []),
        "time_control": dict(payload.get("time_control") or {}),
        "process_log": list(payload.get("process_log") or []),
        "interest_regions": list(payload.get("interest_regions") or []),
        "macro_capsules": list(payload.get("macro_capsules") or []),
        "micro_regions": list(payload.get("micro_regions") or []),
        "performance_state": dict(payload.get("performance_state") or {}),
    }


def active_shard_summary(shards: List[dict]) -> List[dict]:
    rows = []
    for shard in shards:
        if not isinstance(shard, dict):
            continue
        if not bool(shard.get("active", False)):
            continue
        rows.append(
            {
                "shard_id": str(shard.get("shard_id", "")),
                "owned_entity_count": len(_stable_tokens(list(shard.get("owned_entities") or []))),
                "owned_region_count": len(_stable_tokens(list(shard.get("owned_regions") or []))),
                "last_hash_anchor": str(shard.get("last_hash_anchor", "")),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("shard_id", "")))


def per_tick_hash(
    universe_state: dict,
    shards: List[dict],
    pack_lock_hash: str,
    registry_hashes: dict,
    last_tick_hash: str,
) -> str:
    payload = {
        "truth_subset": _truth_hash_subset(universe_state),
        "active_shards": active_shard_summary(shards),
        "pack_lock_hash": str(pack_lock_hash),
        "registry_hashes": dict(registry_hashes or {}),
        "last_tick_hash": str(last_tick_hash),
    }
    return canonical_sha256(payload)


def composite_hash(shards: List[dict]) -> str:
    rows = []
    for row in active_shard_summary(shards):
        rows.append(
            {
                "shard_id": str(row.get("shard_id", "")),
                "shard_hash": str(row.get("last_hash_anchor", "")),
            }
        )
    rows = sorted(rows, key=lambda item: str(item.get("shard_id", "")))
    return canonical_sha256({"shards": rows})


def checkpoint_hash(tick: int, tick_hash: str, previous_checkpoint_hash: str, composite: str) -> str:
    payload = {
        "tick": int(tick),
        "tick_hash": str(tick_hash),
        "previous_checkpoint_hash": str(previous_checkpoint_hash),
        "composite_hash": str(composite),
    }
    return canonical_sha256(payload)


def checkpoint_interval_from_policy(activation_policy: dict) -> int:
    value = 0
    if isinstance(activation_policy, dict):
        value = _as_int(activation_policy.get("checkpoint_interval_ticks", 0), 0)
    if value < 1:
        value = DEFAULT_CHECKPOINT_INTERVAL_TICKS
    return int(value)


def _sequence_sort_key(envelope: dict) -> Tuple[int, str]:
    return (
        _as_int(envelope.get("deterministic_sequence_number", 0), 0),
        str(envelope.get("envelope_id", "")),
    )


def build_intent_envelopes(
    intents: List[dict],
    authority_origin: str,
    source_shard_id: str = DEFAULT_SHARD_ID,
    target_shard_id: str = DEFAULT_SHARD_ID,
    starting_tick: int = 0,
) -> List[dict]:
    out: List[dict] = []
    for index, item in enumerate(list(intents or []), start=1):
        if not isinstance(item, dict):
            continue
        process_id = str(item.get("process_id", "")).strip()
        intent_id = str(item.get("intent_id", "")).strip()
        inputs = item.get("inputs")
        if not process_id or not intent_id or not isinstance(inputs, dict):
            continue
        sequence = _as_int(item.get("deterministic_sequence_number", index), index)
        source_id = str(item.get("source_shard_id", source_shard_id)).strip() or DEFAULT_SHARD_ID
        target_id = str(item.get("target_shard_id", target_shard_id)).strip() or DEFAULT_SHARD_ID
        envelope_id = str(item.get("envelope_id", "")).strip() or "env.{}.{}".format(
            source_id,
            str(sequence).zfill(8),
        )
        submission_tick = _as_int(item.get("submission_tick", starting_tick + (index - 1)), starting_tick + (index - 1))
        out.append(
            {
                "schema_version": "1.0.0",
                "envelope_id": envelope_id,
                "authority_origin": str(authority_origin),
                "source_shard_id": source_id,
                "target_shard_id": target_id,
                "intent_id": intent_id,
                "payload": {
                    "process_id": process_id,
                    "inputs": dict(inputs),
                },
                "deterministic_sequence_number": int(sequence),
                "submission_tick": int(max(0, submission_tick)),
            }
        )
    return sorted(out, key=_sequence_sort_key)


def validate_intent_envelope(repo_root: str, envelope: dict) -> Dict[str, object]:
    return validate_instance(
        repo_root=repo_root,
        schema_name="intent_envelope",
        payload=dict(envelope or {}),
        strict_top_level=True,
    )


def simulation_tick(universe_state: dict) -> int:
    sim = universe_state.get("simulation_time")
    if not isinstance(sim, dict):
        return 0
    return max(0, _as_int(sim.get("tick", 0), 0))

