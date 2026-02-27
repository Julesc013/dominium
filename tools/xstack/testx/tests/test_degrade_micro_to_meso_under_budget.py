"""FAST test: MAT-9 inspection deterministically degrades micro requests under tight budget."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.degrade_micro_to_meso_under_budget"
TEST_TAGS = ["fast", "materials", "inspection", "budget", "degrade"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.materialization_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_structure_aggregate,
    )

    structure_id = "assembly.structure_instance.inspect.budget"
    roi_id = "roi.inspect.budget"
    state = with_structure_aggregate(
        base_state(),
        structure_id=structure_id,
        ag_node_id="ag.node.inspect.budget",
        total_mass=2_400,
        part_count=16,
        batch_id="batch.inspect.budget",
        material_id="material.steel_basic",
    )
    law = law_profile(["process.materialize_structure_roi", "process.inspect_generate_snapshot"])
    admin_authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    observe_authority = authority_context(["entitlement.inspect"], privilege_level="observer", visibility_level="nondiegetic")
    policy = policy_context(max_micro_parts_per_roi=64)

    expanded = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.budget.expand.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(admin_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialization setup failed for budget degradation test"}

    inspected = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.budget.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {
                "target_id": "materialization.state.{}::{}".format(structure_id, roi_id),
                "desired_fidelity": "micro",
                "cost_units": 1,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(observe_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(inspected.get("result", "")) != "complete":
        return {"status": "fail", "message": "micro inspection request should degrade, not refuse, under non-strict budget"}
    achieved = str(inspected.get("achieved_fidelity", "")).strip()
    if achieved == "micro":
        return {"status": "fail", "message": "micro inspection should degrade under tight budget"}
    if not bool(inspected.get("inspection_degraded", False)):
        return {"status": "fail", "message": "inspection should report degraded fidelity under tight budget"}
    return {"status": "pass", "message": "inspection micro->meso/macro degradation passed"}

