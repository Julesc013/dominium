"""Shared MAT-4 logistics test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.cohort_testlib import base_state as cohort_base_state


FIXED_POINT_FRACTIONAL_BITS = 24
FIXED_POINT_SCALE = 1 << FIXED_POINT_FRACTIONAL_BITS


def base_state() -> dict:
    state = copy.deepcopy(cohort_base_state())
    state.setdefault("logistics_manifests", [])
    state.setdefault("shipment_commitments", [])
    state.setdefault("logistics_node_inventories", [])
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


def with_inventory(
    state: dict,
    *,
    node_id: str,
    material_id: str,
    mass: int,
    batch_id: str = "batch.seed",
) -> dict:
    out = copy.deepcopy(state)
    rows = list(out.get("logistics_node_inventories") or [])
    rows.append(
        {
            "schema_version": "1.0.0",
            "node_id": str(node_id),
            "material_stocks": {str(material_id): int(max(0, int(mass)))},
            "batch_refs": [str(batch_id)],
            "inventory_hash": "",
            "extensions": {},
        }
    )
    out["logistics_node_inventories"] = rows
    return out


def logistics_graph(
    *,
    graph_id: str = "graph.logistics.test",
    from_node_id: str = "node.alpha",
    to_node_id: str = "node.beta",
    delay_ticks: int = 0,
    loss_fraction: int = 0,
    capacity_mass_per_tick: int = 10_000,
    cost_units_per_mass: int = 1,
    routing_rule_id: str = "route.direct_only",
) -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": str(graph_id),
        "nodes": [
            {
                "schema_version": "1.0.0",
                "node_id": str(from_node_id),
                "node_type": "depot",
                "location_ref": "site.alpha",
                "capacity_storage": 1_000_000,
                "tags": ["test"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "node_id": str(to_node_id),
                "node_type": "depot",
                "location_ref": "site.beta",
                "capacity_storage": 1_000_000,
                "tags": ["test"],
                "extensions": {},
            },
        ],
        "edges": [
            {
                "schema_version": "1.0.0",
                "edge_id": "edge.alpha_beta",
                "from_node_id": str(from_node_id),
                "to_node_id": str(to_node_id),
                "transport_mode": "road",
                "capacity_mass_per_tick": int(max(0, int(capacity_mass_per_tick))),
                "delay_ticks": int(max(0, int(delay_ticks))),
                "loss_fraction": int(max(0, int(loss_fraction))),
                "cost_units_per_mass": int(max(0, int(cost_units_per_mass))),
                "tags": ["test"],
                "extensions": {},
            }
        ],
        "deterministic_routing_rule_id": str(routing_rule_id),
        "version_introduced": "1.0.0",
        "extensions": {},
    }


def logistics_graph_registry(graph_rows: List[dict] | None = None) -> dict:
    return {"graphs": [dict(row) for row in list(graph_rows or []) if isinstance(row, dict)]}


def logistics_routing_rule_registry() -> dict:
    return {
        "routing_rules": [
            {
                "schema_version": "1.0.0",
                "rule_id": "route.direct_only",
                "description": "direct",
                "tie_break_policy": "edge_id_lexicographic",
                "allow_multi_hop": False,
                "constraints": {},
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "rule_id": "route.shortest_delay",
                "description": "shortest delay",
                "tie_break_policy": "edge_id_lexicographic",
                "allow_multi_hop": True,
                "constraints": {},
                "extensions": {},
            },
        ]
    }


def law_profile(allowed_processes: List[str]) -> dict:
    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map = {}
    privilege_map = {}
    for process_id in unique_processes:
        if process_id == "process.manifest_create":
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
        elif process_id == "process.manifest_tick":
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
        elif process_id == "process.inspect_generate_snapshot":
            entitlement_map[process_id] = "entitlement.inspect"
            privilege_map[process_id] = "observer"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.logistics",
        "allowed_processes": unique_processes,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1_000_000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def authority_context(entitlements: List[str] | None = None, privilege_level: str = "operator") -> dict:
    rows = sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip()))
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.logistics",
        "experience_id": "profile.test.logistics",
        "law_profile_id": "law.test.logistics",
        "entitlements": rows,
        "epistemic_scope": {"scope_id": "scope.test.logistics", "visibility_level": "nondiegetic"},
        "privilege_level": str(privilege_level),
    }


def policy_context(
    *,
    graph_rows: List[dict] | None = None,
    max_compute_units_per_tick: int = 1024,
    logistics_manifest_tick_budget: int = 128,
    logistics_max_active_manifests: int = 1000,
) -> dict:
    return {
        "physics_profile_id": "physics.test.logistics",
        "pack_lock_hash": "a" * 64,
        "logistics_graph_registry": logistics_graph_registry(graph_rows),
        "logistics_routing_rule_registry": logistics_routing_rule_registry(),
        "logistics_manifest_tick_budget": int(max(1, int(logistics_manifest_tick_budget))),
        "logistics_max_active_manifests": int(max(1, int(logistics_max_active_manifests))),
        "logistics_cost_units_per_manifest": 1,
        "logistics_cost_units_per_route_compute": 1,
        "budget_policy": {
            "policy_id": "policy.budget.test.logistics",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": int(max(0, int(max_compute_units_per_tick))),
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.test.logistics",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.test.logistics",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": int(max(0, int(max_compute_units_per_tick))),
                    "max_inspection_cost_units_per_tick": 32,
                    "extensions": {},
                }
            ]
        },
        "numeric_precision_policy": {
            "policy_id": "default_test",
            "fixed_point": {
                "fractional_bits": FIXED_POINT_FRACTIONAL_BITS,
                "storage_bits": 64,
                "overflow_behavior": "refuse",
                "error_budget_max": 0,
            },
        },
        "universe_physics_profile_registry": {
            "physics_profiles": [
                {
                    "physics_profile_id": "physics.test.logistics",
                    "allowed_exception_types": [
                        "exception.boundary_flux",
                        "exception.creation_annihilation",
                    ],
                }
            ]
        },
        "quantity_type_registry": {
            "quantity_types": [
                {"quantity_id": "quantity.mass", "dimension_id": "dim.mass"},
                {"quantity_id": "quantity.mass_energy_total", "dimension_id": "dim.energy"},
            ]
        },
        "quantity_registry": {
            "quantities": [
                {"quantity_id": "quantity.mass", "dimension_id": "dim.mass"},
                {"quantity_id": "quantity.mass_energy_total", "dimension_id": "dim.energy"},
            ]
        },
    }
