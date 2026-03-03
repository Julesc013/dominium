"""FAST test: electrical fault detection remains deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_fault_detection_deterministic"
TEST_TAGS = ["fast", "electric", "fault", "determinism"]


def _run_network_tick(repo_root: str, state: dict):
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import authority_context, law_profile, policy_context

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.fault.deterministic.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.elec_testlib import base_state, build_power_graph, model_binding_rows

    seed_state = base_state(current_tick=19)
    seed_state["power_network_graphs"] = [build_power_graph(capacity_rating=55, resistance_proxy=9)]
    seed_state["model_bindings"] = model_binding_rows(resistive_demand_p=150, motor_demand_p=90, motor_pf_permille=780)

    first_state = copy.deepcopy(seed_state)
    second_state = copy.deepcopy(seed_state)
    first = _run_network_tick(repo_root, first_state)
    second = _run_network_tick(repo_root, second_state)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed for deterministic fault fixture"}

    first_fault_rows = [dict(row) for row in list(first_state.get("elec_fault_states") or []) if isinstance(row, dict)]
    second_fault_rows = [dict(row) for row in list(second_state.get("elec_fault_states") or []) if isinstance(row, dict)]
    if not first_fault_rows:
        return {"status": "fail", "message": "fixture expected at least one detected electrical fault"}
    first_hash = canonical_sha256(first_fault_rows)
    second_hash = canonical_sha256(second_fault_rows)
    if first_hash != second_hash:
        return {"status": "fail", "message": "fault state rows diverged for equivalent deterministic inputs"}

    first_chain = str(first_state.get("fault_state_hash_chain", "")).strip()
    second_chain = str(second_state.get("fault_state_hash_chain", "")).strip()
    if first_chain != second_chain:
        return {"status": "fail", "message": "fault_state_hash_chain diverged between deterministic runs"}
    return {"status": "pass", "message": "electrical fault detection deterministic"}

