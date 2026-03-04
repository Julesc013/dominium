"""FAST test: momentum and electrical transforms emit energy ledger entries."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_energy_ledger_entries_emitted"
TEST_TAGS = ["fast", "physics", "energy", "ledger"]


def run(repo_root: str):
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
    state["power_network_graphs"] = [build_power_graph(edge_count=1, resistance_proxy=10, capacity_rating=220)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=120, motor_demand_p=60, motor_pf_permille=920)
    state.setdefault("elec_flow_channels", [])
    state.setdefault("elec_edge_status_rows", [])
    state.setdefault("elec_node_status_rows", [])
    state.setdefault("elec_network_runtime_state", {"extensions": {}})

    law = elec_law_profile(["process.apply_impulse", "process.elec.network_tick"])
    authority = elec_authority_context()
    policy = elec_policy_context(max_compute_units_per_tick=4096, e1_enabled=True)
    policy["physics_profile_id"] = "phys.realistic.default"

    impulse = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.patch_a2.energy_ledger.impulse",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.patch_a2.energy.001",
                "target_assembly_id": "body.vehicle.mob.free.alpha",
                "impulse_vector": {"x": 900, "y": 0, "z": 0},
                "torque_impulse": 0,
                "external_impulse_logged": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(impulse.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "apply_impulse failed: {}".format(impulse)}

    elec_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.patch_a2.energy_ledger.elec_tick",
            "process_id": "process.elec.network_tick",
            "inputs": {},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(elec_tick.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "elec.network_tick failed: {}".format(elec_tick)}

    ledger_rows = [dict(row) for row in list(state.get("energy_ledger_entries") or []) if isinstance(row, dict)]
    if not ledger_rows:
        return {"status": "fail", "message": "expected non-empty energy_ledger_entries after impulse + elec tick"}
    transform_ids = set(
        str(row.get("transformation_id", "")).strip()
        for row in ledger_rows
        if str(row.get("transformation_id", "")).strip()
    )
    if "transform.impulse_to_kinetic" not in transform_ids:
        return {"status": "fail", "message": "missing transform.impulse_to_kinetic ledger entry"}
    if "transform.electrical_to_thermal" not in transform_ids:
        return {"status": "fail", "message": "missing transform.electrical_to_thermal ledger entry"}
    return {"status": "pass", "message": "energy ledger entries emitted for impulse and electrical dissipation"}
