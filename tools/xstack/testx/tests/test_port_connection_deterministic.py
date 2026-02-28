"""FAST test: port_connect is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_port_connection_deterministic"
TEST_TAGS = ["fast", "materials", "interaction", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.machine_testlib import authority_context, base_state, law_profile, policy_context, with_machine

    state = with_machine(base_state())
    state["machine_ports"].append(
        {
            "schema_version": "1.0.0",
            "port_id": "port.sawmill.energy",
            "machine_id": "machine.sawmill.alpha",
            "parent_structure_id": None,
            "port_type_id": "port.energy_in",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": None,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": "visibility.default",
            "extensions": {},
        }
    )
    state_before = copy.deepcopy(state)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.port.connect.001",
            "process_id": "process.port_connect",
            "inputs": {
                "from_port_id": "port.sawmill.output",
                "to_port_id": "port.sawmill.input",
                "connection_kind": "direct",
            },
        },
        law_profile=law_profile(["process.port_connect"]),
        authority_context=authority_context(["entitlement.tool.operating"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(),
    )
    return {"state_before": state_before, "state_after": state, "result": result}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.port_connect should complete for valid endpoints"}
    if str(first_result.get("connection_id", "")) != str(second_result.get("connection_id", "")):
        return {"status": "fail", "message": "connection_id should be deterministic for identical inputs"}
    if dict(first.get("state_after") or {}) != dict(second.get("state_after") or {}):
        return {"status": "fail", "message": "port_connect mutated state non-deterministically"}
    return {"status": "pass", "message": "port connection determinism verified"}

