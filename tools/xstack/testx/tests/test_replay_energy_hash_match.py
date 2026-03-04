"""STRICT test: PHYS-3 energy ledger and boundary flux hash chains are replay-stable."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_replay_energy_hash_match"
TEST_TAGS = ["strict", "physics", "energy", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context as elec_authority_context,
        build_power_graph,
        law_profile as elec_law_profile,
        model_binding_rows,
        policy_context as elec_policy_context,
    )
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state["power_network_graphs"] = [build_power_graph(edge_count=1, resistance_proxy=8, capacity_rating=220)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=100, motor_demand_p=70, motor_pf_permille=920)
    state.setdefault("elec_flow_channels", [])
    state.setdefault("elec_edge_status_rows", [])
    state.setdefault("elec_node_status_rows", [])
    state.setdefault("elec_network_runtime_state", {"extensions": {}})

    law = elec_law_profile(["process.apply_impulse", "process.elec.network_tick"])
    authority = elec_authority_context()
    policy = elec_policy_context(max_compute_units_per_tick=4096, e1_enabled=True)
    policy["physics_profile_id"] = "phys.realistic.default"

    impulse_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.energy.replay.impulse",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.energy.replay",
                "target_assembly_id": "body.vehicle.mob.free.alpha",
                "impulse_vector": {"x": 900, "y": -200, "z": 0},
                "torque_impulse": 1,
                "external_impulse_logged": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(impulse_result.get("result", "")) != "complete":
        return {"result": dict(impulse_result), "state": dict(state)}

    elec_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.energy.replay.elec",
            "process_id": "process.elec.network_tick",
            "inputs": {},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": dict(elec_result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline energy replay fixture failed: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay energy fixture failed: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})

    ledger_hash_a = str(first_state.get("energy_ledger_hash_chain", "")).strip().lower()
    ledger_hash_b = str(second_state.get("energy_ledger_hash_chain", "")).strip().lower()
    flux_hash_a = str(first_state.get("boundary_flux_hash_chain", "")).strip().lower()
    flux_hash_b = str(second_state.get("boundary_flux_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(ledger_hash_a)) or (not _HASH64.fullmatch(ledger_hash_b)):
        return {"status": "fail", "message": "energy_ledger_hash_chain missing/invalid"}
    if (not _HASH64.fullmatch(flux_hash_a)) or (not _HASH64.fullmatch(flux_hash_b)):
        return {"status": "fail", "message": "boundary_flux_hash_chain missing/invalid"}
    if ledger_hash_a != ledger_hash_b:
        return {"status": "fail", "message": "energy_ledger_hash_chain drifted across equivalent runs"}
    if flux_hash_a != flux_hash_b:
        return {"status": "fail", "message": "boundary_flux_hash_chain drifted across equivalent runs"}

    if list(first_state.get("energy_ledger_entries") or []) != list(second_state.get("energy_ledger_entries") or []):
        return {"status": "fail", "message": "energy ledger entries drifted across equivalent runs"}
    if list(first_state.get("boundary_flux_events") or []) != list(second_state.get("boundary_flux_events") or []):
        return {"status": "fail", "message": "boundary flux events drifted across equivalent runs"}
    return {"status": "pass", "message": "energy replay hash chains are deterministic"}
