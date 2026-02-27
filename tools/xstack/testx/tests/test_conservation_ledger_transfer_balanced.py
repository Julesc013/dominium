"""FAST test: logistics transfer preserves total material mass when loss_fraction is zero."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.conservation_ledger_transfer_balanced"
TEST_TAGS = ["fast", "materials", "logistics", "conservation"]


def _total_mass(state: dict, material_id: str) -> int:
    total = 0
    for row in list(state.get("logistics_node_inventories") or []):
        if not isinstance(row, dict):
            continue
        stocks = dict(row.get("material_stocks") or {})
        total += int(stocks.get(material_id, 0) or 0)
    return int(total)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.logistics_testlib import (
        authority_context,
        base_state,
        law_profile,
        logistics_graph,
        policy_context,
        with_inventory,
    )

    material_id = "material.steel_basic"
    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id=material_id,
        mass=1_500,
        batch_id="batch.cons",
    )
    law = law_profile(["process.manifest_create", "process.manifest_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context(graph_rows=[logistics_graph(delay_ticks=0, loss_fraction=0)])

    before_mass = _total_mass(state, material_id)
    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.conservation.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.cons",
                "material_id": material_id,
                "quantity_mass": 900,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_create failed in conservation transfer test"}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.conservation.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_tick failed in conservation transfer test"}

    after_mass = _total_mass(state, material_id)
    if int(before_mass) != int(after_mass):
        return {
            "status": "fail",
            "message": "total material mass drifted across zero-loss shipment (before={}, after={})".format(before_mass, after_mass),
        }
    metadata = dict(ticked.get("result_metadata") or {})
    if int(metadata.get("loss_count", 0) or 0) != 0:
        return {"status": "fail", "message": "loss_count should be zero for zero-loss shipment transfer"}
    return {"status": "pass", "message": "logistics transfer mass conservation passed"}
