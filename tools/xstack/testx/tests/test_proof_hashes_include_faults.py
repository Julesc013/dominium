"""FAST test: control proof bundles include electrical fault/trip hash chains."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_proof_hashes_include_faults"
TEST_TAGS = ["fast", "electric", "proof", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.proof.control_proof_bundle import build_control_proof_bundle_from_markers
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        build_power_graph,
        law_profile,
        model_binding_rows,
        policy_context,
    )

    state = base_state(current_tick=31)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=58, resistance_proxy=9)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=150, motor_demand_p=95, motor_pf_permille=770)

    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.proof.hash.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed in proof hash fixture"}

    mobility_surface = dict(state.get("elec_proof_surface") or {})
    if not mobility_surface:
        return {"status": "fail", "message": "missing elec_proof_surface after network tick"}
    bundle = build_control_proof_bundle_from_markers(
        tick_start=31,
        tick_end=31,
        decision_markers=[],
        mobility_proof_surface=mobility_surface,
    )
    expected_fault_hash = str(state.get("fault_state_hash_chain", "")).strip().lower()
    expected_trip_hash = str(state.get("trip_event_hash_chain", "")).strip().lower()
    actual_fault_hash = str(bundle.get("fault_state_hash_chain", "")).strip().lower()
    actual_trip_hash = str(bundle.get("trip_event_hash_chain", "")).strip().lower()
    if not expected_fault_hash or not expected_trip_hash:
        return {"status": "fail", "message": "fixture failed to produce electrical fault/trip hash chains"}
    if actual_fault_hash != expected_fault_hash:
        return {"status": "fail", "message": "proof bundle fault_state_hash_chain does not match runtime electrical chain"}
    if actual_trip_hash != expected_trip_hash:
        return {"status": "fail", "message": "proof bundle trip_event_hash_chain does not match runtime electrical chain"}
    return {"status": "pass", "message": "control proof bundles include electrical fault/trip hash chains"}

