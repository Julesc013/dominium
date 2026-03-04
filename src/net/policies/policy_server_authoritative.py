"""Deterministic server-authoritative replication policy (PerceivedModel-only transport)."""

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
    default_action as anti_cheat_default_action,
    emit_event as anti_cheat_emit_event,
    ensure_runtime_channels,
    export_proof_artifacts,
    module_enabled as anti_cheat_module_enabled,
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
from tools.xstack.sessionx.srz import (
    DEFAULT_SHARD_ID,
    build_single_shard,
    composite_hash,
    per_tick_hash,
)


POLICY_ID_SERVER_AUTHORITATIVE = "policy.net.server_authoritative"
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


def _runtime_server(runtime: dict) -> dict:
    server = runtime.get("server")
    if isinstance(server, dict):
        return server
    server = {}
    runtime["server"] = server
    return server


def _runtime_policy_context(runtime: dict) -> dict:
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
        "physics_profile_id": physics_profile_id,
        "active_shard_id": DEFAULT_SHARD_ID,
        "pack_lock_hash": str(((runtime.get("lock_payload") or {}).get("pack_lock_hash", ""))),
        "conservation_runtime_by_shard": runtime_conservation,
        "control_policy": dict(runtime.get("control_policy") or {}),
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
    server["conservation_ledgers"] = rows[-512:]
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
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(tick),
            peer_id=str((_runtime_server(runtime).get("peer_id", "peer.server"))),
            module_id="ac.module.authority_integrity",
            severity="violation",
            reason_code="ac.conservation.exception_type_unexpected",
            evidence=[
                "contract_set_id={}".format(contract_set_id),
                "quantity_id={}".format(quantity_id),
                "exception_type_id={}".format(exception_type_id),
                "ledger_hash={}".format(str(latest.get("ledger_hash", ""))),
            ],
            default_action="audit",
        )

    if _is_ranked_runtime(runtime) and int(meta_override_count) > 0:
        _emit_anti_cheat_event(
            repo_root=repo_root,
            runtime=runtime,
            tick=int(tick),
            peer_id=str((_runtime_server(runtime).get("peer_id", "peer.server"))),
            module_id="ac.module.authority_integrity",
            severity="violation",
            reason_code="ac.conservation.meta_law_override_ranked",
            evidence=[
                "meta_law_override_count={}".format(int(meta_override_count)),
                "contract_set_id={}".format(contract_set_id),
                "ledger_hash={}".format(str(latest.get("ledger_hash", ""))),
            ],
            default_action="audit",
        )


def _law_allows_process(law_profile: dict, process_id: str) -> bool:
    allowed = _sorted_tokens(list((law_profile or {}).get("allowed_processes") or []))
    forbidden = _sorted_tokens(list((law_profile or {}).get("forbidden_processes") or []))
    return bool(process_id in set(allowed) and process_id not in set(forbidden))


def _server_demography_authority(runtime: dict) -> Tuple[dict, dict]:
    clients = dict(runtime.get("clients") or {})
    if not clients:
        return {}, {}
    server = dict(runtime.get("server") or {})
    server_peer_id = str(server.get("peer_id", "")).strip()
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
            "scope_id": "scope.server.authoritative",
            "visibility_level": "nondiegetic",
        }
    return law_profile, authority


