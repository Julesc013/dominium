"""Shared fixtures/helpers for LOD epistemic invariance TestX coverage."""

from __future__ import annotations

import copy
from typing import Dict


REGION_OBJECT_ID = "object.earth"
REGION_ID = "region.{}".format(REGION_OBJECT_ID)
LENS_ID = "lens.lod.test"


def base_state(camera_x_mm: int = 12345) -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "history_anchors": [],
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "entity_id": "agent.alpha",
                "body_id": "body.alpha",
                "owner_peer_id": None,
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
        "body_assemblies": [
            {
                "assembly_id": "body.alpha",
                "owner_assembly_id": REGION_OBJECT_ID,
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 300,
                    "height_mm": 1200,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        ],
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": int(camera_x_mm), "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 123, "pitch": 12, "roll": 6},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": LENS_ID,
            }
        ],
        "time_control": {"rate_permille": 1000, "paused": False, "accumulator_permille": 0},
        "process_log": [],
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "performance_state": {
            "budget_policy_id": "policy.budget.lod_test",
            "fidelity_policy_id": "policy.fidelity.lod_test",
            "activation_policy_id": "policy.activation.lod_test",
            "compute_units_used": 0,
            "max_compute_units_per_tick": 1000000,
            "budget_outcome": "ok",
            "active_region_count": 0,
            "fidelity_tier_counts": {"coarse": 0, "medium": 0, "fine": 0},
            "transition_log": [],
            "solver_binding_trace": [],
        },
    }


def law_profile() -> dict:
    return {
        "law_profile_id": "law.test.lod_invariance",
        "allowed_processes": [
            "process.region_management_tick",
            "process.region_expand",
            "process.region_collapse",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.region_management_tick": "session.boot",
            "process.region_expand": "session.boot",
            "process.region_collapse": "session.boot",
        },
        "process_privilege_requirements": {
            "process.region_management_tick": "observer",
            "process.region_expand": "observer",
            "process.region_collapse": "observer",
        },
        "allowed_lenses": [LENS_ID],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": False},
        "epistemic_policy_id": "ep.policy.lod.test",
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "experience_id": "profile.test.lod",
        "law_profile_id": "law.test.lod_invariance",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.lod.test", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }


def navigation_indices() -> dict:
    return {
        "astronomy_catalog_index": {
            "entries": [
                {
                    "object_id": REGION_OBJECT_ID,
                    "parent_id": "object.sol",
                    "kind": "body",
                    "frame_id": "frame.sol",
                    "search_keys": ["earth"],
                }
            ],
            "search_index": {"earth": [REGION_OBJECT_ID]},
        },
        "site_registry_index": {"sites": [], "search_index": {}},
        "ephemeris_registry": {"tables": []},
        "terrain_tile_registry": {"tiles": []},
    }


def activation_policy() -> dict:
    return {
        "policy_id": "policy.activation.lod_test",
        "interest_radius_rules": [
            {
                "kind": "body",
                "priority": 0,
                "activation_distance_mm": 1_000_000_000,
                "deactivation_distance_mm": 1_000_000_000,
                "anchor_spacing_mm": 1,
            }
        ],
        "hysteresis": {"enter_margin_mm": 0, "exit_margin_mm": 0},
    }


def budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.lod_test",
        "max_regions_micro": 16,
        "max_compute_units_per_tick": 1_000_000,
        "max_entities_micro": 1_000_000,
        "entity_compute_weight": 1,
        "fallback_behavior": "degrade_fidelity",
        "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
    }


def fidelity_policy() -> dict:
    return {
        "policy_id": "policy.fidelity.lod_test",
        "tiers": [
            {"tier_id": "coarse", "max_distance_mm": 1_000_000_000, "micro_entities_target": 0},
            {"tier_id": "medium", "max_distance_mm": 250_000_000, "micro_entities_target": 4},
            {"tier_id": "fine", "max_distance_mm": 25_000_000, "micro_entities_target": 8},
        ],
        "minimum_tier_by_kind": {"*": "coarse"},
        "switching_rules": {
            "upgrade_hysteresis_mm": 0,
            "degrade_hysteresis_mm": 0,
            "degrade_order": ["fine", "medium", "coarse"],
        },
    }


