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
    "process.srz_transfer_entity": 15,
    "process.time_control_set_rate": 20,
    "process.time_set_rate": 20,
    "process.time_pause": 20,
    "process.time_resume": 20,
    "process.time_branch_from_checkpoint": 20,
    "process.faction_create": 22,
    "process.faction_dissolve": 22,
    "process.affiliation_join": 23,
    "process.affiliation_leave": 23,
    "process.affiliation_change_micro": 23,
    "process.cohort_create": 24,
    "process.cohort_expand_to_micro": 24,
    "process.cohort_collapse_from_micro": 24,
    "process.territory_claim": 24,
    "process.territory_release": 24,
    "process.diplomacy_set_relation": 25,
    "process.order_create": 25,
    "process.order_cancel": 25,
    "process.order_tick": 26,
    "process.cohort_relocate": 26,
    "process.role_assign": 26,
    "process.role_revoke": 26,
    "process.manifest_create": 26,
    "process.manifest_tick": 27,
    "process.control_bind_camera": 25,
    "process.control_unbind_camera": 25,
    "process.control_possess_agent": 25,
    "process.control_release_agent": 25,
    "process.control_set_view_lens": 25,
    "process.cosmetic_assign": 25,
    "process.camera_bind_target": 25,
    "process.camera_unbind_target": 25,
    "process.camera_set_view_mode": 25,
    "process.camera_set_lens": 25,
    "process.camera_teleport": 30,
    "process.agent_rotate": 33,
    "process.agent_move": 34,
    "process.body_move_attempt": 35,
    "process.camera_move": 40,
}

PROCESS_ENTITY_SCOPE = {
    "process.region_management_tick": "region.manager",
    "process.srz_transfer_entity": "agent.transfer",
    "process.time_control_set_rate": "time.control",
    "process.time_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.time_branch_from_checkpoint": "time.branch",
    "process.faction_create": "faction.create",
    "process.faction_dissolve": "faction.unknown",
    "process.affiliation_join": "subject.unknown",
    "process.affiliation_leave": "subject.unknown",
    "process.affiliation_change_micro": "subject.unknown",
    "process.cohort_create": "cohort.create",
    "process.cohort_expand_to_micro": "cohort.unknown",
    "process.cohort_collapse_from_micro": "cohort.unknown",
    "process.territory_claim": "territory.unknown",
    "process.territory_release": "territory.unknown",
    "process.diplomacy_set_relation": "diplomacy.unknown",
    "process.order_create": "order.queue",
    "process.order_cancel": "order.queue",
    "process.order_tick": "order.queue",
    "process.cohort_relocate": "cohort.unknown",
    "process.role_assign": "institution.unknown",
    "process.role_revoke": "institution.unknown",
    "process.manifest_create": "logistics.manifest.create",
    "process.manifest_tick": "logistics.manifest.tick",
    "process.control_bind_camera": "controller.binding.camera",
    "process.control_unbind_camera": "controller.binding.camera",
    "process.control_possess_agent": "controller.binding.possess",
    "process.control_release_agent": "controller.binding.possess",
    "process.control_set_view_lens": "camera.main",
    "process.cosmetic_assign": "agent.unknown",
    "process.camera_bind_target": "controller.binding.camera",
    "process.camera_unbind_target": "controller.binding.camera",
    "process.camera_set_view_mode": "camera.main",
    "process.camera_set_lens": "camera.main",
    "process.camera_teleport": "camera.main",
    "process.agent_rotate": "agent.unknown",
    "process.agent_move": "agent.unknown",
    "process.body_move_attempt": "body.unknown",
    "process.camera_move": "camera.main",
}

