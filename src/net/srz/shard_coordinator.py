"""Deterministic SRZ hybrid shard coordinator (single-process multi-shard)."""

from __future__ import annotations

import copy
import os
from typing import Dict, List, Tuple

from src.net.anti_cheat import (
    action_blocks_submission,
    action_drops_without_refusal,
    check_authority_integrity,
    check_behavioral_detection,
    check_client_attestation,
    check_input_integrity,
    check_replay_protection,
    check_sequence_integrity,
    check_state_integrity,
    ensure_runtime_channels,
    export_proof_artifacts,
    refusal_reason_from_action,
)
from src.control.proof import (
    build_control_proof_bundle_from_markers,
    collect_control_decision_markers,
)
from src.mobility import compute_mobility_proof_hashes
from src.reality.ledger import finalize_noop_tick
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.sessionx.boundary_debug import debug_assert_after_execute
from tools.xstack.sessionx.common import norm, refusal, write_canonical_json
from tools.xstack.sessionx.observation import build_truth_model, observe_truth
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.sessionx.srz import simulation_tick

from .routing import DEFAULT_SHARD_ID, route_intent_envelope, shard_index


PROCESS_SCOPE_BY_ID = {
    "process.region_management_tick": "region.state",
    "process.srz_transfer_entity": "agent.shard",
    "process.time_control_set_rate": "time.control",
    "process.time_set_rate": "time.control",
    "process.time_pause": "time.control",
    "process.time_resume": "time.control",
    "process.time_branch_from_checkpoint": "time.branch",
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

PROCESS_OWNER_OBJECT = {
    "process.region_management_tick": "camera.main",
    "process.srz_transfer_entity": "agent.unknown",
    "process.time_control_set_rate": "camera.main",
    "process.time_set_rate": "camera.main",
    "process.time_pause": "camera.main",
    "process.time_resume": "camera.main",
    "process.time_branch_from_checkpoint": "camera.main",
    "process.control_bind_camera": "camera.main",
    "process.control_unbind_camera": "camera.main",
    "process.control_possess_agent": "camera.main",
    "process.control_release_agent": "camera.main",
    "process.control_set_view_lens": "camera.main",
    "process.cosmetic_assign": "agent.unknown",
    "process.camera_bind_target": "camera.main",
    "process.camera_unbind_target": "camera.main",
    "process.camera_set_view_mode": "camera.main",
    "process.camera_set_lens": "camera.main",
    "process.camera_teleport": "camera.main",
    "process.agent_rotate": "agent.unknown",
    "process.agent_move": "agent.unknown",
    "process.body_move_attempt": "body.unknown",
    "process.camera_move": "camera.main",
}

PROCESS_PRIORITY = {
    "process.region_management_tick": 10,
    "process.srz_transfer_entity": 15,
    "process.time_control_set_rate": 20,
    "process.time_set_rate": 20,
    "process.time_pause": 20,
    "process.time_resume": 20,
    "process.time_branch_from_checkpoint": 20,
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

MOVEMENT_PROCESS_IDS = ("process.agent_move", "process.agent_rotate")
TIME_CONTROL_PROCESS_IDS = (
    "process.time_control_set_rate",
    "process.time_set_rate",
    "process.time_pause",
    "process.time_resume",
    "process.time_branch_from_checkpoint",
)


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


def _vector3_int(payload: object) -> dict:
    row = dict(payload) if isinstance(payload, dict) else {}
    return {
        "x": _as_int(row.get("x", 0), 0),
        "y": _as_int(row.get("y", 0), 0),
        "z": _as_int(row.get("z", 0), 0),
    }


def _movement_limits(runtime: dict) -> dict:
    ext = dict((runtime.get("anti_cheat") or {}).get("extensions") or {})
    return {
        "max_intents_per_tick": max(1, _as_int(ext.get("movement_intents_per_tick_max", 3), 3)),
        "max_displacement_mm_per_tick": max(1, _as_int(ext.get("movement_max_displacement_mm_per_tick", 8000), 8000)),
    }


def _movement_requested_distance(inputs: dict) -> Tuple[int, int]:
    payload = dict(inputs if isinstance(inputs, dict) else {})
    local = _vector3_int(payload.get("move_vector_local"))
    if local == {"x": 0, "y": 0, "z": 0}:
        local = _vector3_int(payload.get("delta_local_mm"))
    speed_scalar = max(0, _as_int(payload.get("speed_scalar", 1000), 1000))
    dt_ticks = max(1, _as_int(payload.get("tick_duration", payload.get("dt_ticks", 1)), 1))
    scaled = {
        "x": int(int(local["x"]) * int(speed_scalar) // 1000),
        "y": int(int(local["y"]) * int(speed_scalar) // 1000),
        "z": int(int(local["z"]) * int(speed_scalar) // 1000),
    }
    return int(abs(scaled["x"]) + abs(scaled["y"]) + abs(scaled["z"])), int(dt_ticks)


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


def _session_extensions(runtime: dict) -> dict:
    session_spec = dict(runtime.get("session_spec") or {})
    extensions = session_spec.get("extensions")
    if not isinstance(extensions, dict):
        return {}
    return dict(extensions)


def _session_time_control_policy_id(runtime: dict) -> str:
    session_spec = dict(runtime.get("session_spec") or {})
    return str(session_spec.get("time_control_policy_id", "") or "time.policy.null").strip() or "time.policy.null"


def _time_control_policy(runtime: dict, policy_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("time_control_policy_registry") or {})
    rows = list(registry.get("policies") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("time_control_policy_id", ""))):
        if str(row.get("time_control_policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {
        "time_control_policy_id": str(policy_id),
        "allow_variable_dt": False,
        "allow_pause": True,
        "allow_rate_change": False,
        "allowed_rate_range": {"min": 1000, "max": 1000},
        "dt_quantization_rule_id": "dt.rule.single_tick",
        "checkpoint_interval_ticks": 4,
        "compaction_policy_id": "compaction.policy.keep_all",
        "extensions": {"allow_branching": False, "allow_branch_mid_session": False},
    }


def _dt_quantization_rule(runtime: dict, dt_rule_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("dt_quantization_rule_registry") or {})
    rows = list(registry.get("rules") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("dt_rule_id", ""))):
        if str(row.get("dt_rule_id", "")).strip() == str(dt_rule_id).strip():
            return dict(row)
    return {
        "dt_rule_id": str(dt_rule_id).strip() or "dt.rule.single_tick",
        "allowed_dt_values": [1000],
        "default_dt": 1000,
        "deterministic_rounding_rule": "round.nearest.lower_tie",
        "extensions": {},
    }


def _physics_profile(runtime: dict) -> dict:
    physics_profile_id = str((runtime.get("universe_identity") or {}).get("physics_profile_id", "")).strip()
    registry = dict((runtime.get("registry_payloads") or {}).get("universe_physics_profile_registry") or {})
    rows = list(registry.get("physics_profiles") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("physics_profile_id", ""))):
        if str(row.get("physics_profile_id", "")).strip() == physics_profile_id:
            return dict(row)
    return {}


def _session_transition_policy_id(runtime: dict, profile_row: dict) -> str:
    selected_transition = dict(runtime.get("selected_transition_policy") or {})
    token = str(selected_transition.get("transition_policy_id", "")).strip()
    if token:
        return token
    session_spec = dict(runtime.get("session_spec") or {})
    token = str(session_spec.get("transition_policy_id", "")).strip()
    if token:
        return token
    extensions = dict((profile_row or {}).get("extensions") or {})
    token = str(extensions.get("default_transition_policy_id", "")).strip()
    if token:
        return token
    return "transition.policy.null"


def _transition_policy(runtime: dict, policy_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("transition_policy_registry") or {})
    rows = list(registry.get("policies") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("transition_policy_id", ""))):
        if str(row.get("transition_policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {
        "transition_policy_id": str(policy_id).strip() or "transition.policy.null",
        "description": "fallback deterministic transition policy",
        "max_micro_regions": 0,
        "max_micro_entities": 0,
        "hysteresis_rules": {"min_transition_interval_ticks": 0},
        "arbitration_rule_id": "arb.priority_by_distance",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {},
    }


def _budget_envelope(runtime: dict, envelope_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("budget_envelope_registry") or {})
    rows = list(registry.get("envelopes") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("envelope_id", ""))):
        if str(row.get("envelope_id", "")).strip() == str(envelope_id).strip():
            return dict(row)
    return {
        "envelope_id": str(envelope_id).strip() or "budget.null",
        "max_micro_entities_per_shard": 0,
        "max_micro_regions_per_shard": 0,
        "max_solver_cost_units_per_tick": 0,
        "max_inspection_cost_units_per_tick": 0,
        "extensions": {},
    }


def _arbitration_policy(runtime: dict, policy_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("arbitration_policy_registry") or {})
    rows = list(registry.get("policies") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("arbitration_policy_id", ""))):
        if str(row.get("arbitration_policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {
        "arbitration_policy_id": str(policy_id).strip() or "arb.equal_share",
        "mode": "equal_share",
        "weight_source": "derived",
        "tie_break_rule_id": "tie.player_region_tick",
        "extensions": {},
    }


def _inspection_cache_policy(runtime: dict, policy_id: str) -> dict:
    registry = dict((runtime.get("registry_payloads") or {}).get("inspection_cache_policy_registry") or {})
    rows = list(registry.get("policies") or [])
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("cache_policy_id", ""))):
        if str(row.get("cache_policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {
        "cache_policy_id": str(policy_id).strip() or "cache.off",
        "enable_caching": False,
        "invalidation_rules": [],
        "max_cache_entries": 0,
        "eviction_rule_id": "evict.none",
        "extensions": {},
    }


def _is_unauthorized_time_control_refusal(process_id: str, reason_code: str) -> bool:
    token = str(process_id).strip()
    reason = str(reason_code).strip()
    if token not in set(TIME_CONTROL_PROCESS_IDS):
        return False
    if reason in {
        "ENTITLEMENT_MISSING",
        "PROCESS_FORBIDDEN",
        "refusal.control.entitlement_missing",
        "refusal.control.law_forbidden",
    }:
        return True
    return reason.startswith("refusal.time.")


def _runtime_policy_context(runtime: dict, *, active_shard_id: str = "") -> dict:
    server = _runtime_server(runtime)
    runtime_conservation = server.get("conservation_runtime_by_shard")
    if not isinstance(runtime_conservation, dict):
        runtime_conservation = {}
        server["conservation_runtime_by_shard"] = runtime_conservation
    runtime["server"] = server
    physics_profile_id = str((runtime.get("universe_identity") or {}).get("physics_profile_id", "")).strip()
    if not physics_profile_id:
        physics_profile_id = "physics.null"
    profile_row = _physics_profile(runtime)
    tier_taxonomy_id = str(runtime.get("selected_tier_taxonomy_id", "")).strip() or str(profile_row.get("tier_taxonomy_id", "")).strip() or "tiers.null"
    server_profile = dict(runtime.get("server_profile") or {})
    time_control_policy_id = _session_time_control_policy_id(runtime=runtime)
    selected_time_policy = _time_control_policy(runtime=runtime, policy_id=time_control_policy_id)
    transition_policy_id = _session_transition_policy_id(runtime=runtime, profile_row=profile_row)
    selected_transition_policy = _transition_policy(runtime=runtime, policy_id=transition_policy_id)
    budget_envelope_id = str(profile_row.get("budget_envelope_id", "")).strip() or "budget.null"
    arbitration_policy_id = str(profile_row.get("arbitration_policy_id", "")).strip() or "arb.equal_share"
    inspection_cache_policy_id = str(profile_row.get("inspection_cache_policy_id", "")).strip() or "cache.off"
    selected_budget_envelope = _budget_envelope(runtime=runtime, envelope_id=budget_envelope_id)
    selected_arbitration_policy = _arbitration_policy(runtime=runtime, policy_id=arbitration_policy_id)
    selected_inspection_cache_policy = _inspection_cache_policy(runtime=runtime, policy_id=inspection_cache_policy_id)
    dt_rule_id = str(selected_time_policy.get("dt_quantization_rule_id", "")).strip() or "dt.rule.single_tick"
    selected_dt_rule = _dt_quantization_rule(runtime=runtime, dt_rule_id=dt_rule_id)
    inspection_runtime_budget_state = server.get("inspection_runtime_budget_state")
    if not isinstance(inspection_runtime_budget_state, dict):
        inspection_runtime_budget_state = {"used_by_tick": {}}
        server["inspection_runtime_budget_state"] = inspection_runtime_budget_state
    inspection_cache_state = server.get("inspection_cache_state")
    if not isinstance(inspection_cache_state, dict):
        inspection_cache_state = {"entries_by_key": {}}
        server["inspection_cache_state"] = inspection_cache_state
    runtime["server"] = server

    context = {
        **dict(runtime.get("registry_payloads") or {}),
        "shard_map": dict(runtime.get("shard_map") or {}),
        "active_shard_id": str(active_shard_id).strip() or DEFAULT_SHARD_ID,
        "physics_profile_id": physics_profile_id,
        "pack_lock_hash": str(((runtime.get("lock_payload") or {}).get("pack_lock_hash", ""))),
        "conservation_runtime_by_shard": runtime_conservation,
        "control_policy": dict(runtime.get("control_policy") or {}),
        "allow_cross_shard_collision": bool((runtime.get("control_policy") or {}).get("allow_cross_shard_collision", False)),
        "cosmetic_policy_id": str((runtime.get("control_policy") or {}).get("cosmetic_policy_id", "")),
        "server_policy": dict(runtime.get("server_policy") or {}),
        "server_profile": server_profile,
        "server_profile_id": str(server_profile.get("server_profile_id", "")),
        "time_control_policy_id": str(time_control_policy_id),
        "time_control_policy": dict(selected_time_policy),
        "tier_taxonomy_id": str(tier_taxonomy_id),
        "transition_policy_id": str(transition_policy_id),
        "transition_policy": dict(selected_transition_policy),
        "budget_envelope_id": str(budget_envelope_id),
        "budget_envelope": dict(selected_budget_envelope),
        "arbitration_policy_id": str(arbitration_policy_id),
        "arbitration_policy": dict(selected_arbitration_policy),
        "inspection_cache_policy_id": str(inspection_cache_policy_id),
        "inspection_cache_policy": dict(selected_inspection_cache_policy),
        "inspection_runtime_budget_state": inspection_runtime_budget_state,
        "inspection_cache_state": inspection_cache_state,
        "dt_quantization_rule_id": str(dt_rule_id),
        "dt_quantization_rule": dict(selected_dt_rule),
        "resolved_packs": list(((runtime.get("lock_payload") or {}).get("resolved_packs") or [])),
    }
    session_spec = dict(runtime.get("session_spec") or {})
    parameter_bundle_id = str(session_spec.get("parameter_bundle_id", "")).strip()
    if parameter_bundle_id:
        context["parameter_bundle_id"] = parameter_bundle_id
    session_ext = _session_extensions(runtime)
    demography_policy_id = str(session_ext.get("demography_policy_id", "")).strip()
    if demography_policy_id:
        context["demography_policy_id"] = demography_policy_id
    migration_model_id = str(session_ext.get("migration_model_id", "")).strip()
    if migration_model_id:
        context["migration_model_id"] = migration_model_id
    return context


def _is_ranked_runtime(runtime: dict) -> bool:
    profile_id = str((runtime.get("server_profile") or {}).get("server_profile_id", "")).strip().lower()
    anti_cheat_policy_id = str((runtime.get("anti_cheat") or {}).get("policy_id", "")).strip().lower()
    return ("rank" in profile_id) or ("rank" in anti_cheat_policy_id)


def _conservation_allowed_exception_types(runtime: dict, contract_set_id: str, quantity_id: str) -> List[str]:
    registry = dict((runtime.get("registry_payloads") or {}).get("conservation_contract_set_registry") or {})
    rows = list(registry.get("contract_sets") or [])
    for contract_row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("contract_set_id", ""))):
        if str(contract_row.get("contract_set_id", "")).strip() != str(contract_set_id).strip():
            continue
        quantity_rows = list(contract_row.get("quantities") or [])
        for quantity_row in sorted((item for item in quantity_rows if isinstance(item, dict)), key=lambda item: str(item.get("quantity_id", ""))):
            if str(quantity_row.get("quantity_id", "")).strip() != str(quantity_id).strip():
                continue
            return _sorted_tokens(list(quantity_row.get("allowed_exception_types") or []))
        break
    return []


