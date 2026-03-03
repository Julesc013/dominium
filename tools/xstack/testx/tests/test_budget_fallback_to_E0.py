"""FAST test: electrical E1 solve deterministically falls back to E0 under budget limits."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_budget_fallback_to_E0"
TEST_TAGS = ["fast", "electric", "budget", "fallback"]


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
    state["power_network_graphs"] = [build_power_graph(capacity_rating=180, resistance_proxy=6)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=90, motor_demand_p=40, motor_pf_permille=900)

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.budget.fallback.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {
                "graph_id": "graph.elec.main",
                "max_edges_per_network": 0,
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed in fallback fixture"}
    runtime_state = dict(state.get("elec_network_runtime_state") or {})
    if str(runtime_state.get("last_budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome after forced E0 fallback"}
    edge_rows = [dict(row) for row in list(state.get("elec_edge_status_rows") or []) if isinstance(row, dict)]
    if not edge_rows:
        return {"status": "fail", "message": "missing elec_edge_status_rows after network tick"}
    tiers = sorted(set(str(row.get("tier", "")).strip() for row in edge_rows))
    if tiers != ["E0"]:
        return {"status": "fail", "message": "edge status rows should be E0 tier under forced fallback"}
    return {"status": "pass", "message": "budget fallback to E0 logged deterministically"}

