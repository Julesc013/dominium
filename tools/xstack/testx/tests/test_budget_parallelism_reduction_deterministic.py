"""FAST test: construction tick budget reduction order is deterministic by project_id."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.budget_parallelism_reduction_deterministic"
TEST_TAGS = ["fast", "materials", "construction", "budget", "determinism"]


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
            mass=20_000_000_000,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=20_000_000_000,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context(
        max_compute_units_per_tick=1,
        construction_cost_units_per_active_step=1,
        construction_max_projects_per_tick=16,
    )

    for idx, site_ref in enumerate(["site.alpha", "site.beta", "site.gamma"]):
        created = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.construction.project.create.budget.{}".format(idx),
                "process_id": "process.construction_project_create",
                "inputs": {
                    "blueprint_id": "blueprint.house.basic",
                    "site_ref": site_ref,
                    "logistics_node_id": "node.alpha",
                },
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(created.get("result", "")) != "complete":
            return {"result": created, "state": state, "project_ids": []}

    project_ids = sorted(
        str((dict(row).get("project_id", "")))
        for row in list(state.get("construction_projects") or [])
        if isinstance(row, dict) and str((dict(row).get("project_id", "")).strip())
    )
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.tick.budget",
            "process_id": "process.construction_project_tick",
            "inputs": {"max_projects_per_tick": 16},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": ticked, "state": state, "project_ids": project_ids}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "construction budget reduction tick should complete"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "construction budget reduction state hash anchor diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "construction budget reduction mutated state non-deterministically"}

    project_ids = list(first.get("project_ids") or [])
    if len(project_ids) < 3:
        return {"status": "fail", "message": "expected three projects for budget reduction determinism test"}
    skipped = list(first_result.get("skipped_project_ids") or [])
    if int(first_result.get("processed_project_count", 0) or 0) != 1:
        return {"status": "fail", "message": "budget reduction should process exactly one project at max_compute_units_per_tick=1"}
    if skipped != project_ids[1:]:
        return {"status": "fail", "message": "skipped project order must be deterministic by project_id"}

    project_rows = sorted(
        [dict(row) for row in list(first_state.get("construction_projects") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("project_id", "")),
    )
    row_by_id = dict((str(row.get("project_id", "")), dict(row)) for row in project_rows)
    first_project_status = str((row_by_id.get(project_ids[0]) or {}).get("status", ""))
    if first_project_status not in ("executing", "completed"):
        return {"status": "fail", "message": "first deterministic project should advance under budget-limited tick"}
    for project_id in project_ids[1:]:
        status = str((row_by_id.get(project_id) or {}).get("status", ""))
        if status != "planned":
            return {"status": "fail", "message": "skipped projects should remain planned in budget-limited tick"}
    return {"status": "pass", "message": "construction budget reduction deterministic behavior passed"}

