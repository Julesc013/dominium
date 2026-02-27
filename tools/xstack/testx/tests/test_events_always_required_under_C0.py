"""FAST test: C0 path emits provenance event for macro manifest creation."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.events_always_required_under_c0"
TEST_TAGS = ["fast", "materials", "causality", "provenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.commitment_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
    )
    from tools.xstack.testx.tests.construction_testlib import with_inventory

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
            "intent_id": "intent.materials.events.c0.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 250,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=law_profile(["process.manifest_create"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(strictness_id="causality.C0"),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_create should complete under C0 with valid stock"}

    events = [
        dict(row)
        for row in list(state.get("logistics_provenance_events") or [])
        if isinstance(row, dict)
    ]
    manifest_rows = [
        dict(row)
        for row in list(state.get("logistics_manifests") or [])
        if isinstance(row, dict)
    ]
    if not events or not manifest_rows:
        return {"status": "fail", "message": "manifest_create must emit manifest row and provenance event under C0"}
    manifest_row = dict(manifest_rows[0])
    provenance_ids = list(manifest_row.get("provenance_event_ids") or [])
    if not provenance_ids:
        return {"status": "fail", "message": "manifest provenance_event_ids should include creation event under C0"}
    event_types = sorted(set(str(row.get("event_type", "")).strip() for row in events))
    if "shipment_manifest_created" not in event_types:
        return {"status": "fail", "message": "manifest_create must emit shipment_manifest_created provenance event"}
    return {"status": "pass", "message": "C0 macro event requirement coverage passed"}
