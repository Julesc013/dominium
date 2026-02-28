"""FAST test: machine node pull/operate/push keeps node stock balanced."""

from __future__ import annotations

import sys


TEST_ID = "test_node_integration_balanced"
TEST_TAGS = ["fast", "materials", "interaction", "logistics"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.machine_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_machine,
        with_node_inventory,
    )

    state = with_machine(base_state())
    state = with_node_inventory(state, mass=2000, batch_id="batch.node.seed")
    allowed = [
        "process.machine_pull_from_node",
        "process.machine_operate",
        "process.machine_push_to_node",
    ]
    law = law_profile(allowed)
    authority = authority_context(["entitlement.tool.operating"], privilege_level="operator")
    policy = policy_context()

    pull_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.machine.pull.001",
            "process_id": "process.machine_pull_from_node",
            "inputs": {
                "machine_id": "machine.sawmill.alpha",
                "port_id": "port.sawmill.input",
                "node_id": "node.factory.alpha",
                "batch_id": "batch.node.seed",
                "material_id": "material.wood_basic",
                "mass": 1000,
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    operate_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.machine.operate.002",
            "process_id": "process.machine_operate",
            "inputs": {
                "machine_id": "machine.sawmill.alpha",
                "operation_id": "op.saw_planks",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    push_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.machine.push.003",
            "process_id": "process.machine_push_to_node",
            "inputs": {
                "machine_id": "machine.sawmill.alpha",
                "port_id": "port.sawmill.output",
                "node_id": "node.factory.alpha",
                "mass": 1000,
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(pull_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "machine_pull_from_node refused unexpectedly"}
    if str(operate_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "machine_operate refused unexpectedly"}
    if str(push_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "machine_push_to_node refused unexpectedly"}

    inventories = [dict(row) for row in list(state.get("logistics_node_inventories") or []) if isinstance(row, dict)]
    if not inventories:
        return {"status": "fail", "message": "node inventory missing after machine node integration flow"}
    node_row = dict(inventories[0])
    wood_mass = int((dict(node_row.get("material_stocks") or {})).get("material.wood_basic", 0) or 0)
    if wood_mass != 2000:
        return {
            "status": "fail",
            "message": "node integration mass balance drifted (expected 2000, got {})".format(wood_mass),
        }
    return {"status": "pass", "message": "machine node pull/push integration remains balanced"}

