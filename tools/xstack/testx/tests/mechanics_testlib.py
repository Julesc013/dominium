"""Shared MECH-1 deterministic test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.construction_testlib import (
    authority_context as construction_authority_context,
    base_state as construction_base_state,
    law_profile as construction_law_profile,
    policy_context as construction_policy_context,
)


def base_state() -> dict:
    state = copy.deepcopy(construction_base_state())
    state.setdefault("structural_graphs", [])
    state.setdefault("structural_nodes", [])
    state.setdefault("structural_edges", [])
    state.setdefault("mechanics_provenance_events", [])
    state.setdefault("assembly_graph_detached_edges", [])
    state.setdefault("pending_mechanics_fracture_intents", [])
    state["structural_graphs"] = [
        {
            "schema_version": "1.0.0",
            "structural_graph_id": "structural.graph.alpha",
            "assembly_id": "assembly.structure_instance.alpha",
            "node_ids": ["structural.node.a", "structural.node.b"],
            "edge_ids": ["structural.edge.ab"],
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["structural_nodes"] = [
        {
            "schema_version": "1.0.0",
            "node_id": "structural.node.a",
            "assembly_part_id": "part.a",
            "applied_force": 500,
            "applied_torque": 0,
            "elastic_strain": 0,
            "plastic_strain": 0,
            "failure_state": "none",
            "deterministic_fingerprint": "",
            "extensions": {"integrity_permille": 1000},
        },
        {
            "schema_version": "1.0.0",
            "node_id": "structural.node.b",
            "assembly_part_id": "part.b",
            "applied_force": 500,
            "applied_torque": 0,
            "elastic_strain": 0,
            "plastic_strain": 0,
            "failure_state": "none",
            "deterministic_fingerprint": "",
            "extensions": {"integrity_permille": 1000},
        },
    ]
    state["structural_edges"] = [
        {
            "schema_version": "1.0.0",
            "edge_id": "structural.edge.ab",
            "node_a_id": "structural.node.a",
            "node_b_id": "structural.node.b",
            "connection_type_id": "conn.rigid_joint",
            "stiffness": 1000,
            "max_load": 1000,
            "fatigue_state": {},
            "failure_state": "none",
            "stress_ratio_permille": 0,
            "applied_load": 0,
            "effective_max_load": 1000,
            "last_evaluated_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    return state


def law_profile(allowed_processes: List[str]) -> dict:
    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.mechanics_tick"] = "session.boot"
    entitlements["process.mechanics_fracture"] = "session.boot"
    entitlements["process.weld_joint"] = "entitlement.tool.use"
    entitlements["process.cut_joint"] = "entitlement.tool.use"
    entitlements["process.drill_hole"] = "entitlement.tool.use"
    privileges["process.mechanics_tick"] = "observer"
    privileges["process.mechanics_fracture"] = "observer"
    privileges["process.weld_joint"] = "operator"
    privileges["process.cut_joint"] = "operator"
    privileges["process.drill_hole"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context(entitlements: List[str] | None = None, privilege_level: str = "operator") -> dict:
    return construction_authority_context(entitlements=entitlements, privilege_level=privilege_level)


def policy_context(max_compute_units_per_tick: int = 256) -> dict:
    policy = construction_policy_context(max_compute_units_per_tick=max_compute_units_per_tick)
    policy["connection_type_registry"] = {
        "connection_types": [
            {
                "schema_version": "1.0.0",
                "connection_type_id": "conn.rigid_joint",
                "description": "Rigid joint",
                "default_stiffness": 1000,
                "default_max_load": 1000,
                "supports_rotation": False,
                "supports_translation": False,
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "connection_type_id": "conn.rope",
                "description": "Tension-only rope",
                "default_stiffness": 800,
                "default_max_load": 800,
                "supports_rotation": True,
                "supports_translation": True,
                "extensions": {"tension_only": True},
            },
        ]
    }
    policy["effect_type_registry"] = {
        "effect_types": [
            {
                "schema_version": "1.0.0",
                "effect_type_id": "effect.machine_degraded",
                "description": "Machine degradation",
                "applies_to": ["assembly"],
                "modifies": ["machine_output_permille"],
                "default_visibility_policy_id": "effect.visibility.diegetic_alarm",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "effect_type_id": "effect.speed_cap",
                "description": "Speed cap",
                "applies_to": ["structure"],
                "modifies": ["max_speed_permille"],
                "default_visibility_policy_id": "effect.visibility.diegetic_alarm",
                "extensions": {},
            },
        ]
    }
    policy["stacking_policy_registry"] = {
        "stacking_policies": [
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.min",
                "mode": "min",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.multiply",
                "mode": "multiply",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.replace_latest",
                "mode": "replace",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            },
        ]
    }
    policy["mechanics_max_cost_units_per_tick"] = 64
    return policy

