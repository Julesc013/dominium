"""Shared CIV-2 cohort test fixtures."""

from __future__ import annotations

import copy
from typing import Dict, List


def base_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {
            "tick": 0,
            "timestamp_utc": "1970-01-01T00:00:00Z",
        },
        "agent_states": [],
        "world_assemblies": [
            "camera.main",
        ],
        "active_law_references": [
            "law.test.cohort",
        ],
        "session_references": [
            "session.testx.cohort",
        ],
        "history_anchors": [],
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "time_control": {
            "rate_permille": 1000,
            "paused": False,
            "accumulator_permille": 0,
        },
        "process_log": [],
        "faction_assemblies": [],
        "affiliations": [],
        "territory_assemblies": [],
        "diplomatic_relations": [],
        "cohort_assemblies": [],
        "body_assemblies": [],
        "collision_state": {
            "last_tick_resolved_pairs": [],
            "last_tick_unresolved_pairs": [],
            "last_tick_pair_count": 0,
            "last_tick_anchor": "",
        },
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "performance_state": {
            "budget_policy_id": "policy.budget.test.cohort",
            "fidelity_policy_id": "policy.fidelity.test.cohort",
            "activation_policy_id": "policy.activation.test.cohort",
            "compute_units_used": 0,
            "max_compute_units_per_tick": 5000,
            "budget_outcome": "ok",
            "active_region_count": 0,
            "fidelity_tier_counts": {
                "coarse": 0,
                "medium": 0,
                "fine": 0,
            },
            "transition_log": [],
        },
    }


def mapping_policy_registry(max_micro_agents_per_cohort: int = 16) -> dict:
    return {
        "policies": [
            {
                "mapping_policy_id": "cohort.map.default",
                "description": "test mapping policy",
                "max_micro_agents_per_cohort": int(max(0, max_micro_agents_per_cohort)),
                "spawn_distribution_rules": {
                    "algorithm_id": "spawn.distribution.radial_deterministic.v1",
                    "identity_exposure": "standard",
                    "stable_sort_key": "cohort_id_then_slot",
                },
                "collapse_aggregation_rules": {
                    "algorithm_id": "collapse.aggregate.sum_and_modes.v1",
                    "stable_sort_key": "agent_id_lexicographic",
                },
                "anonymous_micro_agents": False,
                "extensions": {},
            },
            {
                "mapping_policy_id": "cohort.map.rank_strict",
                "description": "rank strict mapping policy",
                "max_micro_agents_per_cohort": int(max(0, max_micro_agents_per_cohort)),
                "spawn_distribution_rules": {
                    "algorithm_id": "spawn.distribution.radial_deterministic.v1",
                    "identity_exposure": "anonymous_unless_entitled",
                    "stable_sort_key": "cohort_id_then_slot",
                },
                "collapse_aggregation_rules": {
                    "algorithm_id": "collapse.aggregate.sum_and_modes.v1",
                    "stable_sort_key": "agent_id_lexicographic",
                },
                "anonymous_micro_agents": True,
                "extensions": {},
            },
        ]
    }


def law_profile(allowed_processes: List[str]) -> dict:
    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map: Dict[str, str] = {}
    privilege_map: Dict[str, str] = {}
    for process_id in unique_processes:
        if process_id in (
            "process.cohort_create",
            "process.cohort_expand_to_micro",
            "process.cohort_collapse_from_micro",
        ):
            entitlement_map[process_id] = "entitlement.civ.admin"
            privilege_map[process_id] = "operator"
        elif process_id == "process.affiliation_change_micro":
            entitlement_map[process_id] = "entitlement.civ.affiliation"
            privilege_map[process_id] = "observer"
        elif process_id == "process.region_management_tick":
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.cohort",
        "allowed_processes": unique_processes,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {
            "max_view_radius_km": 1000000,
            "allow_hidden_state_access": False,
        },
        "epistemic_policy_id": "ep.policy.player_diegetic",
    }


def authority_context(
    entitlements: List[str] | None = None,
    privilege_level: str = "operator",
) -> dict:
    rows = sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip()))
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.cohort",
        "experience_id": "profile.test.cohort",
        "law_profile_id": "law.test.cohort",
        "entitlements": rows,
        "epistemic_scope": {
            "scope_id": "scope.test.cohort",
            "visibility_level": "diegetic",
        },
        "privilege_level": str(privilege_level),
    }


def navigation_indices_for_roi() -> dict:
    return {
        "astronomy_catalog_index": {
            "entries": [
                {
                    "object_id": "earth",
                    "parent_id": "sol",
                    "kind": "body",
                    "frame_id": "frame.sol",
                    "search_keys": ["earth"],
                }
            ],
            "search_index": {
                "earth": ["earth"],
            },
        },
        "site_registry_index": {
            "sites": [],
            "search_index": {},
        },
        "ephemeris_registry": {"tables": []},
        "terrain_tile_registry": {"tiles": []},
    }


def policy_context_for_roi(
    max_entities_micro: int,
    mapping_max_micro: int,
    *,
    active_shard_id: str = "",
    shard_map: dict | None = None,
    strict_contracts: bool = False,
) -> dict:
    return {
        "activation_policy": {
            "policy_id": "policy.activation.test.cohort",
            "interest_radius_rules": [
                {
                    "kind": "body",
                    "priority": 0,
                    "activation_distance_mm": 1000000,
                    "deactivation_distance_mm": 1000000,
                    "anchor_spacing_mm": 1,
                }
            ],
            "hysteresis": {"enter_margin_mm": 0, "exit_margin_mm": 0},
        },
        "budget_policy": {
            "policy_id": "policy.budget.test.cohort",
            "max_regions_micro": 16,
            "max_compute_units_per_tick": 5000,
            "max_entities_micro": int(max(0, max_entities_micro)),
            "entity_compute_weight": 1,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
        },
        "fidelity_policy": {
            "policy_id": "policy.fidelity.test.cohort",
            "tiers": [
                {"tier_id": "coarse", "max_distance_mm": 1000000, "micro_entities_target": 0},
                {"tier_id": "medium", "max_distance_mm": 500000, "micro_entities_target": 8},
                {"tier_id": "fine", "max_distance_mm": 100000, "micro_entities_target": 16},
            ],
            "minimum_tier_by_kind": {"*": "coarse"},
            "switching_rules": {"upgrade_hysteresis_mm": 0, "degrade_hysteresis_mm": 0, "degrade_order": ["fine", "medium", "coarse"]},
        },
        "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=mapping_max_micro),
        "pack_lock_hash": "a" * 64,
        "active_shard_id": str(active_shard_id).strip(),
        "shard_map": dict(shard_map or {}),
        "strict_contracts": bool(strict_contracts),
    }


def copy_state(state: dict) -> dict:
    return copy.deepcopy(state)

