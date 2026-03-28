"""FAST test: construction tick refuses deterministically on insufficient materials."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.insufficient_material_refusal"
TEST_TAGS = ["fast", "materials", "construction", "refusal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.construction.construction_engine import REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL
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
            mass=1_000,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=1_000,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.create.refusal",
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
        return {"status": "fail", "message": "construction create unexpectedly failed in insufficient-material refusal test"}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.tick.refusal",
            "process_id": "process.construction_project_tick",
            "inputs": {"max_projects_per_tick": 4},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "refused":
        return {"status": "fail", "message": "construction tick should refuse when required stock is unavailable"}
    reason_code = str(((dict(ticked.get("refusal") or {})).get("reason_code", "")).strip())
    if reason_code != REFUSAL_CONSTRUCTION_INSUFFICIENT_MATERIAL:
        return {
            "status": "fail",
            "message": "unexpected refusal code '{}' for insufficient material tick".format(reason_code),
        }
    return {"status": "pass", "message": "insufficient-material refusal emitted deterministically"}

