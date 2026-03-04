"""FAST test: ELEC-4 diegetic electrical tool readouts stay redacted in diegetic scope."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_diegetic_tool_readouts_redacted"
TEST_TAGS = ["fast", "electric", "diegetic", "epistemic"]


def _instrument_reading(state: dict, assembly_id: str) -> dict:
    for row in list(state.get("instrument_assemblies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")).strip() != str(assembly_id).strip():
            continue
        return dict(row.get("reading") or {})
    return {}


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

    state = base_state(current_tick=12)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=280, resistance_proxy=7)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=120, motor_demand_p=80, motor_pf_permille=840)

    law = copy.deepcopy(law_profile(["process.elec.network_tick", "process.instrument_tick"]))
    law["epistemic_limits"] = dict(law.get("epistemic_limits") or {})
    law["epistemic_limits"]["allow_hidden_state_access"] = False
    law["epistemic_policy_id"] = "ep.policy.player_diegetic"

    authority = copy.deepcopy(authority_context())
    scope = dict(authority.get("epistemic_scope") or {})
    scope["visibility_level"] = "diegetic"
    authority["epistemic_scope"] = scope
    authority["privilege_level"] = "observer"

    policy = copy.deepcopy(policy_context(e1_enabled=True))
    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.readout.tick.001",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.elec.network_tick failed in diegetic readout fixture"}

    instrument_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.readout.instrument.001",
            "process_id": "process.instrument_tick",
            "inputs": {},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(instrument_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.instrument_tick failed in diegetic readout fixture"}

    voltage = _instrument_reading(state, "instrument.elec.voltage_meter")
    current_proxy = _instrument_reading(state, "instrument.elec.current_proxy_meter")
    pf = _instrument_reading(state, "instrument.elec.pf_meter")
    energized = _instrument_reading(state, "instrument.elec.energized_indicator")
    if not voltage or not current_proxy or not pf or not energized:
        return {"status": "fail", "message": "expected electrical diegetic instrument rows were not written"}

    if str(voltage.get("status", "")).strip() != "COARSE":
        return {"status": "fail", "message": "diegetic voltage readout must be coarse"}
    if str(current_proxy.get("status", "")).strip() != "COARSE":
        return {"status": "fail", "message": "diegetic current proxy readout must be coarse"}
    if str(pf.get("status", "")).strip() != "COARSE":
        return {"status": "fail", "message": "diegetic PF readout must be coarse"}
    if "voltage_proxy" in voltage or "current_proxy" in current_proxy or "pf_permille" in pf:
        return {"status": "fail", "message": "diegetic electrical readouts leaked precise values"}
    if "voltage_band" not in voltage or "current_band" not in current_proxy or "pf_band" not in pf:
        return {"status": "fail", "message": "diegetic electrical readouts must expose quantized bands"}
    if str(energized.get("status", "")).strip() != "COARSE":
        return {"status": "fail", "message": "diegetic energized indicator must be coarse"}
    if "active_power_p" in energized or "apparent_power_s" in energized:
        return {"status": "fail", "message": "diegetic energized indicator leaked precise power values"}

    return {"status": "pass", "message": "diegetic electrical tool readouts remain quantized and redacted"}