def _sync_conservation_ledgers_to_server(runtime: dict, policy_context: dict) -> List[dict]:
    server = _runtime_server(runtime)
    runtime_by_shard = dict(policy_context.get("conservation_runtime_by_shard") or {})
    rows: List[dict] = []
    for shard_id in sorted(runtime_by_shard.keys()):
        shard_runtime = dict(runtime_by_shard.get(shard_id) or {})
        for ledger_row in list(shard_runtime.get("ledger_rows") or []):
            if isinstance(ledger_row, dict):
                rows.append(dict(ledger_row))
    rows = sorted(
        rows,
        key=lambda row: (
            int(_as_int(row.get("tick", 0), 0)),
            str(row.get("shard_id", "")),
            str(row.get("ledger_hash", "")),
        ),
    )
    server["conservation_ledgers"] = rows[-1024:]
    runtime["server"] = server
    return list(server.get("conservation_ledgers") or [])


def _emit_conservation_anti_cheat_signals(
    repo_root: str,
    runtime: dict,
    tick: int,
    ledger_rows: List[dict],
) -> None:
    if not ledger_rows:
        return
    latest = dict(ledger_rows[-1] or {})
    entries = list(latest.get("entries") or [])
    contract_set_id = str(latest.get("contract_set_id", "")).strip()
    if not contract_set_id:
        return

    meta_override_count = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        quantity_id = str(entry.get("quantity_id", "")).strip()
        exception_type_id = str(entry.get("exception_type_id", "")).strip()
        if exception_type_id == "exception.meta_law_override":
            meta_override_count += 1
        if not quantity_id or not exception_type_id:
            continue
        allowed = _conservation_allowed_exception_types(
            runtime=runtime,
            contract_set_id=contract_set_id,
            quantity_id=quantity_id,
        )
        if exception_type_id in set(allowed):
            continue
        check_behavioral_detection(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(tick),
            peer_id=str((_runtime_server(runtime).get("peer_id", "peer.server"))),
            suspicious=True,
            reason_code="ac.conservation.exception_type_unexpected",
            evidence=[
                "contract_set_id={}".format(contract_set_id),
                "quantity_id={}".format(quantity_id),
                "exception_type_id={}".format(exception_type_id),
                "ledger_hash={}".format(str(latest.get("ledger_hash", ""))),
            ],
            default_action_token="audit",
        )

    if _is_ranked_runtime(runtime) and int(meta_override_count) > 0:
        check_behavioral_detection(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(tick),
            peer_id=str((_runtime_server(runtime).get("peer_id", "peer.server"))),
            suspicious=True,
            reason_code="ac.conservation.meta_law_override_ranked",
            evidence=[
                "meta_law_override_count={}".format(int(meta_override_count)),
                "contract_set_id={}".format(contract_set_id),
                "ledger_hash={}".format(str(latest.get("ledger_hash", ""))),
            ],
            default_action_token="audit",
        )


