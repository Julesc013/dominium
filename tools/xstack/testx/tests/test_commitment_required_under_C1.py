"""FAST test: C1 strictness refuses major macro change without commitment linkage."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.commitment_required_under_c1"
TEST_TAGS = ["fast", "materials", "commitment", "causality"]


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

    state = base_state()
    state["logistics_node_inventories"] = [
        {
            "schema_version": "1.0.0",
            "node_id": "node.alpha",
            "material_stocks": {"material.steel_basic": 1_000},
            "batch_refs": ["batch.seed"],
            "inventory_hash": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "node_id": "node.beta",
            "material_stocks": {},
            "batch_refs": [],
            "inventory_hash": "",
            "extensions": {},
        },
    ]
    state["logistics_manifests"] = [
        {
            "schema_version": "1.0.0",
            "manifest_id": "manifest.seed.no_commitment",
            "graph_id": "graph.logistics.test",
            "from_node_id": "node.alpha",
            "to_node_id": "node.beta",
            "batch_id": "batch.seed",
            "material_id": "material.steel_basic",
            "quantity_mass": 100,
            "scheduled_depart_tick": 0,
            "scheduled_arrive_tick": 1,
            "status": "planned",
            "provenance_event_ids": [],
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["shipment_commitments"] = []
    state["material_commitments"] = []

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.commitment.required.c1",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 4},
        },
        law_profile=law_profile(["process.manifest_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(strictness_id="causality.C1"),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "manifest_tick should refuse under C1 without commitment linkage"}
    refusal_row = dict(result.get("refusal") or {})
    if str(refusal_row.get("reason_code", "")) != "refusal.commitment.required_missing":
        return {"status": "fail", "message": "expected refusal.commitment.required_missing under C1"}

    # Determinism check on equivalent cloned state.
    second = execute_intent(
        state=copy.deepcopy(state),
        intent={
            "intent_id": "intent.materials.commitment.required.c1",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 4},
        },
        law_profile=law_profile(["process.manifest_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=policy_context(strictness_id="causality.C1"),
    )
    if dict(result.get("refusal") or {}) != dict(second.get("refusal") or {}):
        return {"status": "fail", "message": "C1 commitment refusal diverged across identical runs"}
    return {"status": "pass", "message": "C1 commitment requirement refusal passed"}
