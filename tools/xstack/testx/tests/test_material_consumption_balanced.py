"""FAST test: construction material consumption events are ledger-balanced."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.material_consumption_balanced"
TEST_TAGS = ["fast", "materials", "construction", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_inventory,
    )

    initial_wood_mass = 10_000_000_000
    initial_stone_mass = 10_000_000_000
    state = with_inventory(
        with_inventory(
            base_state(),
            node_id="node.alpha",
            material_id="material.wood_basic",
            mass=initial_wood_mass,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=initial_stone_mass,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.create.ledger",
            "process_id": "process.construction_project_create",
            "inputs": {
                "blueprint_id": "blueprint.house.basic",
                "site_ref": "site.alpha",
                "logistics_node_id": "node.alpha",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "construction project create failed in ledger-balance test"}

    project_rows = sorted(
        [dict(row) for row in list(state.get("construction_projects") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("project_id", "")),
    )
    if not project_rows:
        return {"status": "fail", "message": "construction project missing after create"}
    project_id = str(project_rows[0].get("project_id", ""))

    for index in range(8):
        ticked = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.construction.project.tick.ledger.{}".format(index),
                "process_id": "process.construction_project_tick",
                "inputs": {"max_projects_per_tick": 16},
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(ticked.get("result", "")) != "complete":
            return {"status": "fail", "message": "construction tick failed in ledger-balance test"}

    events = [
        dict(row)
        for row in list(state.get("construction_provenance_events") or [])
        if isinstance(row, dict) and str(row.get("linked_project_id", "")) == project_id
    ]
    if not events:
        return {"status": "fail", "message": "construction provenance events missing for project"}
    deltas = [int((dict(row.get("ledger_deltas") or {})).get("quantity.mass", 0) or 0) for row in events]
    if not any(delta < 0 for delta in deltas):
        return {"status": "fail", "message": "construction ledger deltas missing material debit events"}
    if not any(delta > 0 for delta in deltas):
        return {"status": "fail", "message": "construction ledger deltas missing batch credit events"}
    if int(sum(deltas)) != 0:
        return {"status": "fail", "message": "construction ledger mass delta must net to zero for balanced project"}

    inventory_rows = [
        dict(row)
        for row in list(state.get("logistics_node_inventories") or [])
        if isinstance(row, dict) and str(row.get("node_id", "")) == "node.alpha"
    ]
    if not inventory_rows:
        return {"status": "fail", "message": "node inventory missing after construction ticks"}
    stocks = dict(inventory_rows[0].get("material_stocks") or {})
    wood_after = int(stocks.get("material.wood_basic", 0) or 0)
    stone_after = int(stocks.get("material.stone_basic", 0) or 0)
    if wood_after >= initial_wood_mass:
        return {"status": "fail", "message": "expected construction tick path to debit wood inventory"}
    if stone_after >= initial_stone_mass:
        return {"status": "fail", "message": "expected construction tick path to debit stone inventory"}
    if wood_after < 0 or stone_after < 0:
        return {"status": "fail", "message": "construction inventory stock cannot become negative"}
    return {"status": "pass", "message": "construction material consumption remained ledger-balanced"}
