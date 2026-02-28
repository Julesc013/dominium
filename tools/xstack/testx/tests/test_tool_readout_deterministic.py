"""STRICT test: tool readout process emits deterministic diegetic channels."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_tool_readout_deterministic"
TEST_TAGS = ["strict", "interaction", "tool", "diegetic"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.tool.readout",
        "allowed_processes": ["process.tool_readout_tick"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.tool_readout_tick": "entitlement.tool.use",
        },
        "process_privilege_requirements": {
            "process.tool_readout_tick": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _tool_state() -> dict:
    return {
        "tool_assemblies": [
            {
                "schema_version": "1.0.0",
                "tool_id": "tool.instance.wrench.alpha",
                "tool_type_id": "tool.wrench.basic",
                "tool_tags": ["tool_tag.fastening", "tool_tag.operating"],
                "effect_model_id": "effect.basic_fastening",
                "equipped_by_agent_id": "agent.alpha",
                "durability_state": {"health_permille": 923},
                "extensions": {},
            }
        ],
        "tool_bindings": [
            {
                "schema_version": "1.0.0",
                "bind_id": "tool.bind.alpha",
                "subject_id": "agent.alpha",
                "tool_id": "tool.instance.wrench.alpha",
                "created_tick": 0,
                "active": True,
                "extensions": {},
            }
        ],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state_one = base_state()
    state_one.update(_tool_state())
    state_two = copy.deepcopy(state_one)
    law = _law_profile()
    auth = authority_context(entitlements=["entitlement.tool.use"], privilege_level="observer")
    policy = policy_context()
    intent = {
        "intent_id": "intent.tool.readout.001",
        "process_id": "process.tool_readout_tick",
        "inputs": {
            "subject_id": "agent.alpha",
            "perceived_now": {
                "selected_dimension_mm": 1234,
            },
        },
    }

    first = execute_intent(
        state=state_one,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state_two,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.tool_readout_tick refused unexpectedly"}
    if dict(first.get("tool_readouts") or {}) != dict(second.get("tool_readouts") or {}):
        return {"status": "fail", "message": "tool readout payload differs across equivalent runs"}
    measurement = dict((dict(first.get("tool_readouts") or {})).get("ch.diegetic.tool.measurement") or {})
    if int(measurement.get("measurement_mm", -1)) != 1230:
        return {"status": "fail", "message": "measurement quantization not deterministic for medium precision"}
    instrument_rows = list(state_one.get("instrument_assemblies") or [])
    measurement_row = {}
    for row in instrument_rows:
        if str((dict(row)).get("assembly_id", "")).strip() == "instrument.tool.measurement":
            measurement_row = dict(row)
            break
    if not measurement_row:
        return {"status": "fail", "message": "instrument.tool.measurement row was not written"}
    outputs = dict(measurement_row.get("outputs") or {})
    if "ch.diegetic.tool.measurement" not in outputs:
        return {"status": "fail", "message": "measurement channel output missing from instrument row"}
    return {"status": "pass", "message": "tool readout determinism verified"}

