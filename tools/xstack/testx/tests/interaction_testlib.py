"""Shared RND-4 interaction fixtures."""

from __future__ import annotations

import copy

from tools.xstack.testx.tests.cohort_testlib import base_state as cohort_base_state


def base_state() -> dict:
    state = copy.deepcopy(cohort_base_state())
    agent_rows = [dict(item) for item in list(state.get("agent_states") or []) if isinstance(item, dict)]
    if not any(str(row.get("agent_id", "")).strip() == "agent.alpha" for row in agent_rows):
        agent_rows.append(
            {
                "agent_id": "agent.alpha",
                "body_id": "body.agent.alpha",
                "faction_id": "faction.alpha",
                "status": "active",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        )
    state["agent_states"] = sorted(agent_rows, key=lambda row: str(row.get("agent_id", "")))
    state.setdefault("order_assemblies", [])
    state.setdefault("order_queue_assemblies", [])
    state.setdefault("institution_assemblies", [])
    state.setdefault("role_assignment_assemblies", [])
    state.setdefault("instrument_assemblies", [])
    state.setdefault("tool_assemblies", [])
    state.setdefault("tool_bindings", [])
    state.setdefault("tasks", [])
    state.setdefault("task_provenance_events", [])
    state.setdefault("pending_task_completion_intents", [])
    return state


def perceived_model(*, tick: int = 7, target_semantic_id: str = "agent.alpha", include_truth_overlay: bool = True) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": int(max(0, int(tick)))},
        "channels": ["ch.core.entities", "ch.diegetic.radio_text"],
        "entities": {
            "entries": [
                {
                    "entity_id": str(target_semantic_id),
                    "semantic_id": str(target_semantic_id),
                    "entity_kind": "agent",
                    "faction_id": "faction.alpha",
                    "material_id": "mat.template.default_by_id_hash",
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }
    if include_truth_overlay:
        payload["truth_overlay"] = {"state_hash_anchor": "abc123" * 10 + "abcd"}
    return payload


def law_profile() -> dict:
    return {
        "law_profile_id": "law.test.interaction",
        "allowed_processes": [
            "process.inspect_generate_snapshot",
            "process.agent_move",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.inspect_generate_snapshot": "entitlement.inspect",
            "process.agent_move": "entitlement.move",
        },
        "process_privilege_requirements": {
            "process.inspect_generate_snapshot": "observer",
            "process.agent_move": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {
            "max_view_radius_km": 1000000,
            "allow_hidden_state_access": False,
        },
        "epistemic_policy_id": "ep.policy.player_diegetic",
    }


def authority_context(*, entitlements: list[str] | None = None, privilege_level: str = "observer") -> dict:
    rows = sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip()))
    return {
        "authority_origin": "client",
        "peer_id": "peer.test.interaction",
        "experience_id": "profile.test.interaction",
        "law_profile_id": "law.test.interaction",
        "entitlements": rows,
        "epistemic_scope": {
            "scope_id": "scope.test.interaction",
            "visibility_level": "diegetic",
        },
        "privilege_level": str(privilege_level),
    }


def interaction_action_registry() -> dict:
    return {
        "actions": [
            {
                "action_id": "interaction.inspect",
                "process_id": "process.inspect_generate_snapshot",
                "display_name": "Inspect",
                "target_kinds": ["agent", "cohort", "faction", "territory"],
                "parameter_schema_id": "dominium.schema.interaction.inspect_params",
                "preview_mode": "expensive",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {"cost_units_estimate": 4},
                "extensions": {},
            },
            {
                "action_id": "interaction.move_agent",
                "process_id": "process.agent_move",
                "display_name": "Move",
                "target_kinds": ["agent"],
                "parameter_schema_id": "dominium.intent.agent_move",
                "preview_mode": "cheap",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {"cost_units_estimate": 1},
                "extensions": {},
            },
        ]
    }


def policy_context(*, max_inspection_budget_per_tick: int = 32) -> dict:
    return {
        "physics_profile_id": "physics.test.interaction",
        "pack_lock_hash": "a" * 64,
        "net_policy_id": "net.policy.server_authoritative.v1",
        "registry_hashes": {"interaction_action_registry_hash": "b" * 64},
        "surface_type_registry": {
            "surface_types": [
                {
                    "schema_version": "1.0.0",
                    "surface_type_id": "surface.handle",
                    "description": "Handle surface",
                    "default_icon_tag": "glyph.surface.handle",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "surface_type_id": "surface.port",
                    "description": "Port surface",
                    "default_icon_tag": "glyph.surface.port",
                    "extensions": {},
                },
            ]
        },
        "tool_tag_registry": {
            "tool_tags": [
                {
                    "schema_version": "1.0.0",
                    "tool_tag_id": "tool_tag.operating",
                    "description": "Operating-capable tool",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "tool_tag_id": "tool_tag.fastening",
                    "description": "Fastening-capable tool",
                    "extensions": {},
                },
            ]
        },
        "surface_visibility_policy_registry": {
            "policies": [
                {
                    "schema_version": "1.0.0",
                    "policy_id": "visibility.default",
                    "requires_entitlement": None,
                    "requires_lens_channel": None,
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "policy_id": "visibility.lab_only",
                    "requires_entitlement": "entitlement.debug_view",
                    "requires_lens_channel": None,
                    "extensions": {},
                },
            ]
        },
        "tool_type_registry": {
            "tool_types": [
                {
                    "schema_version": "1.0.0",
                    "tool_type_id": "tool.wrench.basic",
                    "description": "Baseline wrench test fixture",
                    "default_tool_tags": ["tool_tag.fastening"],
                    "allowed_surface_types": ["surface.handle", "surface.port", "surface.fastener"],
                    "allowed_process_ids": ["process.agent_move", "process.inspect_generate_snapshot", "process.tool_use_prepare"],
                    "provides_instrument_channels": ["ch.diegetic.tool.torque"],
                    "extensions": {},
                }
            ]
        },
        "tool_effect_model_registry": {
            "effect_models": [
                {
                    "schema_version": "1.0.0",
                    "effect_model_id": "effect.basic_fastening",
                    "description": "Baseline fastening effect fixture",
                    "parameters": {
                        "efficiency_multiplier": 1000,
                        "precision_level": "medium",
                        "torque_limit": 5000,
                        "rate_limit": 1200,
                    },
                    "deterministic_rules": {
                        "randomness": "none",
                    },
                    "extensions": {},
                }
            ]
        },
        "task_type_registry": {
            "task_types": [
                {
                    "schema_version": "1.0.0",
                    "task_type_id": "task.tighten_fastener",
                    "description": "Deterministic fastening task fixture",
                    "default_progress_units_total": 16777216,
                    "required_tool_tags": ["tool_tag.fastening"],
                    "allowed_surface_types": ["surface.fastener", "surface.handle"],
                    "completion_process_id": "process.fastener_turn",
                    "progress_model_id": "progress.linear_default",
                    "extensions": {},
                }
            ]
        },
        "progress_model_registry": {
            "progress_models": [
                {
                    "schema_version": "1.0.0",
                    "progress_model_id": "progress.linear_default",
                    "description": "Deterministic linear task progress fixture",
                    "progress_rate_base": 4194304,
                    "tool_efficiency_applies": True,
                    "actor_efficiency_applies": False,
                    "extensions": {},
                }
            ]
        },
        "held_tool_tags": ["tool_tag.operating"],
        "budget_policy": {
            "policy_id": "policy.budget.test.interaction",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": 0,
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.test.interaction",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.test.interaction",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": 0,
                    "max_inspection_cost_units_per_tick": int(max(0, int(max_inspection_budget_per_tick))),
                    "extensions": {},
                }
            ]
        },
        "inspection_cache_policy_id": "cache.default",
        "inspection_cache_policy_registry": {
            "policies": [
                {
                    "cache_policy_id": "cache.default",
                    "enable_caching": True,
                    "invalidation_rules": ["invalidate.on_target_truth_hash_change"],
                    "max_cache_entries": 32,
                    "eviction_rule_id": "evict.deterministic_lru",
                    "extensions": {},
                }
            ]
        },
    }
