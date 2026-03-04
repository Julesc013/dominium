"""Shared CHEM-1 combustion TestX fixtures."""

from __future__ import annotations

import copy
import sys


def seed_combustion_state(
    *,
    initial_fuel: int = 900,
    material_id: str = "material.fuel_oil_stub",
    temperature_value: int = 520,
    entropy_value: int = 0,
) -> dict:
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    target_id = "node.therm.source"
    state["thermal_fire_states"] = [
        {
            "schema_version": "1.0.0",
            "target_id": target_id,
            "active": True,
            "fuel_remaining": int(max(0, int(initial_fuel))),
            "last_update_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {
                "material_id": str(material_id),
                "mixture_ratio_permille": 1000,
            },
        }
    ]
    state["fire_state_rows"] = [dict(row) for row in state["thermal_fire_states"]]
    state["thermal_fire_events"] = []
    state["fire_event_rows"] = []
    state["thermal_node_status_rows"] = [
        {
            "schema_version": "1.0.0",
            "node_id": target_id,
            "temperature": int(temperature_value),
            "last_update_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {
                "temperature": int(temperature_value),
            },
        }
    ]
    state["entropy_states"] = [
        {
            "schema_version": "1.0.0",
            "target_id": target_id,
            "entropy_value": int(max(0, int(entropy_value))),
            "last_update_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state.setdefault("entropy_event_rows", [])
    state.setdefault("combustion_event_rows", [])
    state.setdefault("combustion_emission_rows", [])
    state.setdefault("combustion_impulse_rows", [])
    state.setdefault("chem_species_pool_rows", [])
    state.setdefault("pollutant_species_pool_rows", [])
    state.setdefault("chem_emission_pool_rows", [])
    state.setdefault("energy_ledger_entries", [])
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    return state


def execute_combustion_tick(
    *,
    repo_root: str,
    state: dict,
    inputs: dict | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context as construction_authority_context,
        law_profile as construction_law_profile,
        policy_context as construction_policy_context,
    )

    law = construction_law_profile(["process.fire_tick"])
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = construction_policy_context(max_compute_units_per_tick=int(max_compute_units_per_tick))
    policy["physics_profile_id"] = "phys.realistic.default"
    policy["combustion_max_evaluations_per_tick"] = 128

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.chem1.fire_tick",
            "process_id": "process.fire_tick",
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
