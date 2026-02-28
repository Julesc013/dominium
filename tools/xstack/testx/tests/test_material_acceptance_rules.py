"""FAST test: port material acceptance rules enforce deterministic refusal."""

from __future__ import annotations

import sys


TEST_ID = "test_material_acceptance_rules"
TEST_TAGS = ["fast", "materials", "interaction"]


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

    state = with_machine(
        base_state(),
        accepted_input_materials=["material.wood_basic"],
    )
    state = with_node_inventory(
        state,
        material_id="material.steel_basic",
        mass=1000,
        batch_id="batch.steel.seed",
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.material.acceptance.001",
            "process_id": "process.port_insert_batch",
            "inputs": {
                "port_id": "port.sawmill.input",
                "batch_id": "batch.steel.seed",
                "material_id": "material.steel_basic",
                "mass": 1000,
                "source_node_id": "node.factory.alpha",
            },
        },
        law_profile=law_profile(["process.port_insert_batch"]),
        authority_context=authority_context(["entitlement.tool.operating"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "material acceptance mismatch should refuse"}
    reason_code = str((dict(result.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.port.material_not_accepted":
        return {"status": "fail", "message": "expected refusal.port.material_not_accepted for disallowed material"}
    return {"status": "pass", "message": "material acceptance refusal verified"}
