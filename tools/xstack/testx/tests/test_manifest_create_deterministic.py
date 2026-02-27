"""FAST test: process.manifest_create is deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.manifest_create_deterministic"
TEST_TAGS = ["fast", "materials", "logistics", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.logistics_testlib import (
        authority_context,
        base_state,
        law_profile,
        logistics_graph,
        policy_context,
        with_inventory,
    )

    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id="material.steel_basic",
        mass=2_000,
        batch_id="batch.seed",
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.manifest.create.001",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 500,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=law_profile(["process.manifest_create"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(graph_rows=[logistics_graph()]),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_create must complete for valid stock/route inputs"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "manifest_create state hash anchor diverged"}
    if str(first_result.get("ledger_hash", "")) != str(second_result.get("ledger_hash", "")):
        return {"status": "fail", "message": "manifest_create ledger hash diverged"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if first_state != second_state:
        return {"status": "fail", "message": "manifest_create mutated state non-deterministically"}

    manifests = list(first_state.get("logistics_manifests") or [])
    commitments = list(first_state.get("shipment_commitments") or [])
    if len(manifests) != 1 or len(commitments) != 1:
        return {"status": "fail", "message": "manifest_create should emit one manifest and one shipment commitment"}
    manifest_id = str(manifests[0].get("manifest_id", ""))
    commitment_id = str(commitments[0].get("commitment_id", ""))
    if not manifest_id.startswith("manifest.") or not commitment_id.startswith("commitment.shipment."):
        return {"status": "fail", "message": "manifest/commitment deterministic id format mismatch"}
    return {"status": "pass", "message": "manifest_create deterministic behavior passed"}
