"""FAST test: construction step scheduling is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.step_scheduling_deterministic"
TEST_TAGS = ["fast", "materials", "construction", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_inventory,
    )

    state = with_inventory(
        with_inventory(
            base_state(),
            node_id="node.alpha",
            material_id="material.wood_basic",
            mass=8_000_000_000,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=8_000_000_000,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.create.schedule",
            "process_id": "process.construction_project_create",
            "inputs": {
                "blueprint_id": "blueprint.house.basic",
                "site_ref": "site.alpha",
                "logistics_node_id": "node.alpha",
                "construction_policy_id": "build.policy.default",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"result": created, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.tick.schedule",
            "process_id": "process.construction_project_tick",
            "inputs": {"max_projects_per_tick": 16},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": ticked, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "construction_project_tick must complete in scheduling determinism test"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "construction scheduling state hash anchor diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "construction scheduling mutated state non-deterministically"}

    steps = sorted(
        [dict(row) for row in list(first_state.get("construction_steps") or []) if isinstance(row, dict)],
        key=lambda row: (str(row.get("ag_node_id", "")), str(row.get("step_id", ""))),
    )
    if len(steps) < 3:
        return {"status": "fail", "message": "expected at least three steps for blueprint.house.basic scheduling test"}
    row_by_node = dict((str(row.get("ag_node_id", "")), dict(row)) for row in steps)
    for required in ("node.house.frame", "node.house.panel", "node.house.root"):
        if required not in row_by_node:
            return {"status": "fail", "message": "missing expected AG node '{}'".format(required)}

    executing_nodes = sorted(
        str(row.get("ag_node_id", ""))
        for row in steps
        if str(row.get("status", "")) == "executing"
    )
    if executing_nodes != ["node.house.frame", "node.house.panel"]:
        return {"status": "fail", "message": "deterministic scheduling should start frame and panel first"}

    frame_end = int(row_by_node["node.house.frame"].get("scheduled_end_tick", 0) or 0)
    panel_end = int(row_by_node["node.house.panel"].get("scheduled_end_tick", 0) or 0)
    root_start = int(row_by_node["node.house.root"].get("scheduled_start_tick", 0) or 0)
    if root_start < max(frame_end, panel_end):
        return {"status": "fail", "message": "root step must be scheduled after dependency completion ticks"}
    return {"status": "pass", "message": "construction step scheduling deterministic behavior passed"}

