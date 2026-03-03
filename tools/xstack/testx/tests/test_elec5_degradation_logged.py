"""FAST test: ELEC-5 degradation path emits deterministic degradation + decision logs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_degradation_logged"
TEST_TAGS = ["fast", "electric", "elec5", "degradation", "logging"]


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

    state = base_state(current_tick=21)
    state["power_network_graphs"] = [
        build_power_graph(graph_id="graph.elec.main.1", capacity_rating=80, resistance_proxy=10),
        build_power_graph(graph_id="graph.elec.main.2", capacity_rating=75, resistance_proxy=10),
        build_power_graph(graph_id="graph.elec.main.3", capacity_rating=70, resistance_proxy=10),
    ]
    state["model_bindings"] = model_binding_rows(
        resistive_demand_p=120,
        motor_demand_p=95,
        motor_pf_permille=790,
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec5.degradation.logged.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {
                "max_network_solves_per_tick": 1,
                "pending_low_priority_connections": [
                    {"request_id": "req.low.001", "priority": "low", "created_tick": 19},
                    {"request_id": "req.low.002", "priority": "low", "created_tick": 20},
                ],
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick refused in degradation logging fixture"}
    degradation_rows = [dict(row) for row in list(state.get("elec_degradation_events") or []) if isinstance(row, dict)]
    if not degradation_rows:
        return {"status": "fail", "message": "expected elec_degradation_events rows under constrained budget"}
    chain = str(state.get("degradation_event_hash_chain", "")).strip()
    if len(chain) != 64:
        return {"status": "fail", "message": "missing degradation_event_hash_chain"}
    decision_rows = [dict(row) for row in list(state.get("control_decision_log") or []) if isinstance(row, dict)]
    if not any(str(row.get("process_id", "")).strip() == "process.elec_budget_degrade" for row in decision_rows):
        return {"status": "fail", "message": "expected process.elec_budget_degrade decision-log entries"}
    return {"status": "pass", "message": "ELEC-5 degradation decisions/events are logged deterministically"}

