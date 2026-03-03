"""FAST test: overloaded electrical edges trip breaker through SAFETY pattern path."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_breaker_trip_on_overload"
TEST_TAGS = ["fast", "electric", "safety", "breaker"]


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

    state = base_state(current_tick=7)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=60, resistance_proxy=8)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=140, motor_demand_p=80, motor_pf_permille=800)

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.breaker.overload.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.network_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(e1_enabled=True)),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed for overload breaker fixture"}

    channel_rows = [dict(row) for row in list(state.get("elec_flow_channels") or []) if isinstance(row, dict)]
    if not channel_rows:
        return {"status": "fail", "message": "expected elec_flow_channels after network tick"}
    channel = dict(channel_rows[0])
    if int(max(0, int(channel.get("capacity_per_tick", 0)))) != 0:
        return {"status": "fail", "message": "overload breaker should disconnect channel capacity_per_tick"}
    ext = dict(channel.get("extensions") or {})
    if str(ext.get("breaker_state", "")).strip() != "tripped":
        return {"status": "fail", "message": "breaker_state should be tripped after overload safety action"}
    if not bool(ext.get("safety_disconnected", False)):
        return {"status": "fail", "message": "safety_disconnected flag should be true after breaker trip"}
    return {"status": "pass", "message": "breaker trip applied via safety path on overload"}