def _law_allows_process(law_profile: dict, process_id: str) -> bool:
    allowed = _sorted_tokens(list((law_profile or {}).get("allowed_processes") or []))
    forbidden = _sorted_tokens(list((law_profile or {}).get("forbidden_processes") or []))
    return bool(process_id in set(allowed) and process_id not in set(forbidden))


def _hybrid_demography_authority(runtime: dict) -> Tuple[dict, dict]:
    clients = _runtime_clients(runtime)
    if not clients:
        return {}, {}
    server_peer_id = str((_runtime_server(runtime) or {}).get("peer_id", "")).strip()
    selected_peer_id = server_peer_id if server_peer_id and server_peer_id in clients else sorted(clients.keys())[0]
    selected_client = dict(clients.get(selected_peer_id) or {})
    law_profile = dict(selected_client.get("law_profile") or {})
    authority = dict(selected_client.get("authority_context") or {})
    entitlements = _sorted_tokens(list(authority.get("entitlements") or []) + ["session.boot"])
    authority["authority_origin"] = "server"
    authority["peer_id"] = server_peer_id or "peer.server"
    authority["law_profile_id"] = str(law_profile.get("law_profile_id", "")).strip() or str(authority.get("law_profile_id", "")).strip()
    authority["entitlements"] = entitlements
    authority["privilege_level"] = "system"
    scope = authority.get("epistemic_scope")
    if not isinstance(scope, dict):
        authority["epistemic_scope"] = {
            "scope_id": "scope.server.hybrid",
            "visibility_level": "nondiegetic",
        }
    return law_profile, authority


def _run_hybrid_demography_tick(state: dict, runtime: dict, tick: int, shard_id: str) -> Dict[str, object]:
    process_id = "process.demography_tick"
    law_profile, authority_context = _hybrid_demography_authority(runtime)
    if not law_profile or not authority_context:
        return {"result": "skipped", "reason": "missing_server_authority"}
    if not _law_allows_process(law_profile, process_id):
        return {"result": "skipped", "reason": "law_forbidden"}
    session_ext = _session_extensions(runtime)
    inputs: Dict[str, object] = {}
    demography_policy_id = str(session_ext.get("demography_policy_id", "")).strip()
    if demography_policy_id:
        inputs["demography_policy_id"] = demography_policy_id
    intent_payload = {
        "intent_id": "intent.server.demography.shard.{}.tick.{}".format(str(shard_id), int(tick)),
        "process_id": process_id,
        "inputs": inputs,
    }
    executed = execute_intent(
        state=state,
        intent=intent_payload,
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices=dict(runtime.get("registry_payloads") or {}),
        policy_context=_runtime_policy_context(runtime, active_shard_id=str(shard_id)),
    )
    debug_assert_after_execute(state=state, intent=intent_payload, result=dict(executed or {}))
    return executed


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


def _emit_control_proof_bundle(
    *,
    repo_root: str,
    runtime: dict,
    tick: int,
    envelope_rows: List[dict],
) -> Dict[str, object]:
    markers = collect_control_decision_markers(list(envelope_rows or []))
    global_state = dict(runtime.get("global_state") or {})
    mobility_surface = compute_mobility_proof_hashes(
        travel_event_rows=list(global_state.get("travel_events") or []),
        edge_occupancy_rows=list(global_state.get("edge_occupancies") or []),
        signal_state_rows=list(global_state.get("mobility_signals") or []),
    )
    elec_surface = dict(global_state.get("elec_proof_surface") or {})
    mobility_surface.update(
        {
            "power_flow_hash": str(elec_surface.get("power_flow_hash", global_state.get("power_flow_hash", ""))).strip(),
            "power_flow_hash_chain": str(
                elec_surface.get("power_flow_hash_chain", global_state.get("power_flow_hash_chain", ""))
            ).strip(),
            "fault_state_hash_chain": str(
                elec_surface.get("fault_state_hash_chain", global_state.get("fault_state_hash_chain", ""))
            ).strip(),
            "protection_state_hash_chain": str(
                elec_surface.get("protection_state_hash_chain", global_state.get("protection_state_hash_chain", ""))
            ).strip(),
            "degradation_event_hash_chain": str(
                elec_surface.get("degradation_event_hash_chain", global_state.get("degradation_event_hash_chain", ""))
            ).strip(),
            "trip_event_hash_chain": str(
                elec_surface.get("trip_event_hash_chain", global_state.get("trip_event_hash_chain", ""))
            ).strip(),
            "trip_explanation_hash_chain": str(
                elec_surface.get("trip_explanation_hash_chain", global_state.get("trip_explanation_hash_chain", ""))
            ).strip(),
            "momentum_hash_chain": str(global_state.get("momentum_hash_chain", "")).strip(),
            "impulse_event_hash_chain": str(global_state.get("impulse_event_hash_chain", "")).strip(),
            "energy_ledger_hash_chain": str(global_state.get("energy_ledger_hash_chain", "")).strip(),
            "boundary_flux_hash_chain": str(global_state.get("boundary_flux_hash_chain", "")).strip(),
            "combustion_hash_chain": str(global_state.get("combustion_hash_chain", "")).strip(),
            "emission_hash_chain": str(global_state.get("emission_hash_chain", "")).strip(),
            "impulse_hash_chain": str(global_state.get("impulse_hash_chain", "")).strip(),
            "process_run_hash_chain": str(global_state.get("process_run_hash_chain", "")).strip(),
            "batch_quality_hash_chain": str(global_state.get("batch_quality_hash_chain", "")).strip(),
            "yield_model_hash_chain": str(global_state.get("yield_model_hash_chain", "")).strip(),
            "entropy_hash_chain": str(global_state.get("entropy_hash_chain", "")).strip(),
            "entropy_reset_events_hash_chain": str(
                global_state.get("entropy_reset_events_hash_chain", global_state.get("entropy_reset_hash_chain", ""))
            ).strip(),
            "fluid_flow_hash_chain": str(global_state.get("fluid_flow_hash_chain", "")).strip(),
            "leak_hash_chain": str(global_state.get("leak_hash_chain", "")).strip(),
            "burst_hash_chain": str(global_state.get("burst_hash_chain", "")).strip(),
            "relief_event_hash_chain": str(global_state.get("relief_event_hash_chain", "")).strip(),
            "field_update_hash_chain": str(global_state.get("field_update_hash_chain", "")).strip(),
            "field_sample_hash_chain": str(global_state.get("field_sample_hash_chain", "")).strip(),
            "boundary_field_exchange_hash_chain": str(
                global_state.get("boundary_field_exchange_hash_chain", "")
            ).strip(),
            "time_mapping_hash_chain": str(global_state.get("time_mapping_hash_chain", "")).strip(),
            "schedule_domain_evaluation_hash": str(
                global_state.get("schedule_domain_evaluation_hash", "")
            ).strip(),
            "time_adjust_event_hash_chain": str(
                global_state.get("time_adjust_event_hash_chain", "")
            ).strip(),
            "compaction_marker_hash_chain": str(
                global_state.get("compaction_marker_hash_chain", "")
            ).strip(),
            "compaction_pre_anchor_hash": str(
                global_state.get("compaction_pre_anchor_hash", "")
            ).strip(),
            "compaction_post_anchor_hash": str(
                global_state.get("compaction_post_anchor_hash", "")
            ).strip(),
            "drift_policy_id": str(global_state.get("drift_policy_id", "drift.none")).strip() or "drift.none",
        }
    )
    bundle = build_control_proof_bundle_from_markers(
        tick_start=int(tick),
        tick_end=int(tick),
        decision_markers=markers,
        mobility_proof_surface=mobility_surface,
        extensions={
            "network_policy_id": "policy.net.srz_hybrid",
            "source": "srz_hybrid.queued_envelopes",
        },
    )
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="control_proof_bundle",
        payload=bundle,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return refusal(
            "refusal.net.envelope_invalid",
            "control proof bundle failed schema validation",
            "Fix control proof bundle payload generation before retrying SRZ tick advance.",
            {"schema_id": "control_proof_bundle", "tick": str(int(tick))},
            "$.control_proof_bundle",
        )
    bundle_rel = norm(os.path.join("control_proofs", "control.proof.tick.{}.json".format(int(tick))))
    bundle_ref = _write_runtime_artifact(runtime=runtime, rel_path=bundle_rel, payload=bundle)
    server = _runtime_server(runtime)
    rows = list(server.get("control_proof_bundles") or [])
    rows.append(
        {
            "tick": int(tick),
            "proof_id": str(bundle.get("proof_id", "")),
            "deterministic_fingerprint": str(bundle.get("deterministic_fingerprint", "")),
            "decision_log_count": len(list(bundle.get("decision_log_hashes") or [])),
            "bundle_ref": str(bundle_ref),
        }
    )
    server["control_proof_bundles"] = sorted(
        (dict(row) for row in rows if isinstance(row, dict)),
        key=lambda row: (
            int(_as_int(row.get("tick", 0), 0)),
            str(row.get("proof_id", "")),
        ),
    )
    server["last_control_proof_hash"] = str(bundle.get("deterministic_fingerprint", ""))
    server["last_control_proof_bundle_ref"] = str(bundle_ref)
    runtime["server"] = server
    return {
        "result": "complete",
        "bundle": bundle,
        "bundle_ref": str(bundle_ref),
    }


