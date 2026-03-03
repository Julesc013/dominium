"""FAST test: electrical LOTO prevents breaker reclose until lock removal."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_loto_prevents_reclose"
TEST_TAGS = ["fast", "electric", "loto", "safety"]


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

    state = base_state(current_tick=29)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=50, resistance_proxy=5)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=140, motor_demand_p=110, motor_pf_permille=800)
    allowed = [
        "process.elec.network_tick",
        "process.elec.flip_breaker",
        "process.elec_apply_loto",
    ]
    law = copy.deepcopy(law_profile(allowed))
    authority = copy.deepcopy(authority_context())
    policy = copy.deepcopy(policy_context(e1_enabled=True))

    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.loto.pre.trip",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed in LOTO fixture setup"}
    channel_rows = [dict(row) for row in list(state.get("elec_flow_channels") or []) if isinstance(row, dict)]
    if not channel_rows:
        return {"status": "fail", "message": "missing elec flow channel after network tick"}
    channel_id = str(channel_rows[0].get("channel_id", "")).strip()
    if not channel_id:
        return {"status": "fail", "message": "missing channel_id for LOTO fixture"}

    apply_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.loto.apply",
            "process_id": "process.elec_apply_loto",
            "inputs": {"target_id": channel_id, "lock_tag": "loto.elec.test"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(apply_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to apply LOTO before reclose check"}

    reclose_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.loto.reclose",
            "process_id": "process.elec.flip_breaker",
            "inputs": {"channel_id": channel_id, "breaker_state": "closed"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(reclose_result.get("result", "")) != "refused":
        return {"status": "fail", "message": "reclose must be refused while LOTO is active"}
    refusal = dict(reclose_result.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.maintenance.lockout_active":
        return {"status": "fail", "message": "unexpected refusal code for active LOTO reclose attempt"}
    return {"status": "pass", "message": "LOTO deterministically prevents breaker reclose"}
