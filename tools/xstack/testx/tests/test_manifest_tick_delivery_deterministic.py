"""FAST test: process.manifest_tick delivery is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.manifest_tick_delivery_deterministic"
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
    law = law_profile(["process.manifest_create", "process.manifest_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context(graph_rows=[logistics_graph(delay_ticks=0, loss_fraction=0)])

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.manifest.create.delivery",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 750,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"created": created, "ticked": {}, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.manifest.tick.delivery",
            "process_id": "process.manifest_tick",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "max_manifests_per_tick": 16,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"created": created, "ticked": ticked, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_tick = dict(first.get("ticked") or {})
    second_tick = dict(second.get("ticked") or {})
    if str(first_tick.get("result", "")) != "complete" or str(second_tick.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_tick must complete for valid manifest delivery setup"}
    if str(first_tick.get("state_hash_anchor", "")) != str(second_tick.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "manifest_tick delivery state hash anchor diverged"}
    if dict(first.get("state") or {}) != dict(second.get("state") or {}):
        return {"status": "fail", "message": "manifest_tick delivery mutated state non-deterministically"}

    state = dict(first.get("state") or {})
    manifests = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if len(manifests) != 1:
        return {"status": "fail", "message": "expected one manifest after deterministic create+tick flow"}
    if str(manifests[0].get("status", "")) != "delivered":
        return {"status": "fail", "message": "manifest should be delivered for zero-delay zero-loss route"}

    inventories = sorted(
        (dict(row) for row in list(state.get("logistics_node_inventories") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("node_id", "")),
    )
    source_mass = 0
    destination_mass = 0
    for row in inventories:
        stocks = dict(row.get("material_stocks") or {})
        if str(row.get("node_id", "")) == "node.alpha":
            source_mass = int(stocks.get("material.steel_basic", 0) or 0)
        if str(row.get("node_id", "")) == "node.beta":
            destination_mass = int(stocks.get("material.steel_basic", 0) or 0)
    if source_mass != 1_250 or destination_mass != 750:
        return {"status": "fail", "message": "deterministic source/destination inventory transfer mismatch"}
    return {"status": "pass", "message": "manifest_tick delivery deterministic behavior passed"}
