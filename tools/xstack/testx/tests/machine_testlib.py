"""Shared ACT-4 machine/port test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.interaction_testlib import (
    authority_context as interaction_authority_context,
    base_state as interaction_base_state,
    policy_context as interaction_policy_context,
)


def base_state() -> dict:
    state = copy.deepcopy(interaction_base_state())
    state.setdefault("machine_assemblies", [])
    state.setdefault("machine_ports", [])
    state.setdefault("machine_port_connections", [])
    state.setdefault("machine_provenance_events", [])
    state.setdefault("logistics_node_inventories", [])
    state.setdefault("logistics_manifests", [])
    state.setdefault("shipment_commitments", [])
    state.setdefault("logistics_provenance_events", [])
    state.setdefault(
        "logistics_runtime_state",
        {
            "next_event_sequence": 0,
            "last_manifest_tick": 0,
            "last_budget_outcome": "none",
            "extensions": {},
        },
    )
    return state


def with_machine(
    state: dict,
    *,
    machine_id: str = "machine.sawmill.alpha",
    machine_type_id: str = "machine.sawmill.basic",
    input_port_id: str = "port.sawmill.input",
    output_port_id: str = "port.sawmill.output",
    input_capacity_mass: int = 2000,
    output_capacity_mass: int = 2000,
    accepted_input_materials: List[str] | None = None,
    accepted_output_materials: List[str] | None = None,
) -> dict:
    out = copy.deepcopy(state)
    out["machine_assemblies"] = [
        {
            "schema_version": "1.0.0",
            "machine_id": str(machine_id),
            "machine_type_id": str(machine_type_id),
            "ports": [str(input_port_id), str(output_port_id)],
            "operational_state": "idle",
            "policy_ids": [],
            "extensions": {"site_ref": "site.machine.test"},
        }
    ]
    out["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": str(input_port_id),
            "machine_id": str(machine_id),
            "parent_structure_id": None,
            "port_type_id": "port.material_in",
            "accepted_material_tags": [],
            "accepted_material_ids": list(accepted_input_materials or ["material.wood_basic"]),
            "capacity_mass": int(max(0, int(input_capacity_mass))),
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": "visibility.default",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "port_id": str(output_port_id),
            "machine_id": str(machine_id),
            "parent_structure_id": None,
            "port_type_id": "port.material_out",
            "accepted_material_tags": [],
            "accepted_material_ids": list(accepted_output_materials or []),
            "capacity_mass": int(max(0, int(output_capacity_mass))),
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": "visibility.default",
            "extensions": {},
        },
    ]
    out["machine_port_connections"] = []
    out["machine_provenance_events"] = []
    return out


def with_node_inventory(
    state: dict,
    *,
    node_id: str = "node.factory.alpha",
    material_id: str = "material.wood_basic",
    mass: int = 2000,
    batch_id: str = "batch.node.seed",
) -> dict:
    out = copy.deepcopy(state)
    out["logistics_node_inventories"] = [
        {
            "schema_version": "1.0.0",
            "node_id": str(node_id),
            "material_stocks": {str(material_id): int(max(0, int(mass)))},
            "batch_refs": [str(batch_id)],
            "inventory_hash": "",
            "extensions": {},
        }
    ]
    return out


def law_profile(allowed_processes: List[str]) -> dict:
    unique = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map = dict((process_id, "entitlement.tool.operating") for process_id in unique)
    privilege_map = dict((process_id, "operator") for process_id in unique)
    return {
        "law_profile_id": "law.test.machine_ports",
        "allowed_processes": unique,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1_000_000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def authority_context(entitlements: List[str] | None = None, privilege_level: str = "operator") -> dict:
    rows = list(entitlements or ["entitlement.tool.operating"])
    return interaction_authority_context(entitlements=rows, privilege_level=privilege_level)


def policy_context() -> dict:
    policy = copy.deepcopy(interaction_policy_context())
    policy["port_type_registry"] = {
        "port_types": [
            {
                "schema_version": "1.0.0",
                "port_type_id": "port.material_in",
                "description": "Material input",
                "direction": "in",
                "payload_kind": "material",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "port_type_id": "port.material_out",
                "description": "Material output",
                "direction": "out",
                "payload_kind": "material",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "port_type_id": "port.energy_in",
                "description": "Energy input",
                "direction": "in",
                "payload_kind": "energy",
                "extensions": {},
            },
        ]
    }
    policy["machine_type_registry"] = {
        "machine_types": [
            {
                "schema_version": "1.0.0",
                "machine_type_id": "machine.sawmill.basic",
                "description": "Test sawmill",
                "required_ports": ["port.material_in", "port.material_out"],
                "supported_process_ids": [
                    "op.saw_planks",
                    "process.machine_operate",
                    "process.machine_pull_from_node",
                    "process.machine_push_to_node",
                ],
                "default_rate_params": {"rate_units_per_tick": 1000},
                "extensions": {},
            }
        ]
    }
    policy["machine_operation_registry"] = {
        "operations": [
            {
                "schema_version": "1.0.0",
                "operation_id": "op.saw_planks",
                "description": "Logs to planks",
                "machine_type_ids": ["machine.sawmill.basic"],
                "input_materials": {"material.wood_basic": 1000},
                "output_materials": {"material.wood_basic": 1000},
                "energy_delta_raw": 0,
                "extensions": {"recipe_tag": "wood_log_to_plank"},
            }
        ]
    }
    policy["material_class_registry"] = {
        "materials": [
            {"material_id": "material.wood_basic", "tags": ["tag.wood"], "extensions": {}},
            {"material_id": "material.steel_basic", "tags": ["tag.metal"], "extensions": {}},
        ]
    }
    return policy
