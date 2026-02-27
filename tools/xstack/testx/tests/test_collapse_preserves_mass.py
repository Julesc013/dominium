"""FAST test: dematerialization preserves aggregate mass for structure ROI collapse."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.collapse_preserves_mass"
TEST_TAGS = ["fast", "materials", "materialization", "conservation"]


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

    state = with_structure_aggregate(
        base_state(),
        structure_id="assembly.structure_instance.beta",
        ag_node_id="ag.node.beta",
        total_mass=900,
        part_count=9,
        batch_id="batch.beta",
        material_id="material.iron",
    )
    law = law_profile(["process.materialize_structure_roi", "process.dematerialize_structure_roi"])
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context(max_micro_parts_per_roi=64)

    expanded = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.beta.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {
                "structure_instance_id": "assembly.structure_instance.beta",
                "roi_id": "roi.beta",
                "max_micro_parts": 64,
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialize_structure_roi failed for collapse mass test"}

    collapsed = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.dematerialize.beta.001",
            "process_id": "process.dematerialize_structure_roi",
            "inputs": {
                "structure_instance_id": "assembly.structure_instance.beta",
                "roi_id": "roi.beta",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(collapsed.get("result", "")) != "complete":
        return {"status": "fail", "message": "dematerialize_structure_roi failed for collapse mass test"}

    aggregates = sorted(
        [
            dict(row)
            for row in list(state.get("distribution_aggregates") or [])
            if isinstance(row, dict)
            and str(row.get("structure_id", "")).strip() == "assembly.structure_instance.beta"
            and str(row.get("ag_node_id", "")).strip() == "ag.node.beta"
        ],
        key=lambda row: str(row.get("ag_node_id", "")),
    )
    if not aggregates:
        return {"status": "fail", "message": "collapse did not write distribution aggregate rows"}
    total_mass = int(sum(int(row.get("total_mass", 0) or 0) for row in aggregates))
    if total_mass != 900:
        return {
            "status": "fail",
            "message": "collapse mass mismatch expected=900 actual={}".format(total_mass),
        }
    if any(
        str(row.get("parent_structure_id", "")).strip() == "assembly.structure_instance.beta"
        and str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() == "roi.beta"
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict)
    ):
        return {"status": "fail", "message": "collapse retained micro parts for collapsed ROI"}
    return {"status": "pass", "message": "collapse preserves mass passed"}