def _apply_enforcement_result(
    action: str,
    fallback_reason_code: str,
    fallback_message: str,
    fallback_remediation: str,
    relevant_ids: dict,
    path: str,
) -> Dict[str, object]:
    token = str(action).strip()
    if action_drops_without_refusal(token):
        return {"result": "complete", "accepted": False, "action": token}
    reason_code = refusal_reason_from_action(token, fallback_reason_code=fallback_reason_code)
    if reason_code == "refusal.ac.attestation_missing":
        return refusal(
            "refusal.ac.attestation_missing",
            "anti-cheat policy requires client attestation artifact",
            "Enable client attestation token exchange or use an anti-cheat policy that does not require attestation.",
            dict(relevant_ids or {}),
            str(path),
        )
    if token == "terminate":
        return refusal(
            "refusal.ac.policy_violation",
            "anti-cheat policy escalated this peer to terminate action",
            "Resolve anti-cheat violations and reconnect using a compliant client state.",
            dict(relevant_ids or {}),
            str(path),
        )
    return refusal(
        str(fallback_reason_code),
        str(fallback_message),
        str(fallback_remediation),
        dict(relevant_ids or {}),
        str(path),
    )


def _policy_row(registry_payload: dict, policy_id: str, key: str = "policies") -> dict:
    rows = registry_payload.get(key)
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {}


def _server_profile_row(registry_payload: dict, server_profile_id: str) -> dict:
    rows = registry_payload.get("profiles")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("server_profile_id", ""))):
        if str(row.get("server_profile_id", "")).strip() == str(server_profile_id).strip():
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


def _view_mode_row(runtime: dict, view_mode_id: str) -> dict:
    token = str(view_mode_id).strip()
    if not token:
        return {}
    registry_payloads = dict(runtime.get("registry_payloads") or {})
    view_mode_registry = dict(registry_payloads.get("view_mode_registry") or {})
    rows = view_mode_registry.get("view_modes")
    if not isinstance(rows, list):
        return {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("view_mode_id", ""))):
        if str(row.get("view_mode_id", "")).strip() == token:
            return dict(row)
    return {}


def _is_follow_view_mode(runtime: dict, view_mode_id: str) -> bool:
    row = _view_mode_row(runtime=runtime, view_mode_id=view_mode_id)
    ext = dict(row.get("extensions") or {})
    return str(ext.get("spectator_pattern", "")).strip() == "follow_agent"


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


def _entity_owner_shard(runtime: dict, shard_map: dict, entity_id: str) -> str:
    token = str(entity_id).strip()
    state = dict(runtime.get("global_state") or {})
    if token and isinstance(state, dict):
        agent_rows = state.get("agent_states")
        if isinstance(agent_rows, list):
            for row in sorted((item for item in agent_rows if isinstance(item, dict)), key=lambda item: str(item.get("agent_id", ""))):
                if str(row.get("agent_id", "")).strip() != token:
                    continue
                owner = str(row.get("shard_id", "")).strip()
                if owner:
                    return owner
                break
        body_rows = state.get("body_assemblies")
        if isinstance(body_rows, list):
            for row in sorted((item for item in body_rows if isinstance(item, dict)), key=lambda item: str(item.get("assembly_id", ""))):
                body_id = str(row.get("assembly_id", "")).strip()
                owner_agent_id = str(row.get("owner_agent_id", "")).strip()
                owner_assembly_id = str(row.get("owner_assembly_id", "")).strip()
                if token not in (body_id, owner_agent_id, owner_assembly_id):
                    continue
                owner = str(row.get("shard_id", "")).strip()
                if owner:
                    return owner
                break
    index = shard_index(shard_map)
    owner = str((index.get("object_owner") or {}).get(token, "")).strip()
    if owner:
        return owner
    shard_ids = list(index.get("shard_ids") or [])
    if DEFAULT_SHARD_ID in shard_ids:
        return DEFAULT_SHARD_ID
    if shard_ids:
        return str(shard_ids[0])
    return DEFAULT_SHARD_ID


def _first_input_token(inputs: dict, keys: Tuple[str, ...], default_value: str = "") -> str:
    payload = dict(inputs if isinstance(inputs, dict) else {})
    for key in keys:
        token = str(payload.get(str(key), "")).strip()
        if token:
            return token
    return str(default_value or "").strip()


