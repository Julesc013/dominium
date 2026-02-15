"""Deterministic SRZ scheduling pipeline (read -> propose -> resolve -> commit)."""

from __future__ import annotations

import copy
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import refusal
from .process_runtime import execute_intent
from .srz import (
    DEFAULT_SHARD_ID,
    build_intent_envelopes,
    build_single_shard,
    checkpoint_hash,
    checkpoint_interval_from_policy,
    composite_hash,
    logical_partition_plan,
    owned_entity_ids,
    owned_region_ids,
    per_tick_hash,
    simulation_tick,
    validate_intent_envelope,
    validate_srz_shard,
)


PROCESS_PRIORITY = {
    "process.region_management_tick": 10,
    "process.time_control_set_rate": 20,
    "process.time_pause": 20,
    "process.time_resume": 20,
    "process.camera_teleport": 30,
    "process.camera_move": 40,
}

PROCESS_ENTITY_SCOPE = {
    "process.region_management_tick": "region.manager",
    "process.time_control_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.camera_teleport": "camera.main",
    "process.camera_move": "camera.main",
}

PROCESS_FIELD_SCOPE = {
    "process.region_management_tick": "region.state",
    "process.time_control_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.camera_teleport": "camera.transform",
    "process.camera_move": "camera.transform",
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _proposal_sort_key(proposal: dict) -> Tuple[int, str, str, int]:
    return (
        _as_int(proposal.get("priority", 0), 0),
        str(proposal.get("entity_id", "")),
        str(proposal.get("process_id", "")),
        _as_int(proposal.get("intent_sequence", 0), 0),
    )


def _deterministic_sequence(envelope: dict) -> int:
    return _as_int(envelope.get("deterministic_sequence_number", 0), 0)


def _submission_tick(envelope: dict) -> int:
    return max(0, _as_int(envelope.get("submission_tick", 0), 0))


def _proposal_from_envelope(envelope: dict, script_step: int) -> dict:
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        payload = {}
    process_id = str(payload.get("process_id", ""))
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
    intent_id = str(envelope.get("intent_id", ""))
    return {
        "envelope_id": str(envelope.get("envelope_id", "")),
        "script_step": int(script_step),
        "intent_sequence": _deterministic_sequence(envelope),
        "process_id": process_id,
        "intent": {
            "intent_id": intent_id,
            "process_id": process_id,
            "inputs": dict(inputs),
        },
        "priority": int(PROCESS_PRIORITY.get(process_id, 999)),
        "entity_id": str(PROCESS_ENTITY_SCOPE.get(process_id, "entity.unknown")),
        "field_scope": str(PROCESS_FIELD_SCOPE.get(process_id, "scope.{}".format(process_id))),
    }


def _proposal_order_variation(proposals: List[dict], worker_count: int) -> List[dict]:
    count = max(1, _as_int(worker_count, 1))
    if count == 1:
        return list(proposals)
    buckets: Dict[int, List[dict]] = {}
    for proposal in proposals:
        sequence = _as_int(proposal.get("intent_sequence", 0), 0)
        bucket_id = int(sequence % count)
        buckets.setdefault(bucket_id, []).append(proposal)
    out: List[dict] = []
    for bucket_id in sorted(buckets.keys(), reverse=True):
        bucket = sorted(buckets[bucket_id], key=lambda row: _proposal_sort_key(row))
        out.extend(bucket)
    return out


def _resolve_phase(proposals: List[dict]) -> Dict[str, List[dict]]:
    accepted: List[dict] = []
    dropped: List[dict] = []
    seen_scopes: set = set()
    for proposal in sorted(list(proposals), key=_proposal_sort_key):
        scope_key = "{}|{}".format(str(proposal.get("entity_id", "")), str(proposal.get("field_scope", "")))
        if scope_key in seen_scopes:
            dropped.append(
                {
                    "envelope_id": str(proposal.get("envelope_id", "")),
                    "script_step": int(proposal.get("script_step", 0)),
                    "intent_id": str((proposal.get("intent") or {}).get("intent_id", "")),
                    "process_id": str(proposal.get("process_id", "")),
                    "reason": "conflict_first_wins",
                    "scope_key": scope_key,
                }
            )
            continue
        seen_scopes.add(scope_key)
        accepted.append(dict(proposal))
    return {
        "accepted": accepted,
        "dropped": sorted(dropped, key=lambda row: (str(row.get("scope_key", "")), str(row.get("intent_id", "")))),
    }


def _queue_groups(envelopes: List[dict]) -> List[dict]:
    grouped: Dict[int, List[dict]] = {}
    for row in envelopes:
        grouped.setdefault(_submission_tick(row), []).append(dict(row))
    out = []
    for tick in sorted(grouped.keys()):
        rows = sorted(grouped[tick], key=lambda item: (_deterministic_sequence(item), str(item.get("envelope_id", ""))))
        out.append({"submission_tick": int(tick), "envelopes": rows})
    return out


def replay_intent_script_srz(
    repo_root: str,
    universe_state: dict,
    law_profile: dict,
    authority_context: dict,
    intents: List[dict],
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    pack_lock_hash: str = "",
    registry_hashes: dict | None = None,
    worker_count: int = 1,
    logical_shards: int = 1,
) -> Dict[str, object]:
    state = copy.deepcopy(universe_state if isinstance(universe_state, dict) else {})
    authority_origin = str(authority_context.get("authority_origin", "")).strip() or "client"
    starting_tick = simulation_tick(state)
    envelopes = build_intent_envelopes(
        intents=list(intents or []),
        authority_origin=authority_origin,
        source_shard_id=DEFAULT_SHARD_ID,
        target_shard_id=DEFAULT_SHARD_ID,
        starting_tick=starting_tick,
    )

    for index, envelope in enumerate(envelopes):
        valid = validate_intent_envelope(repo_root=repo_root, envelope=envelope)
        if not bool(valid.get("valid", False)):
            refused = refusal(
                "PROCESS_INPUT_INVALID",
                "intent envelope failed schema validation",
                "Fix script intent envelope fields and retry.",
                {
                    "envelope_id": str(envelope.get("envelope_id", "")),
                },
                "$.intent_envelope",
            )
            refused["script_step"] = int(index)
            return refused
        target_shard_id = str(envelope.get("target_shard_id", "")).strip()
        if target_shard_id != DEFAULT_SHARD_ID:
            refused = refusal(
                "SHARD_TARGET_INVALID",
                "target shard '{}' is invalid for single-shard runtime".format(target_shard_id),
                "Route intents to shard.0 until multi-shard runtime support is enabled.",
                {
                    "target_shard_id": target_shard_id,
                    "supported_shard_id": DEFAULT_SHARD_ID,
                },
                "$.intent_envelope.target_shard_id",
            )
            refused["script_step"] = int(index)
            return refused

    shard = build_single_shard(
        universe_state=state,
        authority_origin=authority_origin,
        compatibility_version="1.0.0",
        last_hash_anchor="",
    )
    shard_valid = validate_srz_shard(repo_root=repo_root, shard=shard)
    if not bool(shard_valid.get("valid", False)):
        return refusal(
            "SRZ_SHARD_INVALID",
            "default shard definition failed schema validation",
            "Fix SRZ shard contract fields before replay.",
            {"shard_id": str(shard.get("shard_id", ""))},
            "$.srz_shard",
        )

    script_state_hash_anchors: List[str] = []
    tick_hash_anchors: List[dict] = []
    checkpoint_hashes: List[dict] = []
    resolution_log: List[dict] = []
    last_tick_hash = ""
    last_checkpoint_hash = ""
    scheduler_tick = 0
    activation_policy = dict((policy_context or {}).get("activation_policy") or {})
    checkpoint_interval = checkpoint_interval_from_policy(activation_policy)

    groups = _queue_groups(envelopes)
    envelope_to_step: Dict[str, int] = {}
    for step_index, envelope in enumerate(envelopes):
        envelope_to_step[str(envelope.get("envelope_id", ""))] = int(step_index)

    logical_partition = logical_partition_plan(shard.get("owned_entities") or [], max(1, _as_int(logical_shards, 1)))
    for group in groups:
        scheduler_tick += 1
        submission_tick = int(group.get("submission_tick", 0))
        tick_envelopes = list(group.get("envelopes") or [])

        read_snapshot_hash = canonical_sha256(state)
        proposed = [
            _proposal_from_envelope(
                envelope=row,
                script_step=int(envelope_to_step.get(str(row.get("envelope_id", "")), 0)),
            )
            for row in tick_envelopes
        ]
        proposed = _proposal_order_variation(proposed, worker_count=max(1, _as_int(worker_count, 1)))
        resolved = _resolve_phase(proposed)
        accepted = list(resolved.get("accepted") or [])
        dropped = list(resolved.get("dropped") or [])

        for proposal in accepted:
            executed = execute_intent(
                state=state,
                intent=dict(proposal.get("intent") or {}),
                law_profile=law_profile,
                authority_context=authority_context,
                navigation_indices=navigation_indices,
                policy_context=policy_context,
            )
            if executed.get("result") != "complete":
                refused = dict(executed)
                refused["script_step"] = int(proposal.get("script_step", 0))
                refused["scheduler_tick"] = int(scheduler_tick)
                refused["phase"] = "commit"
                refused["envelope_id"] = str(proposal.get("envelope_id", ""))
                return refused
            script_state_hash_anchors.append(str(executed.get("state_hash_anchor", "")))

        shard["owned_entities"] = owned_entity_ids(state)
        shard["owned_regions"] = owned_region_ids(state)
        pending = []
        for pending_group in groups:
            if int(pending_group.get("submission_tick", 0)) < int(submission_tick):
                continue
            for pending_envelope in pending_group.get("envelopes") or []:
                if int(envelope_to_step.get(str(pending_envelope.get("envelope_id", "")), 0)) <= int(
                    envelope_to_step.get(str(tick_envelopes[-1].get("envelope_id", "")), -1)
                ):
                    continue
                pending.append(str(pending_envelope.get("envelope_id", "")))
        shard["process_queue"] = sorted(set(token for token in pending if token))
        current_tick = simulation_tick(state)
        tick_hash = per_tick_hash(
            universe_state=state,
            shards=[shard],
            pack_lock_hash=str(pack_lock_hash),
            registry_hashes=dict(registry_hashes or {}),
            last_tick_hash=str(last_tick_hash),
        )
        shard["last_hash_anchor"] = tick_hash
        current_composite = composite_hash([shard])
        tick_hash_row = {
            "scheduler_tick": int(scheduler_tick),
            "submission_tick": int(submission_tick),
            "simulation_tick": int(current_tick),
            "tick_hash": str(tick_hash),
            "composite_hash": str(current_composite),
        }
        tick_hash_anchors.append(tick_hash_row)
        last_tick_hash = str(tick_hash)

        if int(scheduler_tick % checkpoint_interval) == 0:
            cp_hash = checkpoint_hash(
                tick=int(scheduler_tick),
                tick_hash=str(tick_hash),
                previous_checkpoint_hash=str(last_checkpoint_hash),
                composite=str(current_composite),
            )
            last_checkpoint_hash = cp_hash
            checkpoint_hashes.append(
                {
                    "scheduler_tick": int(scheduler_tick),
                    "simulation_tick": int(current_tick),
                    "checkpoint_hash": str(cp_hash),
                    "tick_hash": str(tick_hash),
                    "composite_hash": str(current_composite),
                }
            )

        resolution_log.append(
            {
                "scheduler_tick": int(scheduler_tick),
                "submission_tick": int(submission_tick),
                "read_snapshot_hash": str(read_snapshot_hash),
                "proposal_count": len(proposed),
                "accepted_count": len(accepted),
                "dropped_count": len(dropped),
                "dropped": list(dropped),
            }
        )

    final_composite = composite_hash([shard])
    return {
        "result": "complete",
        "universe_state": state,
        "state_hash_anchors": script_state_hash_anchors,
        "tick_hash_anchors": tick_hash_anchors,
        "checkpoint_hashes": checkpoint_hashes,
        "composite_hash": final_composite,
        "final_state_hash": canonical_sha256(state),
        "srz": {
            "schema_version": "1.0.0",
            "runtime_mode": "single_shard",
            "scheduler_phase_order": ["read", "propose", "resolve", "commit"],
            "worker_count_requested": max(1, _as_int(worker_count, 1)),
            "worker_count_effective": 1,
            "logical_shard_count_requested": max(1, _as_int(logical_shards, 1)),
            "logical_partition_plan": logical_partition,
            "active_shards": [
                {
                    "shard_id": str(shard.get("shard_id", "")),
                    "owned_entities_count": len(list(shard.get("owned_entities") or [])),
                    "owned_regions_count": len(list(shard.get("owned_regions") or [])),
                    "process_queue_count": len(list(shard.get("process_queue") or [])),
                    "last_hash_anchor": str(shard.get("last_hash_anchor", "")),
                }
            ],
            "resolution_log": resolution_log,
        },
    }


def execute_single_intent_srz(
    repo_root: str,
    universe_state: dict,
    law_profile: dict,
    authority_context: dict,
    intent: dict,
    navigation_indices: dict | None = None,
    policy_context: dict | None = None,
    pack_lock_hash: str = "",
    registry_hashes: dict | None = None,
    worker_count: int = 1,
) -> Dict[str, object]:
    result = replay_intent_script_srz(
        repo_root=repo_root,
        universe_state=universe_state,
        law_profile=law_profile,
        authority_context=authority_context,
        intents=[dict(intent or {})],
        navigation_indices=navigation_indices,
        policy_context=policy_context,
        pack_lock_hash=pack_lock_hash,
        registry_hashes=dict(registry_hashes or {}),
        worker_count=max(1, _as_int(worker_count, 1)),
        logical_shards=1,
    )
    if result.get("result") != "complete":
        return result
    state_anchors = list(result.get("state_hash_anchors") or [])
    tick_anchors = list(result.get("tick_hash_anchors") or [])
    tick_value = 0
    if tick_anchors:
        tick_value = _as_int((tick_anchors[-1] or {}).get("simulation_tick", 0), 0)
    return {
        "result": "complete",
        "universe_state": dict(result.get("universe_state") or {}),
        "state_hash_anchor": str(state_anchors[-1]) if state_anchors else "",
        "tick": int(tick_value),
        "tick_hash_anchor": str((tick_anchors[-1] or {}).get("tick_hash", "")) if tick_anchors else "",
        "composite_hash": str(result.get("composite_hash", "")),
        "srz": dict(result.get("srz") or {}),
    }
