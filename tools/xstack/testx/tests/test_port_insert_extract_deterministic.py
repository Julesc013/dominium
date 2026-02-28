"""FAST test: port insert/extract pipeline is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_port_insert_extract_deterministic"
TEST_TAGS = ["fast", "materials", "interaction", "determinism"]


def _run_once() -> dict:
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
    law = law_profile(["process.port_insert_batch", "process.port_extract_batch"])
    authority = authority_context(["entitlement.tool.operating"], privilege_level="operator")
    policy = policy_context()

    insert_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.port.insert.001",
            "process_id": "process.port_insert_batch",
            "inputs": {
                "port_id": "port.sawmill.input",
                "batch_id": "batch.node.seed",
                "material_id": "material.wood_basic",
                "mass": 1000,
                "source_node_id": "node.factory.alpha",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    extract_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.port.extract.001",
            "process_id": "process.port_extract_batch",
            "inputs": {
                "port_id": "port.sawmill.input",
                "mass": 1000,
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    return {"state": state, "insert_result": insert_result, "extract_result": extract_result}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    insert_first = dict(first.get("insert_result") or {})
    insert_second = dict(second.get("insert_result") or {})
    extract_first = dict(first.get("extract_result") or {})
    extract_second = dict(second.get("extract_result") or {})
    if str(insert_first.get("result", "")) != "complete" or str(extract_first.get("result", "")) != "complete":
        return {"status": "fail", "message": "port insert/extract should complete for valid fixture inputs"}
    if str(insert_second.get("result", "")) != "complete" or str(extract_second.get("result", "")) != "complete":
        return {"status": "fail", "message": "port insert/extract second run should complete"}

    if str(insert_first.get("state_hash_anchor", "")) != str(insert_second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "port_insert_batch state hash diverged"}
    if str(extract_first.get("state_hash_anchor", "")) != str(extract_second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "port_extract_batch state hash diverged"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if first_state != second_state:
        return {"status": "fail", "message": "port insert/extract mutated state non-deterministically"}

    batches = list(dict(extract_first).get("output_batches") or [])
    if not batches:
        return {"status": "fail", "message": "port_extract_batch should emit deterministic output batch rows"}
    if not str((dict(batches[0])).get("batch_id", "")).startswith("batch.port.extract."):
        return {"status": "fail", "message": "port_extract_batch deterministic batch id format mismatch"}

    return {"status": "pass", "message": "port insert/extract deterministic behavior verified"}

