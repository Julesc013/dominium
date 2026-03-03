"""FAST test: ELEC-5 cascade loop remains bounded by configured iteration cap."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cascade_bounded"
TEST_TAGS = ["fast", "electric", "elec5", "cascade", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        build_power_graph,
        law_profile,
        model_binding_rows,
        policy_context,
    )

    state = base_state(current_tick=11)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=48, resistance_proxy=11)]
    state["model_bindings"] = model_binding_rows(
        resistive_demand_p=170,
        motor_demand_p=130,
        motor_pf_permille=760,
    )
    max_iterations = 2
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec5.cascade.bounded.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {
                "graph_id": "graph.elec.main",
                "cascade_max_iterations": max_iterations,
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick refused in cascade bound fixture"}
    observed_count = int(max(0, int(result.get("cascade_iteration_count", 0) or 0)))
    observed_cap = int(max(0, int(result.get("cascade_max_iterations", 0) or 0)))
    if observed_cap != int(max_iterations):
        return {"status": "fail", "message": "cascade_max_iterations was not preserved in result metadata"}
    if observed_count > observed_cap:
        return {"status": "fail", "message": "cascade iteration count exceeded configured cap"}
    runtime_state = dict(state.get("elec_network_runtime_state") or {})
    runtime_ext = dict(runtime_state.get("extensions") or {})
    if int(max(0, int(runtime_ext.get("cascade_max_iterations", 0) or 0))) != int(max_iterations):
        return {"status": "fail", "message": "runtime cascade cap metadata missing or incorrect"}
    return {"status": "pass", "message": "ELEC-5 cascade bounded by deterministic cap"}

