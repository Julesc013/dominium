"""FAST test: entropy contribution events are deterministic for registered transforms."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_entropy_increment_deterministic"
TEST_TAGS = ["fast", "physics", "entropy", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        build_power_graph,
        law_profile,
        model_binding_rows,
        policy_context,
    )
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state["power_network_graphs"] = [build_power_graph(edge_count=1, resistance_proxy=8, capacity_rating=220)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=100, motor_demand_p=70, motor_pf_permille=920)
    state.setdefault("elec_flow_channels", [])
    state.setdefault("elec_edge_status_rows", [])
    state.setdefault("elec_node_status_rows", [])
    state.setdefault("elec_network_runtime_state", {"extensions": {}})

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.entropy.elec.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {},
        },
        law_profile=law_profile(["process.elec.network_tick"]),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context(max_compute_units_per_tick=4096, e1_enabled=True), physics_profile_id="phys.realistic.default"),
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)

    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "first elec tick refused: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "second elec tick refused: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})

    event_rows_a = [dict(row) for row in list(first_state.get("entropy_event_rows") or []) if isinstance(row, dict)]
    event_rows_b = [dict(row) for row in list(second_state.get("entropy_event_rows") or []) if isinstance(row, dict)]
    if not event_rows_a:
        return {"status": "fail", "message": "entropy_event_rows should not be empty after elec loss transform"}
    if event_rows_a != event_rows_b:
        return {"status": "fail", "message": "entropy_event_rows drifted across equivalent runs"}

    chain_a = str(first_state.get("entropy_hash_chain", "")).strip().lower()
    chain_b = str(second_state.get("entropy_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
        return {"status": "fail", "message": "entropy_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "entropy_hash_chain drifted across equivalent runs"}

    return {"status": "pass", "message": "entropy increments are deterministic for registered transforms"}
