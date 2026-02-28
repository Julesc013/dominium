"""FAST test: ACT-4 machine/port refusal codes are emitted as expected."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_refusal_codes_correct"
TEST_TAGS = ["fast", "materials", "interaction", "refusal"]


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

    policy = policy_context()
    authority = authority_context(["entitlement.tool.operating"], privilege_level="operator")

    # refusal.port.full
    state_full = with_machine(base_state(), input_capacity_mass=1000)
    state_full = with_node_inventory(state_full, mass=2000, batch_id="batch.node.seed")
    full_result = execute_intent(
        state=state_full,
        intent={
            "intent_id": "intent.test.refusal.full.001",
            "process_id": "process.port_insert_batch",
            "inputs": {
                "port_id": "port.sawmill.input",
                "batch_id": "batch.node.seed",
                "material_id": "material.wood_basic",
                "mass": 1500,
                "source_node_id": "node.factory.alpha",
            },
        },
        law_profile=law_profile(["process.port_insert_batch"]),
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    full_reason_code = str((dict(full_result.get("refusal") or {})).get("reason_code", "")).strip()
    if full_reason_code != "refusal.port.full":
        return {"status": "fail", "message": "expected refusal.port.full for over-capacity insert"}

    # refusal.port.empty
    state_empty = with_machine(base_state())
    empty_result = execute_intent(
        state=state_empty,
        intent={
            "intent_id": "intent.test.refusal.empty.001",
            "process_id": "process.port_extract_batch",
            "inputs": {
                "port_id": "port.sawmill.input",
                "mass": 100,
            },
        },
        law_profile=law_profile(["process.port_extract_batch"]),
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    empty_reason_code = str((dict(empty_result.get("refusal") or {})).get("reason_code", "")).strip()
    if empty_reason_code != "refusal.port.empty":
        return {"status": "fail", "message": "expected refusal.port.empty for extracting from empty port"}

    # refusal.logistics.insufficient_stock
    state_stock = with_machine(base_state())
    state_stock = with_node_inventory(state_stock, mass=100, batch_id="batch.node.seed")
    stock_result = execute_intent(
        state=state_stock,
        intent={
            "intent_id": "intent.test.refusal.stock.001",
            "process_id": "process.machine_pull_from_node",
            "inputs": {
                "machine_id": "machine.sawmill.alpha",
                "node_id": "node.factory.alpha",
                "port_id": "port.sawmill.input",
                "batch_id": "batch.node.seed",
                "material_id": "material.wood_basic",
                "mass": 500,
            },
        },
        law_profile=law_profile(["process.machine_pull_from_node"]),
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    stock_reason_code = str((dict(stock_result.get("refusal") or {})).get("reason_code", "")).strip()
    if stock_reason_code != "refusal.logistics.insufficient_stock":
        return {"status": "fail", "message": "expected refusal.logistics.insufficient_stock for pull over available stock"}

    # refusal.port.forbidden_by_law (gate refusal)
    state_gate = with_machine(base_state())
    denied_law = law_profile([])
    denied_result = execute_intent(
        state=copy.deepcopy(state_gate),
        intent={
            "intent_id": "intent.test.refusal.gate.001",
            "process_id": "process.port_connect",
            "inputs": {
                "from_port_id": "port.sawmill.input",
                "to_port_id": "port.sawmill.output",
            },
        },
        law_profile=denied_law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    denied_reason_code = str((dict(denied_result.get("refusal") or {})).get("reason_code", "")).strip()
    if denied_reason_code != "refusal.port.forbidden_by_law":
        return {"status": "fail", "message": "expected refusal.port.forbidden_by_law for forbidden process"}

    return {"status": "pass", "message": "ACT-4 refusal codes verified"}
