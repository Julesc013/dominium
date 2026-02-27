"""Shared MAT-5 construction test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.logistics_testlib import (
    base_state as logistics_base_state,
    logistics_graph_registry,
    logistics_routing_rule_registry,
    with_inventory as logistics_with_inventory,
)


def base_state() -> dict:
    state = copy.deepcopy(logistics_base_state())
    state.setdefault("construction_projects", [])
    state.setdefault("construction_steps", [])
    state.setdefault("construction_commitments", [])
    state.setdefault("construction_provenance_events", [])
    state.setdefault("installed_structure_instances", [])
    state.setdefault(
        "construction_runtime_state",
        {
            "next_event_sequence": 0,
            "last_project_tick": 0,
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
    rows = [dict(row) for row in list(out.get("logistics_node_inventories") or []) if isinstance(row, dict)]
    target_node_id = str(node_id)
    target_material_id = str(material_id)
    target_mass = int(max(0, int(mass)))
    target_batch_id = str(batch_id)
    matched = False
    for row in rows:
        if str(row.get("node_id", "")) != target_node_id:
            continue
        stocks = dict(row.get("material_stocks") or {})
        existing = int(stocks.get(target_material_id, 0) or 0)
        stocks[target_material_id] = int(existing + target_mass)
        row["material_stocks"] = dict((key, int(stocks[key])) for key in sorted(stocks.keys()))
        batch_refs = sorted(set(str(item).strip() for item in list(row.get("batch_refs") or []) + [target_batch_id] if str(item).strip()))
        row["batch_refs"] = batch_refs
        row["inventory_hash"] = ""
        matched = True
        break
    if not matched:
        out = logistics_with_inventory(
            out,
            node_id=target_node_id,
            material_id=target_material_id,
            mass=target_mass,
            batch_id=target_batch_id,
        )
    else:
        out["logistics_node_inventories"] = rows
    return out


def law_profile(allowed_processes: List[str]) -> dict:
    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map = {}
    privilege_map = {}
    for process_id in unique_processes:
        if process_id in (
            "process.construction_project_create",
            "process.construction_pause",
            "process.construction_resume",
            "process.manifest_create",
        ):
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
        elif process_id in ("process.construction_project_tick", "process.manifest_tick"):
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
        elif process_id == "process.inspect_generate_snapshot":
            entitlement_map[process_id] = "entitlement.inspect"
            privilege_map[process_id] = "observer"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.construction",
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
        "peer_id": "peer.test.construction",
        "experience_id": "profile.test.construction",
        "law_profile_id": "law.test.construction",
        "entitlements": rows,
        "epistemic_scope": {"scope_id": "scope.test.construction", "visibility_level": "nondiegetic"},
        "privilege_level": str(privilege_level),
    }


def construction_policy_registry(allow_parallel_steps: bool = True, max_parallel_steps: int = 4) -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "policy_id": "build.policy.default",
                "default_step_duration_ticks": {
                    "default": 3,
                    "part": 2,
                    "subassembly": 4,
                    "connector": 1,
                    "site_anchor": 5,
                },
                "allow_parallel_steps": bool(allow_parallel_steps),
                "max_parallel_steps": int(max(1, int(max_parallel_steps))),
                "deterministic_scheduling_rule_id": "schedule.ag_node_lexicographic",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "policy_id": "build.policy.rank_strict",
                "default_step_duration_ticks": {
                    "default": 5,
                    "part": 4,
                    "subassembly": 6,
                    "connector": 2,
                    "site_anchor": 8,
                },
                "allow_parallel_steps": False,
                "max_parallel_steps": 1,
                "deterministic_scheduling_rule_id": "schedule.ag_node_lexicographic",
                "extensions": {"rank_profile": True},
            },
        ]
    }


def policy_context(
    *,
    max_compute_units_per_tick: int = 1024,
    construction_max_projects_per_tick: int = 128,
    construction_max_parallel_steps_override: int = 0,
    construction_cost_units_per_active_step: int = 1,
    allow_parallel_steps: bool = True,
    max_parallel_steps: int = 4,
) -> dict:
    return {
        "physics_profile_id": "physics.test.construction",
        "pack_lock_hash": "b" * 64,
        "construction_policy_registry": construction_policy_registry(
            allow_parallel_steps=bool(allow_parallel_steps),
            max_parallel_steps=int(max_parallel_steps),
        ),
        "construction_policy_id": "build.policy.default",
        "construction_max_projects_per_tick": int(max(1, int(construction_max_projects_per_tick))),
        "construction_max_parallel_steps_override": int(max(0, int(construction_max_parallel_steps_override))),
        "construction_cost_units_per_active_step": int(max(1, int(construction_cost_units_per_active_step))),
        "logistics_graph_registry": logistics_graph_registry([]),
        "logistics_routing_rule_registry": logistics_routing_rule_registry(),
        "budget_policy": {
            "policy_id": "policy.budget.test.construction",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": int(max(0, int(max_compute_units_per_tick))),
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.test.construction",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.test.construction",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": int(max(0, int(max_compute_units_per_tick))),
                    "max_inspection_cost_units_per_tick": 64,
                    "extensions": {},
                }
            ]
        },
        "numeric_precision_policy": {
            "policy_id": "default_test",
            "fixed_point": {
                "fractional_bits": 24,
                "storage_bits": 64,
                "overflow_behavior": "refuse",
                "error_budget_max": 0,
            },
        },
        "universe_physics_profile_registry": {
            "physics_profiles": [
                {
                    "physics_profile_id": "physics.test.construction",
                    "allowed_exception_types": [
                        "exception.boundary_flux",
                        "exception.creation_annihilation",
                        "exception.numeric_error_budget",
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
