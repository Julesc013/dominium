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


def seed_process_run_state(
    *,
    reaction_id: str = "reaction.smelting_stub",
    equipment_id: str = "equipment.chem.reactor.alpha",
    ore_mass: int = 900,
    reductant_mass: int = 420,
    contamination_tags: list[str] | None = None,
    entropy_value: int = 0,
) -> dict:
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state
    from materials import create_material_batch
    from chem import build_batch_quality_row

    contamination = sorted(set(str(tag).strip() for tag in list(contamination_tags or ["contaminant.trace_sulfur"]) if str(tag).strip()))
    state = seed_free_state(initial_velocity_x=0)

    ore_batch = create_material_batch(
        material_id="material.ore_stub",
        quantity_mass_raw=int(max(0, int(ore_mass))),
        origin_process_id="process.seed_fixture",
        origin_tick=0,
        parent_batch_ids=[],
        quality_distribution={},
    )
    reductant_batch = create_material_batch(
        material_id="material.reductant_stub",
        quantity_mass_raw=int(max(0, int(reductant_mass))),
        origin_process_id="process.seed_fixture",
        origin_tick=0,
        parent_batch_ids=[],
        quality_distribution={},
    )
    ore_batch_id = str(ore_batch.get("batch_id", "")).strip()
    reductant_batch_id = str(reductant_batch.get("batch_id", "")).strip()

    ore_quality = build_batch_quality_row(
        batch_id=ore_batch_id,
        quality_grade="grade.B",
        defect_flags=[],
        contamination_tags=list(contamination),
        yield_factor=1000,
        extensions={"source": "test.seed"},
    )
    reductant_quality = build_batch_quality_row(
        batch_id=reductant_batch_id,
        quality_grade="grade.B",
        defect_flags=[],
        contamination_tags=[],
        yield_factor=1000,
        extensions={"source": "test.seed"},
    )

    state["material_batches"] = [dict(ore_batch), dict(reductant_batch)]
    state["batch_quality_rows"] = [dict(ore_quality), dict(reductant_quality)]
    state["chem_process_run_state_rows"] = []
    state["process_run_state_rows"] = []
    state["chem_process_run_events"] = []
    state["chem_yield_model_rows"] = []
    state["chem_process_emission_rows"] = []
    state["chem_species_pool_rows"] = []
    state["pollutant_species_pool_rows"] = []
    state.setdefault("energy_ledger_entries", [])
    state.setdefault("entropy_event_rows", [])
    state["entropy_states"] = [
        {
            "schema_version": "1.0.0",
            "target_id": str(equipment_id),
            "entropy_value": int(max(0, int(entropy_value))),
            "last_update_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    state["chem_test_fixture"] = {
        "reaction_id": str(reaction_id),
        "equipment_id": str(equipment_id),
        "input_batch_ids": [str(ore_batch_id), str(reductant_batch_id)],
        "run_id": "run.chem.test.alpha",
    }
    return state


def execute_process_run_intent(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
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

    allowed_processes = [
        "process.process_run_start",
        "process.process_run_tick",
        "process.process_run_end",
    ]
    law = construction_law_profile(allowed_processes)
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect", "entitlement.tool.operating"],
        privilege_level="operator",
    )
    policy = construction_policy_context(max_compute_units_per_tick=int(max_compute_units_per_tick))
    policy["physics_profile_id"] = "phys.realistic.default"
    policy["chem_max_process_run_evaluations_per_tick"] = 128

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.chem2.{}".format(str(process_id).replace(".", "_")),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def execute_process_run_lifecycle(
    *,
    repo_root: str,
    state: dict,
    run_id: str | None = None,
    catalyst_present: bool = False,
    spec_score_permille: int = 900,
    temperature: int = 640,
    pressure_head: int = 180,
) -> dict:
    fixture = dict(state.get("chem_test_fixture") or {})
    start_inputs = {
        "run_id": str(run_id or fixture.get("run_id", "run.chem.test.alpha")),
        "reaction_id": str(fixture.get("reaction_id", "reaction.smelting_stub")),
        "equipment_id": str(fixture.get("equipment_id", "equipment.chem.reactor.alpha")),
        "input_batch_ids": list(fixture.get("input_batch_ids") or []),
    }
    start = execute_process_run_intent(
        repo_root=repo_root,
        state=state,
        process_id="process.process_run_start",
        inputs=start_inputs,
    )
    tick = execute_process_run_intent(
        repo_root=repo_root,
        state=state,
        process_id="process.process_run_tick",
        inputs={
            "run_id": str(start_inputs["run_id"]),
            "temperature": int(temperature),
            "pressure_head": int(max(0, int(pressure_head))),
            "catalyst_present": bool(catalyst_present),
            "spec_score_permille": int(max(0, min(1000, int(spec_score_permille)))),
        },
    )
    end = execute_process_run_intent(
        repo_root=repo_root,
        state=state,
        process_id="process.process_run_end",
        inputs={
            "run_id": str(start_inputs["run_id"]),
            "status": "complete",
        },
    )
    return {
        "run_id": str(start_inputs["run_id"]),
        "start": dict(start),
        "tick": dict(tick),
        "end": dict(end),
    }
