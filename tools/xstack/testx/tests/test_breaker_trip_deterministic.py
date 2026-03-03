"""FAST test: breaker trips are deterministic across equivalent overload runs."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_breaker_trip_deterministic"
TEST_TAGS = ["fast", "electric", "safety", "breaker", "determinism"]


def _run_tick(state: dict):
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import authority_context, law_profile, policy_context

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.breaker.deterministic.tick",
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

    seed_state = base_state(current_tick=23)
    seed_state["power_network_graphs"] = [build_power_graph(capacity_rating=60, resistance_proxy=6)]
    seed_state["model_bindings"] = model_binding_rows(resistive_demand_p=140, motor_demand_p=100, motor_pf_permille=790)

    first_state = copy.deepcopy(seed_state)
    second_state = copy.deepcopy(seed_state)
    first = _run_tick(first_state)
    second = _run_tick(second_state)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed for breaker deterministic fixture"}

    first_hash = str(first_state.get("trip_event_hash_chain", "")).strip()
    second_hash = str(second_state.get("trip_event_hash_chain", "")).strip()
    if (not first_hash) or first_hash != second_hash:
        return {"status": "fail", "message": "trip_event_hash_chain mismatch between deterministic runs"}

    first_channels = [dict(row) for row in list(first_state.get("elec_flow_channels") or []) if isinstance(row, dict)]
    second_channels = [dict(row) for row in list(second_state.get("elec_flow_channels") or []) if isinstance(row, dict)]
    if canonical_sha256(first_channels) != canonical_sha256(second_channels):
        return {"status": "fail", "message": "post-trip flow channel state diverged across deterministic runs"}
    return {"status": "pass", "message": "breaker trip behavior deterministic"}