PROCESS_FIELD_SCOPE = {
    "process.region_management_tick": "region.state",
    "process.srz_transfer_entity": "agent.shard",
    "process.time_control_set_rate": "time.control",
    "process.time_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.time_branch_from_checkpoint": "time.branch",
    "process.faction_create": "civ.faction.state",
    "process.faction_dissolve": "civ.faction.state",
    "process.affiliation_join": "civ.affiliation.state",
    "process.affiliation_leave": "civ.affiliation.state",
    "process.affiliation_change_micro": "civ.affiliation.state",
    "process.cohort_create": "civ.cohort.state",
    "process.cohort_expand_to_micro": "civ.cohort.state",
    "process.cohort_collapse_from_micro": "civ.cohort.state",
    "process.territory_claim": "civ.territory.state",
    "process.territory_release": "civ.territory.state",
    "process.diplomacy_set_relation": "civ.diplomacy.state",
    "process.order_create": "civ.order.state",
    "process.order_cancel": "civ.order.state",
    "process.order_tick": "civ.order.state",
    "process.cohort_relocate": "civ.cohort.state",
    "process.role_assign": "civ.institution.state",
    "process.role_revoke": "civ.institution.state",
    "process.manifest_create": "logistics.manifest.state",
    "process.manifest_tick": "logistics.manifest.state",
    "process.control_bind_camera": "control.binding.camera",
    "process.control_unbind_camera": "control.binding.camera",
    "process.control_possess_agent": "control.binding.possess",
    "process.control_release_agent": "control.binding.possess",
    "process.control_set_view_lens": "camera.lens",
    "process.cosmetic_assign": "representation.cosmetic",
    "process.camera_bind_target": "control.binding.camera",
    "process.camera_unbind_target": "control.binding.camera",
    "process.camera_set_view_mode": "camera.view_mode",
    "process.camera_set_lens": "camera.lens",
    "process.camera_teleport": "camera.transform",
    "process.agent_rotate": "agent.orientation",
    "process.agent_move": "body.transform",
    "process.body_move_attempt": "body.transform",
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
    entity_scope = str(PROCESS_ENTITY_SCOPE.get(process_id, "entity.unknown"))
    if process_id == "process.body_move_attempt":
        body_id = str(inputs.get("body_id", "") or inputs.get("target_body_id", "")).strip()
        if body_id:
            entity_scope = body_id
    if process_id in ("process.agent_move", "process.agent_rotate", "process.srz_transfer_entity"):
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "") or inputs.get("target_id", "")).strip()
        if agent_id:
            entity_scope = agent_id
    if process_id in (
        "process.control_bind_camera",
        "process.control_unbind_camera",
        "process.control_set_view_lens",
        "process.camera_bind_target",
        "process.camera_unbind_target",
        "process.camera_set_view_mode",
        "process.camera_set_lens",
    ):
        camera_id = str(inputs.get("camera_id", "")).strip() or "camera.main"
        entity_scope = camera_id
    if process_id == "process.cosmetic_assign":
        agent_id = str(inputs.get("agent_id", "") or inputs.get("target_agent_id", "") or inputs.get("target_id", "")).strip()
        if agent_id:
            entity_scope = agent_id
    if process_id == "process.faction_create":
        founder_agent_id = str(inputs.get("founder_agent_id", "")).strip()
        if founder_agent_id:
            entity_scope = "faction.create.{}".format(founder_agent_id)
    if process_id == "process.faction_dissolve":
        faction_id = str(inputs.get("faction_id", "")).strip()
        if faction_id:
            entity_scope = faction_id
    if process_id in ("process.affiliation_join", "process.affiliation_leave"):
        subject_id = str(inputs.get("subject_id", "")).strip()
        if subject_id:
            entity_scope = subject_id
    if process_id == "process.affiliation_change_micro":
        subject_id = str(inputs.get("subject_id", "")).strip()
        if subject_id:
            entity_scope = subject_id
    if process_id in ("process.cohort_expand_to_micro", "process.cohort_collapse_from_micro"):
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        if cohort_id:
            entity_scope = cohort_id
    if process_id == "process.cohort_create":
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        if cohort_id:
            entity_scope = cohort_id
        else:
            location_ref = str(inputs.get("location_ref", "") or inputs.get("region_id", "")).strip()
            if location_ref:
                entity_scope = "cohort.create.{}".format(location_ref)
    if process_id in ("process.territory_claim", "process.territory_release"):
        territory_id = str(inputs.get("territory_id", "")).strip()
        if territory_id:
            entity_scope = territory_id
    if process_id == "process.diplomacy_set_relation":
        faction_a = str(inputs.get("faction_a", "")).strip()
        faction_b = str(inputs.get("faction_b", "")).strip()
        if faction_a and faction_b:
            left = faction_a if faction_a <= faction_b else faction_b
            right = faction_b if faction_a <= faction_b else faction_a
            entity_scope = "diplo.{}::{}".format(left, right)
    if process_id == "process.order_create":
        target_kind = str(inputs.get("target_kind", "")).strip()
        target_id = str(inputs.get("target_id", "")).strip()
        if target_kind and target_id:
            entity_scope = "{}.{}".format(target_kind, target_id)
    if process_id == "process.order_cancel":
        order_id = str(inputs.get("order_id", "")).strip()
        if order_id:
            entity_scope = order_id
    if process_id == "process.order_tick":
        entity_scope = "order.tick"
    if process_id == "process.cohort_relocate":
        cohort_id = str(inputs.get("cohort_id", "")).strip()
        if cohort_id:
            entity_scope = cohort_id
    if process_id == "process.role_assign":
        institution_id = str(inputs.get("institution_id", "")).strip()
        subject_id = str(inputs.get("subject_id", "")).strip()
        if institution_id and subject_id:
            entity_scope = "role_assign.{}::{}".format(institution_id, subject_id)
    if process_id == "process.role_revoke":
        assignment_id = str(inputs.get("assignment_id", "")).strip()
        if assignment_id:
            entity_scope = assignment_id
    if process_id == "process.manifest_create":
        from_node_id = str(inputs.get("from_node_id", "")).strip()
        to_node_id = str(inputs.get("to_node_id", "")).strip()
        batch_id = str(inputs.get("batch_id", "")).strip()
        if from_node_id and to_node_id and batch_id:
            entity_scope = "manifest.create.{}::{}::{}".format(from_node_id, to_node_id, batch_id)
    if process_id == "process.manifest_tick":
        graph_id = str(inputs.get("graph_id", "")).strip()
        if graph_id:
            entity_scope = "manifest.tick.{}".format(graph_id)
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
        "entity_id": entity_scope,
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
    checkpoint_snapshots: List[dict] = []
    accepted_envelopes: List[dict] = []
    resolution_log: List[dict] = []
    last_tick_hash = ""
    last_checkpoint_hash = ""
    scheduler_tick = 0
    activation_policy = dict((policy_context or {}).get("activation_policy") or {})
    time_control_policy = dict((policy_context or {}).get("time_control_policy") or {})
    checkpoint_interval = checkpoint_interval_from_policy(
        activation_policy,
        time_control_policy=time_control_policy,
    )

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
        tick_ledger_hash = ""

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
            token = str(executed.get("ledger_hash", "")).strip()
            if token:
                tick_ledger_hash = token
            accepted_envelopes.append(
                {
                    "scheduler_tick": int(scheduler_tick),
                    "submission_tick": int(submission_tick),
                    "envelope_id": str(proposal.get("envelope_id", "")),
                    "intent_id": str((proposal.get("intent") or {}).get("intent_id", "")),
                    "process_id": str(proposal.get("process_id", "")),
                    "deterministic_sequence_number": int(proposal.get("intent_sequence", 0) or 0),
                }
            )

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
        transition_event_hash = canonical_sha256(
            sorted(
                (
                    dict(item)
                    for item in list((dict(state.get("performance_state") or {})).get("transition_events") or [])
                    if isinstance(item, dict)
                ),
                key=lambda item: (
                    int(item.get("tick", 0) or 0),
                    str(item.get("shard_id", "")),
                    str(item.get("region_id", "")),
                    str(item.get("event_id", "")),
                ),
            )
        )
        tick_hash = per_tick_hash(
            universe_state=state,
            shards=[shard],
            pack_lock_hash=str(pack_lock_hash),
            registry_hashes=dict(registry_hashes or {}),
            last_tick_hash=str(last_tick_hash),
            ledger_hash=str(tick_ledger_hash),
            transition_event_hash=str(transition_event_hash),
        )
        shard["last_hash_anchor"] = tick_hash
        current_composite = composite_hash([shard])
        tick_hash_row = {
            "scheduler_tick": int(scheduler_tick),
            "submission_tick": int(submission_tick),
            "simulation_tick": int(current_tick),
            "ledger_hash": str(tick_ledger_hash),
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
            checkpoint_snapshots.append(
                {
                    "scheduler_tick": int(scheduler_tick),
                    "simulation_tick": int(current_tick),
                    "checkpoint_hash": str(cp_hash),
                    "tick_hash": str(tick_hash),
                    "composite_hash": str(current_composite),
                    "ledger_hash": str(tick_ledger_hash or ""),
                    "truth_hash_anchor": canonical_sha256(state),
                    "state_snapshot": copy.deepcopy(state),
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
        "checkpoint_snapshots": checkpoint_snapshots,
        "accepted_envelopes": sorted(
            accepted_envelopes,
            key=lambda row: (
                int(row.get("submission_tick", 0) or 0),
                int(row.get("deterministic_sequence_number", 0) or 0),
                str(row.get("envelope_id", "")),
            ),
        ),
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
