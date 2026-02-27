"""FAST test: deterministic loss fraction handling in manifest_tick."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.loss_fraction_deterministic"
TEST_TAGS = ["fast", "materials", "logistics", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.logistics_testlib import (
        FIXED_POINT_SCALE,
        authority_context,
        base_state,
        law_profile,
        logistics_graph,
        policy_context,
        with_inventory,
    )

    loss_fraction = int(FIXED_POINT_SCALE // 4)
    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id="material.steel_basic",
        mass=4_000,
        batch_id="batch.loss",
    )
    law = law_profile(["process.manifest_create", "process.manifest_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context(graph_rows=[logistics_graph(delay_ticks=0, loss_fraction=loss_fraction)])

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.loss.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.loss",
                "material_id": "material.steel_basic",
                "quantity_mass": 1000,
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
            "intent_id": "intent.logistics.loss.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 8},
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
        return {"status": "fail", "message": "loss-fraction manifest tick should complete"}
    if dict(first.get("state") or {}) != dict(second.get("state") or {}):
        return {"status": "fail", "message": "loss-fraction result state diverged across repeated runs"}

    state = dict(first.get("state") or {})
    manifests = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if len(manifests) != 1:
        return {"status": "fail", "message": "expected one manifest in loss-fraction test state"}
    if str(manifests[0].get("status", "")) != "lost":
        return {"status": "fail", "message": "manifest status should be 'lost' when loss_fraction > 0"}

    inventories = sorted(
        (dict(row) for row in list(state.get("logistics_node_inventories") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("node_id", "")),
    )
    destination_mass = 0
    for row in inventories:
        if str(row.get("node_id", "")) != "node.beta":
            continue
        destination_mass = int((dict(row.get("material_stocks") or {})).get("material.steel_basic", 0) or 0)
    if destination_mass != 750:
        return {"status": "fail", "message": "loss-fraction delivery mass should be deterministic (expected 750)"}

    events = list(state.get("logistics_provenance_events") or [])
    event_types = sorted(str((dict(row).get("event_type", ""))) for row in events if isinstance(row, dict))
    if "shipment_lost" not in event_types:
        return {"status": "fail", "message": "shipment_lost event missing for non-zero loss fraction"}
    return {"status": "pass", "message": "loss fraction deterministic behavior passed"}
