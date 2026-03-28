"""FAST test: ELEC-5 proof hash-chain fields remain stable for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_proof_hash_chain_stable"
TEST_TAGS = ["fast", "electric", "elec5", "proof", "determinism"]


def _run_once(repo_root: str) -> dict:
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

    state = base_state(current_tick=33)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=64, resistance_proxy=9)]
    state["model_bindings"] = model_binding_rows(
        resistive_demand_p=150,
        motor_demand_p=100,
        motor_pf_permille=780,
    )
    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec5.proof.hash.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main", "max_network_solves_per_tick": 1},
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"result": "refused"}
    mobility_surface = dict(state.get("elec_proof_surface") or {})
    bundle = build_control_proof_bundle_from_markers(
        tick_start=33,
        tick_end=33,
        decision_markers=[],
        mobility_proof_surface=mobility_surface,
    )
    return {
        "result": "complete",
        "bundle": bundle,
    }


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick refused in proof chain stability fixture"}
    bundle_one = dict(first.get("bundle") or {})
    bundle_two = dict(second.get("bundle") or {})
    keys = (
        "power_flow_hash_chain",
        "fault_state_hash_chain",
        "protection_state_hash_chain",
        "degradation_event_hash_chain",
    )
    for key in keys:
        if str(bundle_one.get(key, "")).strip().lower() != str(bundle_two.get(key, "")).strip().lower():
            return {"status": "fail", "message": "proof hash chain drift for key {}".format(key)}
        if len(str(bundle_one.get(key, "")).strip()) != 64:
            return {"status": "fail", "message": "missing 64-char proof hash chain for key {}".format(key)}
    return {"status": "pass", "message": "ELEC-5 proof hash-chain values are stable"}