def _proposal_owner_object_id(process_id: str, inputs: dict) -> str:
    token = str(process_id).strip()
    if token in ("process.agent_move", "process.agent_rotate", "process.srz_transfer_entity"):
        return _first_input_token(
            inputs,
            ("agent_id", "target_agent_id", "target_id"),
            "agent.unknown",
        ) or "agent.unknown"
    if token in ("process.control_bind_camera", "process.control_unbind_camera"):
        return _first_input_token(
            inputs,
            ("camera_id", "target_camera_id", "target_id"),
            "camera.main",
        ) or "camera.main"
    if token in ("process.camera_bind_target", "process.camera_unbind_target"):
        target_type = str((inputs or {}).get("target_type", "")).strip()
        if target_type in ("agent", "body", "site"):
            target = _first_input_token(
                inputs,
                ("target_id",),
                "",
            )
            if target:
                return target
        return _first_input_token(
            inputs,
            ("camera_id", "target_camera_id"),
            "camera.main",
        ) or "camera.main"
    if token == "process.camera_set_view_mode":
        target_type = str((inputs or {}).get("target_type", "")).strip()
        if target_type in ("agent", "body", "site"):
            target = _first_input_token(
                inputs,
                ("target_id",),
                "",
            )
            if target:
                return target
        return _first_input_token(
            inputs,
            ("camera_id", "target_camera_id"),
            "camera.main",
        ) or "camera.main"
    if token == "process.camera_set_lens":
        return _first_input_token(
            inputs,
            ("camera_id", "target_camera_id"),
            "camera.main",
        ) or "camera.main"
    if token in ("process.control_possess_agent", "process.control_release_agent"):
        return _first_input_token(
            inputs,
            ("agent_id", "target_agent_id", "target_id"),
            "camera.main",
        ) or "camera.main"
    if token == "process.cosmetic_assign":
        return _first_input_token(
            inputs,
            ("agent_id", "target_agent_id", "target_id"),
            "agent.unknown",
        ) or "agent.unknown"
    if token == "process.control_set_view_lens":
        return _first_input_token(
            inputs,
            ("camera_id", "target_camera_id", "target_id"),
            "camera.main",
        ) or "camera.main"
    if token == "process.body_move_attempt":
        return _first_input_token(
            inputs,
            ("body_id", "target_body_id", "target_id"),
            "body.unknown",
        ) or "body.unknown"
    return str(PROCESS_OWNER_OBJECT.get(token, "camera.main"))


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
    server_profile = {}
    server_profile_id = str(network.get("server_profile_id", "")).strip()
    if isinstance(registry_payloads, dict):
        server_profile = _server_profile_row(
            dict(registry_payloads.get("server_profile_registry") or {}),
            server_profile_id,
        )
    server_profile_ext = dict(server_profile.get("extensions") or {})
    cosmetic_policy_id = (
        str(server_profile_ext.get("cosmetic_policy_id", "")).strip()
        or str(server_ext.get("cosmetic_policy_id", "")).strip()
    )
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
    allow_cross_shard_possession = bool(server_ext.get("allow_cross_shard_possession", False))
    allow_cross_shard_collision = bool(server_ext.get("allow_cross_shard_collision", False))
    allow_srz_transfer = bool(server_ext.get("allow_srz_transfer", False))

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
        "control_policy": {
            "allow_cross_shard_possession": bool(allow_cross_shard_possession),
            "allow_cross_shard_collision": bool(allow_cross_shard_collision),
            "allow_cross_shard_follow": bool(server_ext.get("allow_cross_shard_follow", False)),
            "allow_srz_transfer": bool(allow_srz_transfer),
            "allowed_view_modes": _sorted_tokens(list(server_ext.get("allowed_view_modes") or [])),
            "cosmetic_policy_id": cosmetic_policy_id,
        },
        "server_policy": dict(server_policy),
        "server_profile": dict(server_profile),
        "representation_state": {
            "assignments": {},
            "events": [],
        },
        "perception_interest_policy": perception_policy,
        "anti_cheat": {
            "policy_id": anti_cheat_policy_id,
            "modules_enabled": _sorted_tokens(list(anti_cheat_policy.get("modules_enabled") or [])),
            "default_actions": dict(anti_cheat_policy.get("default_actions") or {}),
            "extensions": dict(anti_cheat_policy.get("extensions") or {}),
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
            "last_ledger_hash": "",
            "last_ledger_by_shard": {},
            "last_composite_hash": "0" * 64,
            "last_control_proof_hash": "",
            "last_control_proof_bundle_ref": "",
            "hash_anchor_frames": [],
            "control_proof_bundles": [],
            "snapshots": [],
            "snapshot_peer_models": {},
            "snapshot_peer_memory": {},
            "baseline_snapshot_id": "",
            "baseline_snapshot_ids": [],
            "perceived_deltas": [],
            "anti_cheat_events": [],
            "anti_cheat_enforcement_actions": [],
            "anti_cheat_refusal_injections": [],
            "anti_cheat_anchor_mismatches": [],
            "anti_cheat_violation_counters": {},
            "terminated_peers": [],
            "refusals": [],
            "conservation_runtime_by_shard": {},
            "conservation_ledgers": [],
        },
        "shards": shard_rows,
        "clients": {},
    }
    runtime_registry_payloads = dict(runtime.get("registry_payloads") or {})
    runtime_registry_payloads["representation_state"] = runtime.get("representation_state")
    runtime["registry_payloads"] = runtime_registry_payloads
    ensure_runtime_channels(runtime)

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
        decision = check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int((_runtime_server(runtime).get("network_tick", 0)), 0),
            peer_id=str((envelope or {}).get("source_peer_id", "peer.unknown")),
            valid=False,
            reason_code="refusal.net.envelope_invalid",
            evidence=["intent envelope schema validation failed"],
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.envelope_invalid",
            fallback_message="intent envelope failed net_intent_envelope schema validation",
            fallback_remediation="Fix envelope fields and retry submission.",
            relevant_ids={"schema_id": "net_intent_envelope"},
            path="$.intent_envelope",
        )

    server = _runtime_server(runtime)
    peer_id = str(envelope.get("source_peer_id", "")).strip()
    clients = _runtime_clients(runtime)
    if peer_id not in clients:
        decision = check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            allowed=False,
            reason_code="refusal.net.authority_violation",
            evidence=["source peer is not joined to SRZ hybrid runtime"],
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.authority_violation",
            fallback_message="source peer is not joined to SRZ hybrid runtime",
            fallback_remediation="Join peer via baseline sync before submitting intents.",
            relevant_ids={"peer_id": peer_id or "<empty>"},
            path="$.source_peer_id",
        )

    anti_extensions = dict((runtime.get("anti_cheat") or {}).get("extensions") or {})
    attestation_required = bool(anti_extensions.get("require_attestation", False))
    envelope_ext = dict(envelope.get("extensions") or {})
    attestation_token = str(envelope_ext.get("attestation_token", "")).strip() or str(envelope.get("signature", "")).strip()
    attestation_check = check_client_attestation(
        repo_root=repo_root,
        runtime=runtime,
        tick=_as_int(server.get("network_tick", 0), 0),
        peer_id=peer_id,
        required=bool(attestation_required),
        attestation_token=attestation_token,
        default_action_token="require_attestation",
    )
    if str(attestation_check.get("result", "")) != "complete":
        return _apply_enforcement_result(
            action=str(attestation_check.get("action", "require_attestation")),
            fallback_reason_code="refusal.ac.attestation_missing",
            fallback_message="client attestation token is required by anti-cheat policy",
            fallback_remediation="Provide deterministic attestation token or use a policy that does not require attestation.",
            relevant_ids={"peer_id": peer_id or "<empty>"},
            path="$.signature",
        )

    expected_pack_lock = str(server.get("pack_lock_hash", "")).strip()
    if str(envelope.get("pack_lock_hash", "")).strip() != expected_pack_lock:
        decision = check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            valid=False,
            reason_code="refusal.net.handshake_pack_lock_mismatch",
            evidence=["intent envelope pack_lock_hash does not match server lock hash"],
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.handshake_pack_lock_mismatch",
            fallback_message="intent envelope pack_lock_hash does not match server lock hash",
            fallback_remediation="Reconnect using matching bundle lockfile and retry intent submission.",
            relevant_ids={"peer_id": peer_id},
            path="$.pack_lock_hash",
        )

    seen = _sorted_tokens(list(server.get("seen_envelope_ids") or []))
    envelope_id = str(envelope.get("envelope_id", "")).strip()
    if envelope_id in seen:
        decision = check_replay_protection(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            envelope_id=envelope_id,
            seen_envelope_ids=seen,
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.replay_detected",
            fallback_message="intent envelope replay detected",
            fallback_remediation="Generate a new deterministic envelope sequence and retry submission.",
            relevant_ids={"envelope_id": envelope_id},
            path="$.envelope_id",
        )

    sequence = _as_int(envelope.get("deterministic_sequence_number", 0), 0)
    last_seq_map = dict(server.get("last_sequence_by_peer") or {})
    expected_next = _as_int(last_seq_map.get(peer_id, 0), 0) + 1
    if sequence != expected_next:
        decision = check_sequence_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            sequence=int(sequence),
            expected_sequence=int(expected_next),
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.sequence_violation",
            fallback_message="deterministic_sequence_number is out of order for peer '{}'".format(peer_id),
            fallback_remediation="Submit envelopes with monotonic deterministic_sequence_number values.",
            relevant_ids={"peer_id": peer_id, "expected_sequence": str(expected_next), "actual_sequence": str(sequence)},
            path="$.deterministic_sequence_number",
        )

    payload = dict(envelope.get("payload") or {})
    process_id = str(payload.get("process_id", "")).strip()
    if process_id in MOVEMENT_PROCESS_IDS:
        limits = _movement_limits(runtime=runtime)
        movement_inputs = dict(payload.get("inputs") or {})
        submission_tick = _as_int(envelope.get("submission_tick", 0), 0)
        existing_movement_count = 0
        for queued in list(server.get("queued_envelopes") or []):
            if not isinstance(queued, dict):
                continue
            if str(queued.get("source_peer_id", "")).strip() != peer_id:
                continue
            if _as_int(queued.get("submission_tick", 0), 0) != int(submission_tick):
                continue
            queued_process = str((dict(queued.get("payload") or {})).get("process_id", "")).strip()
            if queued_process in MOVEMENT_PROCESS_IDS:
                existing_movement_count += 1
        if int(existing_movement_count) >= int(limits["max_intents_per_tick"]):
            decision = check_input_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=_as_int(server.get("network_tick", 0), 0),
                peer_id=peer_id,
                valid=False,
                reason_code="ac.movement.intent_rate_exceeded",
                evidence=[
                    "movement intent frequency exceeded deterministic per-tick limit",
                    "submission_tick={},current_count={},max_count={}".format(
                        int(submission_tick),
                        int(existing_movement_count),
                        int(limits["max_intents_per_tick"]),
                    ),
                ],
                default_action_token="throttle",
            )
            action = str(decision.get("action", "throttle"))
            if action_blocks_submission(action):
                return _apply_enforcement_result(
                    action=action,
                    fallback_reason_code="refusal.ac.policy_violation",
                    fallback_message="movement intent rate exceeds deterministic anti-cheat threshold",
                    fallback_remediation="Reduce movement intent frequency per tick or adjust anti-cheat policy thresholds.",
                    relevant_ids={"peer_id": peer_id, "process_id": process_id},
                    path="$.payload.process_id",
                )
            if str(action).strip() == "throttle":
                return {"result": "complete", "accepted": False, "action": "throttle"}

        requested_distance_mm, requested_dt_ticks = _movement_requested_distance(movement_inputs)
        max_distance_mm = int(limits["max_displacement_mm_per_tick"]) * int(max(1, requested_dt_ticks))
        if int(requested_distance_mm) > int(max_distance_mm):
            behavior = check_behavioral_detection(
                repo_root=repo_root,
                runtime=runtime,
                tick=_as_int(server.get("network_tick", 0), 0),
                peer_id=peer_id,
                suspicious=True,
                reason_code="ac.movement.requested_displacement_exceeded",
                evidence=[
                    "movement request exceeds deterministic displacement threshold",
                    "requested_distance_mm={},max_distance_mm={},dt_ticks={}".format(
                        int(requested_distance_mm),
                        int(max_distance_mm),
                        int(max(1, requested_dt_ticks)),
                    ),
                ],
                default_action_token="throttle",
            )
            action = str(behavior.get("action", "throttle"))
            if action_blocks_submission(action):
                return _apply_enforcement_result(
                    action=action,
                    fallback_reason_code="refusal.ac.policy_violation",
                    fallback_message="movement request exceeds deterministic displacement threshold",
                    fallback_remediation="Reduce requested movement delta per tick or adjust anti-cheat movement thresholds.",
                    relevant_ids={"peer_id": peer_id, "process_id": process_id},
                    path="$.payload.inputs.move_vector_local",
                )
            if str(action).strip() == "throttle":
                return {"result": "complete", "accepted": False, "action": "throttle"}

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
            decision = check_authority_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=_as_int(server.get("network_tick", 0), 0),
                peer_id=peer_id,
                allowed=False,
                reason_code="refusal.net.shard_target_invalid",
                evidence=["routed envelope target_shard_id is not active"],
                default_action_token="refuse",
            )
            return _apply_enforcement_result(
                action=str(decision.get("action", "refuse")),
                fallback_reason_code="refusal.net.shard_target_invalid",
                fallback_message="routed envelope target_shard_id '{}' is not active".format(target or "<empty>"),
                fallback_remediation="Route to an active shard declared by shard_map registry.",
                relevant_ids={"target_shard_id": target or "<empty>"},
                path="$.target_shard_id",
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
    shard_map = dict(runtime.get("shard_map") or {})
    owner_object_id = _proposal_owner_object_id(process_id=process_id, inputs=dict(inputs))
    owner_shard_id = _entity_owner_shard(runtime=runtime, shard_map=shard_map, entity_id=owner_object_id)
    if process_id in ("process.control_possess_agent", "process.control_release_agent"):
        controller_id = _first_input_token(
            dict(inputs),
            ("controller_id", "target_controller_id"),
        )
        agent_id = _first_input_token(
            dict(inputs),
            ("agent_id", "target_agent_id", "target_id"),
        )
        controller_shard_id = _entity_owner_shard(runtime=runtime, shard_map=shard_map, entity_id=controller_id or owner_object_id)
        agent_shard_id = _entity_owner_shard(runtime=runtime, shard_map=shard_map, entity_id=agent_id or owner_object_id)
        control_policy = dict(runtime.get("control_policy") or {})
        allow_cross = bool(control_policy.get("allow_cross_shard_possession", False))
        if controller_id and agent_id and controller_shard_id != agent_shard_id and not allow_cross:
            return refusal(
                "refusal.control.cross_shard_possession_forbidden",
                "controller '{}' and agent '{}' resolve to different shards ('{}' vs '{}')".format(
                    controller_id,
                    agent_id,
                    controller_shard_id,
                    agent_shard_id,
                ),
                "Route controller and possessed agent to the same shard, or enable allow_cross_shard_possession in server policy.",
                {
                    "controller_id": controller_id,
                    "agent_id": agent_id,
                    "controller_shard_id": controller_shard_id,
                    "agent_shard_id": agent_shard_id,
                },
                "$.intent_envelope.payload.inputs",
            )
        if agent_id:
            owner_object_id = str(agent_id)
            owner_shard_id = str(agent_shard_id)
    if process_id in ("process.control_bind_camera", "process.camera_bind_target", "process.camera_set_view_mode"):
        camera_id = _first_input_token(
            dict(inputs),
            ("camera_id", "target_camera_id", "target_id"),
            "camera.main",
        ) or "camera.main"
        target_type = str((inputs or {}).get("target_type", "none")).strip() or "none"
        target_id = _first_input_token(
            dict(inputs),
            ("target_id",),
            "",
        )
        camera_shard_id = _entity_owner_shard(runtime=runtime, shard_map=shard_map, entity_id=camera_id)
        target_owner_shard_id = ""
        if target_type in ("agent", "body", "site") and target_id:
            target_owner_shard_id = _entity_owner_shard(runtime=runtime, shard_map=shard_map, entity_id=target_id)
        control_policy = dict(runtime.get("control_policy") or {})
        allow_cross_shard_follow = bool(control_policy.get("allow_cross_shard_follow", False))
        requested_view_mode = str((inputs or {}).get("view_mode_id", "")).strip()
        if camera_shard_id and target_owner_shard_id and camera_shard_id != target_owner_shard_id:
            if not _is_follow_view_mode(runtime=runtime, view_mode_id=requested_view_mode) or not allow_cross_shard_follow:
                return refusal(
                    "refusal.view.cross_shard_follow_forbidden",
                    "camera '{}' and target '{}' resolve to different shards ('{}' vs '{}')".format(
                        camera_id,
                        target_id,
                        camera_shard_id,
                        target_owner_shard_id,
                    ),
                    "Use same-shard follow target or enable cross-shard spectator follow policy.",
                    {
                        "camera_id": camera_id,
                        "target_id": target_id,
                        "camera_shard_id": camera_shard_id,
                        "target_shard_id": target_owner_shard_id,
                        "view_mode_id": requested_view_mode or "<unspecified>",
                    },
                    "$.intent_envelope.payload.inputs",
                )
        if target_owner_shard_id:
            owner_object_id = str(target_id)
            owner_shard_id = str(target_owner_shard_id)
    if process_id == "process.srz_transfer_entity":
        control_policy = dict(runtime.get("control_policy") or {})
        if not bool(control_policy.get("allow_srz_transfer", False)):
            return refusal(
                "refusal.agent.boundary_cross_forbidden",
                "SRZ transfer process is disabled by active server control policy",
                "Enable allow_srz_transfer in server policy extensions to permit deterministic shard transfers.",
                {"process_id": process_id},
                "$.intent_envelope.payload.process_id",
            )
    if owner_shard_id != target_shard_id:
        reason_code = "refusal.net.cross_shard_unsupported"
        message = "process '{}' owner '{}' resolves to shard '{}' but routed envelope targets '{}'".format(
            process_id,
            owner_object_id,
            owner_shard_id,
            target_shard_id or "<empty>",
        )
        remediation = "Use deterministic routing so process owner and target shard match, or implement declared cross-shard process metadata."
        if process_id in ("process.agent_move", "process.agent_rotate"):
            reason_code = "refusal.net.shard_target_invalid"
            remediation = "Route movement intents to the owning agent shard."
        return refusal(
            reason_code,
            message,
            remediation,
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
    global_state = dict(runtime.get("global_state") or {})
    performance_state = dict(global_state.get("performance_state") or {})
    transition_event_hash = canonical_sha256(
        sorted(
            (dict(item) for item in list(performance_state.get("transition_events") or []) if isinstance(item, dict)),
            key=lambda item: (
                int(_as_int(item.get("tick", 0), 0)),
                str(item.get("shard_id", "")),
                str(item.get("region_id", "")),
                str(item.get("event_id", "")),
            ),
        )
    )
    payload = {
        "tick": int(tick),
        "state_hash": canonical_sha256(global_state),
        "pack_lock_hash": str(server.get("pack_lock_hash", "")),
        "registry_hashes": dict(server.get("registry_hashes") or {}),
        "ledger_hash": str(server.get("last_ledger_hash", "")),
        "transition_event_hash": str(transition_event_hash),
        "previous_composite_hash": str(server.get("last_composite_hash", "0" * 64)),
    }
    control_proof_hash = str(server.get("last_control_proof_hash", "")).strip()
    if control_proof_hash:
        payload["control_proof_hash"] = control_proof_hash
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
            "ledger_hash": str(server.get("last_ledger_hash", "")),
            "transition_event_hash": canonical_sha256(
                sorted(
                    (
                        dict(item)
                        for item in list((dict((runtime.get("global_state") or {})).get("performance_state") or {}).get("transition_events") or [])
                        if isinstance(item, dict)
                    ),
                    key=lambda item: (
                        int(_as_int(item.get("tick", 0), 0)),
                        str(item.get("shard_id", "")),
                        str(item.get("region_id", "")),
                        str(item.get("event_id", "")),
                    ),
                )
            ),
            "control_proof_hash": str(server.get("last_control_proof_hash", "")),
            "control_proof_bundle_ref": str(server.get("last_control_proof_bundle_ref", "")),
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
    clients = _runtime_clients(runtime)
    peer_models = {}
    peer_hashes = {}
    peer_memory = {}
    peer_memory_hashes = {}
    for peer_id in sorted(clients.keys()):
        client = dict(clients.get(peer_id) or {})
        perceived_model = dict(client.get("last_perceived_model") or {})
        memory_state = dict(client.get("memory_state") or {})
        peer_models[peer_id] = perceived_model
        peer_hashes[peer_id] = canonical_sha256(perceived_model)
        peer_memory[peer_id] = memory_state
        peer_memory_hashes[peer_id] = canonical_sha256(memory_state)
    snapshots = []
    for shard in _runtime_shards(runtime):
        shard_id = str(shard.get("shard_id", "")).strip()
        snapshot_id = "snapshot.{}.tick.{}".format(shard_id, int(tick))
        snapshot_payload = {
            "schema_version": "1.0.0",
            "snapshot_id": snapshot_id,
            "tick": int(tick),
            "shard_id": shard_id,
            "state": dict(runtime.get("global_state") or {}),
            "peer_hashes": dict((key, peer_hashes[key]) for key in sorted(peer_hashes.keys())),
            "peer_memory_hashes": dict((key, peer_memory_hashes[key]) for key in sorted(peer_memory_hashes.keys())),
        }
        payload_ref = _write_runtime_artifact(
            runtime=runtime,
            rel_path=norm(os.path.join("snapshots", shard_id, "tick.{}.json".format(int(tick)))),
            payload=snapshot_payload,
        )
        snapshot = {
            "schema_version": "1.0.0",
            "snapshot_id": snapshot_id,
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
    snapshot_models = dict(server.get("snapshot_peer_models") or {})
    snapshot_memory = dict(server.get("snapshot_peer_memory") or {})
    for snapshot in snapshots:
        snapshot_id = str((snapshot or {}).get("snapshot_id", "")).strip()
        if not snapshot_id:
            continue
        snapshot_models[snapshot_id] = copy.deepcopy(peer_models)
        snapshot_memory[snapshot_id] = copy.deepcopy(peer_memory)
    server["snapshot_peer_models"] = snapshot_models
    server["snapshot_peer_memory"] = snapshot_memory
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
        memory_state = dict(client.get("memory_state") or {})
        memory_store_hash = str(memory_state.get("store_hash", ""))
        delta_payload = {
            "schema_version": "1.0.0",
            "perceived_delta_id": "pdelta.{}.tick.{}".format(peer_id, int(tick)),
            "tick": int(tick),
            "replace": perceived_model,
            "previous_hash": str(client.get("last_perceived_hash", "")),
            "extensions": {
                "memory_store_hash": memory_store_hash,
                "memory_state_hash": canonical_sha256(memory_state),
            },
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
                "memory_store_hash": memory_store_hash,
                "memory_state_hash": canonical_sha256(memory_state),
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
            actual_hash = canonical_sha256(dict(delta_payload.get("replace") or {}))
            state_check = check_state_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(tick),
                peer_id=peer_id,
                expected_hash=str(perceived_hash),
                actual_hash=str(actual_hash),
                reason_code="refusal.net.resync_required",
                default_action_token="audit",
            )
            enforcement = _apply_enforcement_result(
                action=str(state_check.get("action", "audit")),
                fallback_reason_code="refusal.net.resync_required",
                fallback_message="perceived delta hash mismatch detected",
                fallback_remediation="Request hybrid snapshot resync before continuing.",
                relevant_ids={"peer_id": peer_id, "tick": str(tick)},
                path="$.perceived_delta.perceived_hash",
            )
            if str(enforcement.get("result", "")) != "complete":
                return enforcement
            continue
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
    tick_ledger_by_shard: Dict[str, str] = {}
    for envelope in ready:
        built = _build_proposal(runtime=runtime, envelope=envelope, tick=int(tick))
        if str(built.get("result", "")) != "complete":
            refusal_payload = dict(built.get("refusal") or {})
            refusal_code = str(refusal_payload.get("reason_code", "refusal.net.envelope_invalid"))
            if refusal_code in (
                "refusal.net.authority_violation",
                "refusal.net.shard_target_invalid",
                "refusal.net.cross_shard_unsupported",
                "refusal.agent.boundary_cross_forbidden",
                "refusal.control.cross_shard_possession_forbidden",
                "refusal.control.cross_shard_collision_forbidden",
                "refusal.view.cross_shard_follow_forbidden",
            ):
                check_authority_integrity(
                    repo_root=repo_root,
                    runtime=runtime,
                    tick=int(tick),
                    peer_id=str(envelope.get("source_peer_id", "")),
                    allowed=False,
                    reason_code=refusal_code,
                    evidence=["proposal build refused deterministic envelope"],
                    default_action_token="refuse",
                )
            else:
                check_input_integrity(
                    repo_root=repo_root,
                    runtime=runtime,
                    tick=int(tick),
                    peer_id=str(envelope.get("source_peer_id", "")),
                    valid=False,
                    reason_code=refusal_code,
                    evidence=["proposal build refused deterministic envelope"],
                    default_action_token="refuse",
                )
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
        intent_payload = {
            "intent_id": str(proposal.get("intent_id", "")),
            "process_id": str(proposal.get("process_id", "")),
            "inputs": dict(proposal.get("inputs") or {}),
        }
        executed = execute_intent(
            state=state,
            intent=intent_payload,
            law_profile=dict(client.get("law_profile") or {}),
            authority_context=dict(client.get("authority_context") or {}),
            navigation_indices=dict(runtime.get("registry_payloads") or {}),
            policy_context=_runtime_policy_context(
                runtime,
                active_shard_id=str(proposal.get("target_shard_id", "")),
            ),
        )
        debug_assert_after_execute(state=state, intent=intent_payload, result=dict(executed or {}))
        if str(executed.get("result", "")) != "complete":
            refusal_payload = dict(executed.get("refusal") or {})
            refusal_reason_code = str(refusal_payload.get("reason_code", "refusal.net.authority_violation"))
            process_id = str(proposal.get("process_id", "")).strip()
            unauthorized_time_control = _is_unauthorized_time_control_refusal(
                process_id=process_id,
                reason_code=refusal_reason_code,
            )
            authority_reason_code = (
                "ac.time_control.unauthorized_change_attempt"
                if unauthorized_time_control
                else refusal_reason_code
            )
            authority_evidence = ["hybrid process execution refused submitted envelope"]
            if unauthorized_time_control:
                authority_evidence.append("process_id={}".format(process_id))
                authority_evidence.append("refusal_reason_code={}".format(refusal_reason_code))
            check_authority_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(tick),
                peer_id=peer_id,
                allowed=False,
                reason_code=str(authority_reason_code),
                evidence=authority_evidence,
                default_action_token="refuse",
            )
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

        process_id = str(proposal.get("process_id", "")).strip()
        if process_id in MOVEMENT_PROCESS_IDS:
            limits = _movement_limits(runtime=runtime)
            moved_distance_mm = max(0, _as_int(executed.get("movement_distance_mm", 0), 0))
            moved_dt_ticks = max(1, _as_int(executed.get("dt_ticks", 1), 1))
            max_distance_mm = int(limits["max_displacement_mm_per_tick"]) * int(moved_dt_ticks)
            check_behavioral_detection(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(tick),
                peer_id=peer_id,
                suspicious=bool(int(moved_distance_mm) > int(max_distance_mm)),
                reason_code="ac.movement.actual_displacement_exceeded",
                evidence=[
                    "movement displacement exceeded deterministic threshold after hybrid execution",
                    "agent_id={},moved_distance_mm={},max_distance_mm={},dt_ticks={}".format(
                        str(executed.get("agent_id", "")),
                        int(moved_distance_mm),
                        int(max_distance_mm),
                        int(moved_dt_ticks),
                    ),
                ],
                default_action_token="audit",
            )

        processed.append(
            {
                "envelope_id": str(proposal.get("envelope_id", "")),
                "peer_id": peer_id,
                "result": "complete",
                "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            }
        )
        ledger_token = str(executed.get("ledger_hash", "")).strip()
        target_shard_id = str(proposal.get("target_shard_id", "")).strip() or DEFAULT_SHARD_ID
        if ledger_token:
            tick_ledger_by_shard[target_shard_id] = ledger_token

    demography_ticks: List[dict] = []
    server_peer_id = str(server.get("peer_id", "")).strip() or "peer.server"
    for shard_row in _runtime_shards(runtime):
        shard_id = str(shard_row.get("shard_id", "")).strip()
        if not shard_id:
            continue
        demography_tick = _run_hybrid_demography_tick(
            state=state,
            runtime=runtime,
            tick=int(tick),
            shard_id=shard_id,
        )
        demography_result = str(demography_tick.get("result", ""))
        demography_summary = {
            "shard_id": shard_id,
            "result": demography_result or "skipped",
        }
        if demography_result == "complete":
            processed.append(
                {
                    "envelope_id": "auto.demography.{}.tick.{}".format(shard_id, int(tick)),
                    "peer_id": server_peer_id,
                    "result": "complete",
                    "state_hash_anchor": str(demography_tick.get("state_hash_anchor", "")),
                }
            )
            demography_summary.update(
                {
                    "state_hash_anchor": str(demography_tick.get("state_hash_anchor", "")),
                    "demography_policy_id": str(demography_tick.get("demography_policy_id", "")),
                    "processed_cohort_count": int(demography_tick.get("processed_cohort_count", 0) or 0),
                    "total_births": int(demography_tick.get("total_births", 0) or 0),
                    "total_deaths": int(demography_tick.get("total_deaths", 0) or 0),
                }
            )
            demography_ledger_hash = str(demography_tick.get("ledger_hash", "")).strip()
            if demography_ledger_hash:
                tick_ledger_by_shard[shard_id] = demography_ledger_hash
        elif demography_result == "refused":
            refusal_payload = dict(demography_tick.get("refusal") or {})
            processed.append(
                {
                    "envelope_id": "auto.demography.{}.tick.{}".format(shard_id, int(tick)),
                    "peer_id": server_peer_id,
                    "result": "refused",
                    "refusal": refusal_payload,
                }
            )
            _record_refusal(
                runtime=runtime,
                tick=int(tick),
                envelope_id="auto.demography.{}.tick.{}".format(shard_id, int(tick)),
                peer_id=server_peer_id,
                refusal_payload=refusal_payload,
            )
            demography_summary["refusal"] = refusal_payload
        else:
            demography_summary["reason"] = str(demography_tick.get("reason", "not_enabled"))
        demography_ticks.append(demography_summary)

    state_tick = int(simulation_tick(dict(state)))
    for shard_row in _runtime_shards(runtime):
        shard_id = str(shard_row.get("shard_id", "")).strip()
        if not shard_id:
            continue
        if str(tick_ledger_by_shard.get(shard_id, "")).strip():
            continue
        shard_policy_context = _runtime_policy_context(runtime, active_shard_id=shard_id)
        noop_finalized = finalize_noop_tick(
            policy_context=shard_policy_context,
            tick=int(state_tick),
            process_id="process.tick_ledger",
        )
        if str(noop_finalized.get("result", "")) == "complete":
            token = str(noop_finalized.get("ledger_hash", "")).strip()
            if token:
                tick_ledger_by_shard[shard_id] = token

    tick_ledger_hash = canonical_sha256(
        {
            "tick": int(tick),
            "ledger_by_shard": dict((key, tick_ledger_by_shard[key]) for key in sorted(tick_ledger_by_shard.keys())),
        }
    )
    sync_policy_context = _runtime_policy_context(runtime, active_shard_id=DEFAULT_SHARD_ID)
    ledger_rows = _sync_conservation_ledgers_to_server(runtime, sync_policy_context)
    _emit_conservation_anti_cheat_signals(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        ledger_rows=ledger_rows,
    )

    runtime["global_state"] = state
    server["network_tick"] = int(tick)
    server["last_ledger_hash"] = str(tick_ledger_hash)
    server["last_ledger_by_shard"] = dict((key, tick_ledger_by_shard[key]) for key in sorted(tick_ledger_by_shard.keys()))
    server["queued_envelopes"] = sorted(pending, key=_queue_sort_key)
    runtime["server"] = server

    proof_result = _emit_control_proof_bundle(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        envelope_rows=[dict(row) for row in list(ready or []) if isinstance(row, dict)],
    )
    if str(proof_result.get("result", "")) != "complete":
        return proof_result

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
        "ledger_hash": str(tick_ledger_hash),
        "processed_envelopes": processed,
        "resolved_proposals": resolved,
        "demography_ticks": demography_ticks,
        "hash_anchor_frame": frame,
        "control_proof_bundle": dict(proof_result.get("bundle") or {}),
        "perceived_deltas": list(deltas.get("perceived_deltas") or []),
        "client_memory_hashes": dict(
            sorted(
                (
                    key,
                    canonical_sha256(dict((value or {}).get("memory_state") or {})),
                )
                for key, value in (runtime.get("clients") or {}).items()
            )
        ),
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
    proof = export_proof_artifacts(
        repo_root=repo_root,
        runtime=runtime,
        run_id="tick.{}".format(int(server.get("network_tick", 0) or 0)),
    )
    return {
        "result": "complete",
        "queue_results": queue_results,
        "steps": steps,
        "final_tick": int(server.get("network_tick", 0) or 0),
        "final_composite_hash": str((frames[-1] if frames else {}).get("composite_hash", "")),
        "control_proof_bundle_ref": str(server.get("last_control_proof_bundle_ref", "")),
        "control_proof_hash": str(server.get("last_control_proof_hash", "")),
        "anti_cheat_proof": dict(proof),
    }


def prepare_hybrid_baseline(repo_root: str, runtime: dict) -> Dict[str, object]:
    server = _runtime_server(runtime)
    tick = _as_int(server.get("network_tick", 0), 0)
    baseline_proof = _emit_control_proof_bundle(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        envelope_rows=[],
    )
    if str(baseline_proof.get("result", "")) != "complete":
        return baseline_proof
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
        "extensions": {
            "control_proof_bundle_ref": str((_runtime_server(runtime).get("last_control_proof_bundle_ref", ""))),
            "control_proof_hash": str((_runtime_server(runtime).get("last_control_proof_hash", ""))),
        },
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
    snapshot_id_token = str(selected.get("snapshot_id", "")).strip()
    snapshot_models = dict(server.get("snapshot_peer_models") or {})
    peer_models = dict(snapshot_models.get(snapshot_id_token) or {})
    snapshot_memory = dict(server.get("snapshot_peer_memory") or {})
    peer_memory = dict(snapshot_memory.get(snapshot_id_token) or {})
    peer_model = peer_models.get(str(peer_id))
    peer_memory_state = peer_memory.get(str(peer_id))

    clients = _runtime_clients(runtime)
    if str(peer_id) not in clients:
        return refusal(
            "refusal.net.authority_violation",
            "peer is not joined to SRZ hybrid runtime",
            "Join peer before requesting snapshot resync.",
            {"peer_id": str(peer_id)},
            "$.peer_id",
        )
    if not isinstance(peer_model, dict):
        observed = _derive_perceived_for_peer(runtime=runtime, peer_id=str(peer_id))
        if str(observed.get("result", "")) != "complete":
            return observed
        peer_model = dict(observed.get("perceived_model") or {})
        peer_memory_state = dict(observed.get("memory_state") or {})
        peer_models[str(peer_id)] = dict(peer_model)
        peer_memory[str(peer_id)] = dict(peer_memory_state)
        snapshot_models[snapshot_id_token] = peer_models
        snapshot_memory[snapshot_id_token] = peer_memory
        server["snapshot_peer_models"] = snapshot_models
        server["snapshot_peer_memory"] = snapshot_memory
        runtime["server"] = server

    client = dict(clients.get(str(peer_id)) or {})
    client["last_perceived_model"] = dict(peer_model)
    client["last_perceived_hash"] = canonical_sha256(peer_model)
    client["memory_state"] = dict(peer_memory_state if isinstance(peer_memory_state, dict) else {})
    client["last_applied_tick"] = int(selected.get("tick", 0) or 0)
    client["resync_count"] = _as_int(client.get("resync_count", 0), 0) + 1
    clients[str(peer_id)] = client
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    return {
        "result": "complete",
        "snapshot": selected,
        "peer_id": str(peer_id),
        "perceived_hash": str(client.get("last_perceived_hash", "")),
        "memory_state_hash": canonical_sha256(dict(client.get("memory_state") or {})),
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
