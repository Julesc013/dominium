"""FAST test: process.construction_project_create is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.project_create_deterministic"
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
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.create.001",
            "process_id": "process.construction_project_create",
            "inputs": {
                "blueprint_id": "blueprint.house.basic",
                "site_ref": "site.alpha",
                "logistics_node_id": "node.alpha",
                "construction_policy_id": "build.policy.default",
            },
        },
        law_profile=law_profile(["process.construction_project_create"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(),
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
        return {"status": "fail", "message": "construction_project_create must complete for valid blueprint/site inputs"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "construction_project_create state hash anchor diverged"}
    if str(first_result.get("ledger_hash", "")) != str(second_result.get("ledger_hash", "")):
        return {"status": "fail", "message": "construction_project_create ledger hash diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "construction_project_create mutated state non-deterministically"}

    projects = sorted(
        [dict(row) for row in list(first_state.get("construction_projects") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("project_id", "")),
    )
    steps = [dict(row) for row in list(first_state.get("construction_steps") or []) if isinstance(row, dict)]
    commitments = [dict(row) for row in list(first_state.get("construction_commitments") or []) if isinstance(row, dict)]
    structures = [dict(row) for row in list(first_state.get("installed_structure_instances") or []) if isinstance(row, dict)]
    events = [dict(row) for row in list(first_state.get("construction_provenance_events") or []) if isinstance(row, dict)]
    if len(projects) != 1 or not steps or not commitments or len(structures) != 1 or not events:
        return {"status": "fail", "message": "construction_project_create should emit project, steps, commitments, structure, and provenance"}
    project_id = str(projects[0].get("project_id", ""))
    if not project_id.startswith("project.construction."):
        return {"status": "fail", "message": "construction project deterministic id format mismatch"}
    if not any(str(row.get("event_type_id", "")) == "event.construct_project_created" for row in events):
        return {"status": "fail", "message": "construction project creation must emit construct_project_created event"}
    return {"status": "pass", "message": "construction_project_create deterministic behavior passed"}