def _run_server_demography_tick(state: dict, runtime: dict, server_tick: int) -> Dict[str, object]:
    process_id = "process.demography_tick"
    law_profile, authority_context = _server_demography_authority(runtime)
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
        "intent_id": "intent.server.demography.tick.{}".format(int(server_tick)),
        "process_id": process_id,
        "inputs": inputs,
    }
    executed = execute_intent(
        state=state,
        intent=intent_payload,
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices=dict(runtime.get("registry_payloads") or {}),
        policy_context=_runtime_policy_context(runtime),
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
    universe_state = dict((_runtime_server(runtime).get("universe_state") or {}))
    mobility_surface = compute_mobility_proof_hashes(
        travel_event_rows=list(universe_state.get("travel_events") or []),
        edge_occupancy_rows=list(universe_state.get("edge_occupancies") or []),
        signal_state_rows=list(universe_state.get("mobility_signals") or []),
    )
    elec_surface = dict(universe_state.get("elec_proof_surface") or {})
    mobility_surface.update(
        {
            "power_flow_hash": str(elec_surface.get("power_flow_hash", universe_state.get("power_flow_hash", ""))).strip(),
            "power_flow_hash_chain": str(
                elec_surface.get("power_flow_hash_chain", universe_state.get("power_flow_hash_chain", ""))
            ).strip(),
            "fault_state_hash_chain": str(
                elec_surface.get("fault_state_hash_chain", universe_state.get("fault_state_hash_chain", ""))
            ).strip(),
            "protection_state_hash_chain": str(
                elec_surface.get("protection_state_hash_chain", universe_state.get("protection_state_hash_chain", ""))
            ).strip(),
            "degradation_event_hash_chain": str(
                elec_surface.get("degradation_event_hash_chain", universe_state.get("degradation_event_hash_chain", ""))
            ).strip(),
            "degradation_hash_chain": str(universe_state.get("degradation_hash_chain", "")).strip(),
            "maintenance_action_hash_chain": str(universe_state.get("maintenance_action_hash_chain", "")).strip(),
            "trip_event_hash_chain": str(
                elec_surface.get("trip_event_hash_chain", universe_state.get("trip_event_hash_chain", ""))
            ).strip(),
            "trip_explanation_hash_chain": str(
                elec_surface.get("trip_explanation_hash_chain", universe_state.get("trip_explanation_hash_chain", ""))
            ).strip(),
            "momentum_hash_chain": str(universe_state.get("momentum_hash_chain", "")).strip(),
            "impulse_event_hash_chain": str(universe_state.get("impulse_event_hash_chain", "")).strip(),
            "energy_ledger_hash_chain": str(universe_state.get("energy_ledger_hash_chain", "")).strip(),
            "boundary_flux_hash_chain": str(universe_state.get("boundary_flux_hash_chain", "")).strip(),
            "combustion_hash_chain": str(universe_state.get("combustion_hash_chain", "")).strip(),
            "emission_hash_chain": str(universe_state.get("emission_hash_chain", "")).strip(),
            "impulse_hash_chain": str(universe_state.get("impulse_hash_chain", "")).strip(),
            "process_run_hash_chain": str(universe_state.get("process_run_hash_chain", "")).strip(),
            "batch_quality_hash_chain": str(universe_state.get("batch_quality_hash_chain", "")).strip(),
            "yield_model_hash_chain": str(universe_state.get("yield_model_hash_chain", "")).strip(),
            "quantity_tolerance_registry_hash": str(universe_state.get("quantity_tolerance_registry_hash", "")).strip(),
            "rounding_mode_policy_hash": str(universe_state.get("rounding_mode_policy_hash", "")).strip(),
            "entropy_hash_chain": str(universe_state.get("entropy_hash_chain", "")).strip(),
            "entropy_reset_events_hash_chain": str(
                universe_state.get("entropy_reset_events_hash_chain", universe_state.get("entropy_reset_hash_chain", ""))
            ).strip(),
            "fluid_flow_hash_chain": str(universe_state.get("fluid_flow_hash_chain", "")).strip(),
            "leak_hash_chain": str(universe_state.get("leak_hash_chain", "")).strip(),
            "burst_hash_chain": str(universe_state.get("burst_hash_chain", "")).strip(),
            "relief_event_hash_chain": str(universe_state.get("relief_event_hash_chain", "")).strip(),
            "field_update_hash_chain": str(universe_state.get("field_update_hash_chain", "")).strip(),
            "field_sample_hash_chain": str(universe_state.get("field_sample_hash_chain", "")).strip(),
            "boundary_field_exchange_hash_chain": str(
                universe_state.get("boundary_field_exchange_hash_chain", "")
            ).strip(),
            "time_mapping_hash_chain": str(universe_state.get("time_mapping_hash_chain", "")).strip(),
            "schedule_domain_evaluation_hash": str(
                universe_state.get("schedule_domain_evaluation_hash", "")
            ).strip(),
            "time_adjust_event_hash_chain": str(
                universe_state.get("time_adjust_event_hash_chain", "")
            ).strip(),
            "compaction_marker_hash_chain": str(
                universe_state.get("compaction_marker_hash_chain", "")
            ).strip(),
            "compaction_pre_anchor_hash": str(
                universe_state.get("compaction_pre_anchor_hash", "")
            ).strip(),
            "compaction_post_anchor_hash": str(
                universe_state.get("compaction_post_anchor_hash", "")
            ).strip(),
            "drift_policy_id": str(universe_state.get("drift_policy_id", "drift.none")).strip() or "drift.none",
        }
    )
    bundle = build_control_proof_bundle_from_markers(
        tick_start=int(tick),
        tick_end=int(tick),
        decision_markers=markers,
        mobility_proof_surface=mobility_surface,
        extensions={
            "network_policy_id": POLICY_ID_SERVER_AUTHORITATIVE,
            "source": "server_authoritative.intent_queue",
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
            "Fix control proof bundle payload generation before retrying tick advance.",
            {"schema_id": "control_proof_bundle", "tick": str(int(tick))},
            "$.control_proof_bundle",
        )
    bundle_rel = norm(os.path.join("control_proofs", "control.proof.tick.{}.json".format(int(tick))))
    bundle_ref = _write_runtime_artifact(runtime=runtime, rel_path=bundle_rel, payload=bundle)
    server = dict(runtime.get("server") or {})
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


def _module_enabled(runtime: dict, module_id: str) -> bool:
    return bool(anti_cheat_module_enabled(runtime=runtime, module_id=module_id))


def _module_action(runtime: dict, module_id: str, fallback: str = "audit") -> str:
    return str(anti_cheat_default_action(runtime=runtime, module_id=module_id, fallback=fallback))


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
    emitted = anti_cheat_emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        peer_id=str(peer_id),
        module_id=str(module_id),
        severity=str(severity),
        reason_code=str(reason_code),
        evidence=list(evidence or []),
        default_action_token=str(default_action),
    )
    event = dict(emitted.get("event") or {})
    if not event:
        return {}
    event["action"] = str(emitted.get("action", _module_action(runtime=runtime, module_id=module_id, fallback=default_action)))
    return event


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
            path,
        )
    if token == "terminate":
        return refusal(
            "refusal.ac.policy_violation",
            "anti-cheat policy escalated this peer to terminate action",
            "Resolve anti-cheat violations and reconnect using a compliant client state.",
            dict(relevant_ids or {}),
            path,
        )
    if action_blocks_submission(token):
        return refusal(
            str(fallback_reason_code),
            str(fallback_message),
            str(fallback_remediation),
            dict(relevant_ids or {}),
            str(path),
        )
    return {"result": "complete", "accepted": False, "action": token}


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

    server_policy_id = str(network.get("server_policy_id", "")).strip()
    server_policy = {}
    if isinstance(registry_payloads, dict):
        server_policy = _policy_row(
            dict(registry_payloads.get("net_server_policy_registry") or {}),
            server_policy_id,
        )
    server_profile = {}
    server_profile_id = str(network.get("server_profile_id", "")).strip()
    if isinstance(registry_payloads, dict):
        server_profile = _server_profile_row(
            dict(registry_payloads.get("server_profile_registry") or {}),
            server_profile_id,
        )
    server_profile_extensions = dict(server_profile.get("extensions") or {})
    server_extensions = dict(server_policy.get("extensions") or {})
    cosmetic_policy_id = (
        str(server_profile_extensions.get("cosmetic_policy_id", "")).strip()
        or str(server_extensions.get("cosmetic_policy_id", "")).strip()
    )
    control_policy = {
        "allowed_view_modes": _sorted_tokens(list(server_extensions.get("allowed_view_modes") or [])),
        "allow_cross_shard_follow": bool(server_extensions.get("allow_cross_shard_follow", False)),
        "allow_cross_shard_collision": bool(server_extensions.get("allow_cross_shard_collision", False)),
        "allow_cross_shard_possession": bool(server_extensions.get("allow_cross_shard_possession", False)),
        "allow_srz_transfer": bool(server_extensions.get("allow_srz_transfer", False)),
        "cosmetic_policy_id": cosmetic_policy_id,
    }

    cadence = _snapshot_cadence(replication_policy_row, explicit=int(snapshot_cadence_ticks))
    registry_hashes = _registry_hashes(lock_payload)
    artifacts_rel = norm(os.path.join("build", "net", "authoritative", str(save_id)))
    registry_payloads_copy = copy.deepcopy(registry_payloads if isinstance(registry_payloads, dict) else {})
    representation_state = {
        "assignments": {},
        "events": [],
    }
    registry_payloads_copy["representation_state"] = representation_state

    runtime = {
        "schema_version": "1.0.0",
        "policy_id": POLICY_ID_SERVER_AUTHORITATIVE,
        "repo_root": norm(repo_root),
        "save_id": str(save_id),
        "artifacts_rel": artifacts_rel,
        "session_spec": copy.deepcopy(session_spec if isinstance(session_spec, dict) else {}),
        "lock_payload": copy.deepcopy(lock_payload if isinstance(lock_payload, dict) else {}),
        "registry_payloads": registry_payloads_copy,
        "universe_identity": copy.deepcopy(universe_identity if isinstance(universe_identity, dict) else {}),
        "identity_ref": norm(os.path.join("saves", str(save_id), "universe_identity.json")),
        "state_ref": norm(os.path.join("saves", str(save_id), "universe_state.json")),
        "server_policy": dict(server_policy),
        "server_profile": dict(server_profile),
        "control_policy": control_policy,
        "representation_state": representation_state,
        "anti_cheat": {
            "policy_id": anti_cheat_policy_id,
            "modules_enabled": _sorted_tokens(list(anti_cheat_policy.get("modules_enabled") or [])),
            "default_actions": dict(anti_cheat_policy.get("default_actions") or {}),
            "extensions": dict(anti_cheat_policy.get("extensions") or {}),
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
            "last_ledger_hash": "",
            "last_composite_hash": _zero_hash(),
            "last_control_proof_hash": "",
            "last_control_proof_bundle_ref": "",
            "hash_anchor_frames": [],
            "control_proof_bundles": [],
            "snapshots": [],
            "snapshot_peer_models": {},
            "snapshot_peer_memory": {},
            "snapshot_cadence_ticks": int(cadence),
            "baseline_snapshot_id": "",
            "anti_cheat_events": [],
            "anti_cheat_enforcement_actions": [],
            "anti_cheat_refusal_injections": [],
            "anti_cheat_anchor_mismatches": [],
            "anti_cheat_violation_counters": {},
            "terminated_peers": [],
            "perceived_deltas": [],
            "refusals": [],
            "conservation_runtime_by_shard": {},
            "conservation_ledgers": [],
        },
        "clients": {},
    }
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
        decision = check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int((runtime.get("server") or {}).get("network_tick", 0), 0),
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

    server = dict(runtime.get("server") or {})
    peer_id = str(envelope.get("source_peer_id", "")).strip()
    clients = dict(runtime.get("clients") or {})
    if peer_id not in clients:
        decision = check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            allowed=False,
            reason_code="refusal.net.authority_violation",
            evidence=["source peer is not joined to authoritative runtime"],
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.authority_violation",
            fallback_message="source peer is not joined to server-authoritative runtime",
            fallback_remediation="Join peer via baseline snapshot before submitting intents.",
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

    target_shard_id = str(envelope.get("target_shard_id", "")).strip()
    if target_shard_id != DEFAULT_SHARD_ID:
        decision = check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=_as_int(server.get("network_tick", 0), 0),
            peer_id=peer_id,
            allowed=False,
            reason_code="refusal.net.shard_target_invalid",
            evidence=["target_shard_id must be shard.0 for current authoritative runtime"],
            default_action_token="refuse",
        )
        return _apply_enforcement_result(
            action=str(decision.get("action", "refuse")),
            fallback_reason_code="refusal.net.shard_target_invalid",
            fallback_message="target_shard_id '{}' is invalid for current authoritative runtime".format(target_shard_id or "<empty>"),
            fallback_remediation="Route envelopes to shard.0 until distributed SRZ replication is enabled.",
            relevant_ids={"target_shard_id": target_shard_id or "<empty>"},
            path="$.target_shard_id",
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
            evidence=["envelope pack_lock_hash mismatches server lock hash"],
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
            fallback_message="deterministic_sequence_number is non-monotonic for peer '{}'".format(peer_id),
            fallback_remediation="Submit envelope sequence numbers monotonically per peer.",
            relevant_ids={"peer_id": peer_id, "expected_sequence": str(expected_next), "received_sequence": str(sequence)},
            path="$.deterministic_sequence_number",
        )

    payload = dict(envelope.get("payload") or {})
    process_id = str(payload.get("process_id", "")).strip()
    if process_id in MOVEMENT_PROCESS_IDS:
        limits = _movement_limits(runtime=runtime)
        movement_inputs = dict(payload.get("inputs") or {})
        submission_tick = _as_int(envelope.get("submission_tick", 0), 0)
        existing_movement_count = 0
        for queued in list(server.get("intent_queue") or []):
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
    ledger_hash = str(server.get("last_ledger_hash", "")).strip()
    performance_state = dict(state.get("performance_state") or {})
    transition_events = list(performance_state.get("transition_events") or [])
    transition_event_hash = canonical_sha256(
        sorted(
            (dict(item) for item in transition_events if isinstance(item, dict)),
            key=lambda item: (
                int(_as_int(item.get("tick", 0), 0)),
                str(item.get("shard_id", "")),
                str(item.get("region_id", "")),
                str(item.get("event_id", "")),
            ),
        )
    )
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
        ledger_hash=str(ledger_hash),
        transition_event_hash=str(transition_event_hash),
        control_decision_hash=str(server.get("last_control_proof_hash", "")),
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
        "extensions": {
            "ledger_hash": str(ledger_hash),
            "transition_event_hash": str(transition_event_hash),
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

    baseline_proof = _emit_control_proof_bundle(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(tick),
        envelope_rows=[],
    )
    if str(baseline_proof.get("result", "")) != "complete":
        return baseline_proof

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
        "extensions": {
            "control_proof_bundle_ref": str(((runtime.get("server") or {}).get("last_control_proof_bundle_ref", ""))),
            "control_proof_hash": str(((runtime.get("server") or {}).get("last_control_proof_hash", ""))),
        },
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
    tick_ledger_hash = ""

    clients = dict(runtime.get("clients") or {})
    state = dict(server.get("universe_state") or {})
    for envelope in ready:
        peer_id = str(envelope.get("source_peer_id", "")).strip()
        client = dict(clients.get(peer_id) or {})
        payload = dict(envelope.get("payload") or {})
        process_id = str(payload.get("process_id", "")).strip()
        inputs = payload.get("inputs")
        if not process_id or not isinstance(inputs, dict):
            decision = check_input_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                valid=False,
                reason_code="refusal.net.envelope_invalid",
                evidence=["intent envelope payload shape invalid"],
                default_action_token="refuse",
            )
            enforcement = _apply_enforcement_result(
                action=str(decision.get("action", "refuse")),
                fallback_reason_code="refusal.net.envelope_invalid",
                fallback_message="intent envelope payload must contain process_id and inputs",
                fallback_remediation="Fix envelope payload structure and resend.",
                relevant_ids={"envelope_id": str(envelope.get("envelope_id", ""))},
                path="$.payload",
            )
            if str(enforcement.get("result", "")) != "complete":
                processed_rows.append(
                    {
                        "envelope_id": str(envelope.get("envelope_id", "")),
                        "peer_id": peer_id,
                        "result": "refused",
                        "refusal": dict(enforcement.get("refusal") or {}),
                    }
                )
            else:
                processed_rows.append(
                    {
                        "envelope_id": str(envelope.get("envelope_id", "")),
                        "peer_id": peer_id,
                        "result": "dropped",
                        "action": str(enforcement.get("action", "")),
                    }
                )
            continue

        intent_payload = {
            "intent_id": str(envelope.get("intent_id", "")),
            "process_id": process_id,
            "inputs": dict(inputs),
        }
        executed = execute_intent(
            state=state,
            intent=intent_payload,
            law_profile=dict(client.get("law_profile") or {}),
            authority_context=dict(client.get("authority_context") or {}),
            navigation_indices=dict(runtime.get("registry_payloads") or {}),
            policy_context=_runtime_policy_context(runtime),
        )
        debug_assert_after_execute(state=state, intent=intent_payload, result=dict(executed or {}))
        if str(executed.get("result", "")) != "complete":
            refusal_reason_code = str(((executed.get("refusal") or {}).get("reason_code", "refusal.net.authority_violation")))
            unauthorized_time_control = _is_unauthorized_time_control_refusal(
                process_id=process_id,
                reason_code=refusal_reason_code,
            )
            if unauthorized_time_control:
                _emit_anti_cheat_event(
                    repo_root=repo_root,
                    runtime=runtime,
                    tick=int(server_tick),
                    peer_id=peer_id,
                    module_id="ac.module.authority_integrity",
                    severity="violation",
                    reason_code="ac.time_control.unauthorized_change_attempt",
                    evidence=[
                        "process_id={}".format(process_id),
                        "refusal_reason_code={}".format(refusal_reason_code),
                        "envelope_id={}".format(str(envelope.get("envelope_id", ""))),
                    ],
                    default_action="refuse",
                )
            decision = check_authority_integrity(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                allowed=False,
                reason_code=refusal_reason_code,
                evidence=["authoritative process execution refused submitted envelope"],
                default_action_token="refuse",
            )
            decision_action = str(decision.get("action", "refuse"))
            if unauthorized_time_control:
                decision_action = "refuse"
            enforcement = _apply_enforcement_result(
                action=decision_action,
                fallback_reason_code=refusal_reason_code,
                fallback_message="authoritative process execution refused submitted envelope",
                fallback_remediation="Resolve authority/law violations then resend deterministic intent envelope.",
                relevant_ids={"envelope_id": str(envelope.get("envelope_id", "")), "peer_id": peer_id},
                path="$.payload.process_id",
            )
            if str(enforcement.get("result", "")) != "complete":
                processed_rows.append(
                    {
                        "envelope_id": str(envelope.get("envelope_id", "")),
                        "peer_id": peer_id,
                        "result": "refused",
                        "refusal": dict(enforcement.get("refusal") or {}),
                    }
                )
                server_refusals = list((runtime.get("server") or {}).get("refusals") or [])
                server_refusals.append(
                    {
                        "tick": int(server_tick),
                        "peer_id": peer_id,
                        "envelope_id": str(envelope.get("envelope_id", "")),
                        "reason_code": str(((enforcement.get("refusal") or {}).get("reason_code", ""))),
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
            else:
                processed_rows.append(
                    {
                        "envelope_id": str(envelope.get("envelope_id", "")),
                        "peer_id": peer_id,
                        "result": "dropped",
                        "action": str(enforcement.get("action", "")),
                    }
                )
            continue

        if process_id in MOVEMENT_PROCESS_IDS:
            limits = _movement_limits(runtime=runtime)
            moved_distance_mm = max(0, _as_int(executed.get("movement_distance_mm", 0), 0))
            moved_dt_ticks = max(1, _as_int(executed.get("dt_ticks", 1), 1))
            max_distance_mm = int(limits["max_displacement_mm_per_tick"]) * int(moved_dt_ticks)
            check_behavioral_detection(
                repo_root=repo_root,
                runtime=runtime,
                tick=int(server_tick),
                peer_id=peer_id,
                suspicious=bool(int(moved_distance_mm) > int(max_distance_mm)),
                reason_code="ac.movement.actual_displacement_exceeded",
                evidence=[
                    "movement displacement exceeded deterministic threshold after authoritative execution",
                    "agent_id={},moved_distance_mm={},max_distance_mm={},dt_ticks={}".format(
                        str(executed.get("agent_id", "")),
                        int(moved_distance_mm),
                        int(max_distance_mm),
                        int(moved_dt_ticks),
                    ),
                ],
                default_action_token="audit",
            )

        processed_rows.append(
            {
                "envelope_id": str(envelope.get("envelope_id", "")),
                "peer_id": peer_id,
                "result": "complete",
                "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
            }
        )
        ledger_token = str(executed.get("ledger_hash", "")).strip()
        if ledger_token:
            tick_ledger_hash = ledger_token

    server_peer_id = str((runtime.get("server") or {}).get("peer_id", "")).strip() or "peer.server"
    demography_tick_summary: Dict[str, object] = {
        "result": "skipped",
        "reason": "not_evaluated",
    }
    demography_tick = _run_server_demography_tick(
        state=state,
        runtime=runtime,
        server_tick=int(server_tick),
    )
    demography_result = str(demography_tick.get("result", ""))
    if demography_result == "complete":
        processed_rows.append(
            {
                "envelope_id": "auto.demography.tick.{}".format(int(server_tick)),
                "peer_id": server_peer_id,
                "result": "complete",
                "state_hash_anchor": str(demography_tick.get("state_hash_anchor", "")),
            }
        )
        demography_ledger_hash = str(demography_tick.get("ledger_hash", "")).strip()
        if demography_ledger_hash:
            tick_ledger_hash = demography_ledger_hash
        demography_tick_summary = {
            "result": "complete",
            "state_hash_anchor": str(demography_tick.get("state_hash_anchor", "")),
            "demography_policy_id": str(demography_tick.get("demography_policy_id", "")),
            "processed_cohort_count": int(demography_tick.get("processed_cohort_count", 0) or 0),
            "total_births": int(demography_tick.get("total_births", 0) or 0),
            "total_deaths": int(demography_tick.get("total_deaths", 0) or 0),
        }
    elif demography_result == "refused":
        refusal_payload = dict(demography_tick.get("refusal") or {})
        processed_rows.append(
            {
                "envelope_id": "auto.demography.tick.{}".format(int(server_tick)),
                "peer_id": server_peer_id,
                "result": "refused",
                "refusal": refusal_payload,
            }
        )
        server_refusals = list((runtime.get("server") or {}).get("refusals") or [])
        server_refusals.append(
            {
                "tick": int(server_tick),
                "peer_id": server_peer_id,
                "envelope_id": "auto.demography.tick.{}".format(int(server_tick)),
                "reason_code": str(refusal_payload.get("reason_code", "")),
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
        demography_tick_summary = {
            "result": "refused",
            "refusal": refusal_payload,
        }
    else:
        demography_tick_summary = {
            "result": "skipped",
            "reason": str(demography_tick.get("reason", "not_enabled")),
        }

    conservation_policy_context = _runtime_policy_context(runtime)
    if not tick_ledger_hash:
        noop_finalized = finalize_noop_tick(
            policy_context=conservation_policy_context,
            tick=int(_state_tick(state)),
            process_id="process.tick_ledger",
        )
        if str(noop_finalized.get("result", "")) == "complete":
            tick_ledger_hash = str(noop_finalized.get("ledger_hash", "")).strip()
    ledger_rows = _sync_conservation_ledgers_to_server(runtime, conservation_policy_context)
    _emit_conservation_anti_cheat_signals(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(server_tick),
        ledger_rows=ledger_rows,
    )

    server = dict(runtime.get("server") or {})
    server["network_tick"] = int(server_tick)
    server["intent_queue"] = sorted((dict(row) for row in pending if isinstance(row, dict)), key=_queue_sort_key)
    server["universe_state"] = state
    server["last_ledger_hash"] = str(tick_ledger_hash or server.get("last_ledger_hash", ""))
    runtime["server"] = server

    proof_result = _emit_control_proof_bundle(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(server_tick),
        envelope_rows=[dict(row) for row in list(ready or []) if isinstance(row, dict)],
    )
    if str(proof_result.get("result", "")) != "complete":
        return proof_result

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
        memory_state = dict(client.get("memory_state") or {})
        memory_store_hash = str(memory_state.get("store_hash", ""))
        delta_payload = {
            "schema_version": "1.0.0",
            "perceived_delta_id": "pdelta.{}.tick.{}".format(peer_id, int(server_tick)),
            "tick": int(server_tick),
            "replace": perceived_model,
            "previous_hash": str(client.get("last_perceived_hash", "")),
            "extensions": {
                "memory_store_hash": memory_store_hash,
                "memory_state_hash": canonical_sha256(memory_state),
            },
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
                tick=int(server_tick),
                peer_id=peer_id,
                expected_hash=str(perceived_hash),
                actual_hash=str(actual_hash),
                reason_code="refusal.net.resync_required",
                default_action_token="audit",
            )
            enforcement = _apply_enforcement_result(
                action=str(state_check.get("action", "audit")),
                fallback_reason_code="refusal.net.resync_required",
                fallback_message="perceived hash mismatch during delta apply",
                fallback_remediation="Request deterministic snapshot resync and retry.",
                relevant_ids={"peer_id": peer_id, "tick": str(server_tick)},
                path="$.perceived_delta",
            )
            if str(enforcement.get("result", "")) != "complete":
                return enforcement
            continue
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

    anti_cheat_emit_event(
        repo_root=repo_root,
        runtime=runtime,
        tick=int(server_tick),
        peer_id=str(server.get("peer_id", "peer.server")),
        module_id="ac.module.behavioral_detection",
        severity="info",
        reason_code="ac.behavior.tick_complete",
        evidence=["server-authoritative tick completed"],
        default_action_token="audit",
    )
    return {
        "result": "complete",
        "tick": int(server_tick),
        "ledger_hash": str(tick_ledger_hash),
        "processed_envelopes": processed_rows,
        "demography_tick": demography_tick_summary,
        "hash_anchor_frame": frame,
        "control_proof_bundle": dict(proof_result.get("bundle") or {}),
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
    proof = export_proof_artifacts(
        repo_root=repo_root,
        runtime=runtime,
        run_id="tick.{}".format(int(server.get("network_tick", 0) or 0)),
    )
    return {
        "result": "complete",
        "queue_results": queued,
        "steps": steps,
        "final_tick": int(server.get("network_tick", 0) or 0),
        "final_composite_hash": str((frames[-1] if frames else {}).get("composite_hash", "")),
        "control_proof_bundle_ref": str(server.get("last_control_proof_bundle_ref", "")),
        "control_proof_hash": str(server.get("last_control_proof_hash", "")),
        "anti_cheat_proof": dict(proof),
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