def policy_context(memory_enabled: bool, strict_contracts: bool) -> dict:
    payload: Dict[str, object] = {
        "activation_policy": activation_policy(),
        "budget_policy": budget_policy(),
        "fidelity_policy": fidelity_policy(),
        "strict_contracts": bool(strict_contracts),
    }
    if memory_enabled:
        payload["decay_model_registry"] = {
            "decay_models": [
                {
                    "decay_model_id": "ep.decay.session_basic",
                    "description": "deterministic session decay",
                    "ttl_rules": [
                        {"rule_id": "ttl.default", "channel_id": "*", "subject_kind": "*", "ttl_ticks": 64}
                    ],
                    "refresh_rules": [
                        {
                            "rule_id": "refresh.default",
                            "channel_id": "*",
                            "subject_kind": "*",
                            "refresh_on_observed": True,
                        }
                    ],
                    "eviction_rule_id": "evict.oldest_first",
                    "extensions": {},
                }
            ]
        }
        payload["eviction_rule_registry"] = {
            "eviction_rules": [
                {
                    "eviction_rule_id": "evict.oldest_first",
                    "description": "deterministic oldest-first eviction",
                    "algorithm_id": "evict.oldest_first",
                    "priority_by_channel": {},
                    "priority_by_subject_kind": {},
                    "extensions": {},
                }
            ]
        }
    return payload


def lod_observation(memory_enabled: bool) -> dict:
    retention_policy_id = "ep.retention.session_basic" if memory_enabled else "ep.retention.none"
    return {
        "lens": {
            "lens_id": LENS_ID,
            "lens_type": "diegetic",
            "required_entitlements": ["session.boot"],
            "observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.core.navigation",
                "ch.core.entities",
            ],
            "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
        },
        "epistemic_policy": {
            "epistemic_policy_id": "ep.policy.lod.test",
            "allowed_observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.core.navigation",
                "ch.core.entities",
            ],
            "forbidden_channels": [
                "ch.truth.overlay.terrain_height",
                "ch.truth.overlay.anchor_hash",
            ],
            "retention_policy_id": retention_policy_id,
            "inference_policy_id": "ep.infer.none",
            "max_precision_rules": [
                {
                    "rule_id": "near",
                    "channel_id": "ch.camera.state",
                    "max_distance_mm": 1000,
                    "position_quantization_mm": 1,
                    "orientation_quantization_mdeg": 1,
                },
                {
                    "rule_id": "far",
                    "channel_id": "ch.camera.state",
                    "max_distance_mm": 1_000_000_000,
                    "position_quantization_mm": 100,
                    "orientation_quantization_mdeg": 50,
                },
            ],
            "deterministic_filters": [
                "filter.channel_allow_deny.v1",
                "filter.quantize_precision.v1",
                "filter.interest_cull.v1",
                "filter.lod_epistemic_redaction.v1",
            ],
            "extensions": {"lod_precision_envelope_id": "ep.envelope.lod.test"},
        },
        "retention_policy": {
            "retention_policy_id": retention_policy_id,
            "memory_allowed": bool(memory_enabled),
            "max_memory_items": 64 if memory_enabled else 0,
            "decay_model_id": "ep.decay.session_basic" if memory_enabled else "ep.decay.none",
            "eviction_rule_id": "evict.oldest_first" if memory_enabled else "evict.none",
            "deterministic_eviction_rule_id": "evict.oldest_first" if memory_enabled else "evict.none",
            "extensions": {},
        },
        "allowed_new_channels": [],
        "allowed_new_entity_ids": [],
        "perception_interest_limit": 0,
    }


def execute_region_transition(
    state: dict,
    process_id: str,
    strict_contracts: bool,
    memory_enabled: bool,
    desired_tier: str = "fine",
    force_information_gain: bool = False,
) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    inputs = {
        "region_id": REGION_ID,
        "desired_tier": str(desired_tier),
        "enforce_lod_invariance": True,
        "lod_observation": lod_observation(memory_enabled=memory_enabled),
    }
    if force_information_gain:
        inputs["test_force_lod_information_gain"] = True

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.{}.{}".format(process_id.replace(".", "_"), "001"),
            "process_id": process_id,
            "inputs": inputs,
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices=navigation_indices(),
        policy_context=policy_context(memory_enabled=memory_enabled, strict_contracts=strict_contracts),
    )


def observe_state(state: dict, memory_enabled: bool, memory_state: dict | None = None) -> dict:
    from tools.xstack.sessionx.observation import observe_truth

    lod_cfg = lod_observation(memory_enabled=memory_enabled)
    lens = dict(lod_cfg.get("lens") or {})
    return observe_truth(
        truth_model={
            "schema_version": "1.0.0",
            "universe_state": copy.deepcopy(state),
            "registry_payloads": {},
        },
        lens=lens,
        law_profile=law_profile(),
        authority_context=authority_context(),
        viewpoint_id="viewpoint.lod.test",
        epistemic_policy=dict(lod_cfg.get("epistemic_policy") or {}),
        retention_policy=dict(lod_cfg.get("retention_policy") or {}),
        memory_state=dict(memory_state or {}),
        perception_interest_limit=None,
    )

