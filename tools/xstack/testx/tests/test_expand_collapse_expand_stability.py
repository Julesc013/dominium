"""FAST test: expand->collapse->expand preserves deterministic micro identity and seeds."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.expand_collapse_expand_stability"
TEST_TAGS = ["fast", "materials", "materialization", "determinism"]


def _micro_identity_rows(state: dict, structure_id: str, roi_id: str):
    rows = []
    for row in list(state.get("micro_part_instances") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("parent_structure_id", "")).strip() != structure_id:
            continue
        if str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() != roi_id:
            continue
        rows.append(
            {
                "micro_part_id": str(row.get("micro_part_id", "")).strip(),
                "seed": str(row.get("deterministic_seed", "")).strip(),
                "mass": int(row.get("mass", 0) or 0),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("micro_part_id", "")))


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

    structure_id = "assembly.structure_instance.gamma"
    roi_id = "roi.gamma"
    state = with_structure_aggregate(
        base_state(),
        structure_id=structure_id,
        ag_node_id="ag.node.gamma",
        total_mass=1400,
        part_count=7,
        batch_id="batch.gamma",
        material_id="material.steel_basic",
    )
    law = law_profile(["process.materialize_structure_roi", "process.dematerialize_structure_roi"])
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = policy_context(max_micro_parts_per_roi=64)

    first_expand = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.gamma.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(first_expand.get("result", "")) != "complete":
        return {"status": "fail", "message": "initial materialize failed"}
    first_rows = _micro_identity_rows(state, structure_id=structure_id, roi_id=roi_id)
    if not first_rows:
        return {"status": "fail", "message": "initial expand produced no micro parts"}

    collapsed = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.dematerialize.gamma.001",
            "process_id": "process.dematerialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(collapsed.get("result", "")) != "complete":
        return {"status": "fail", "message": "collapse failed during expand-collapse-expand stability test"}

    second_expand = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.gamma.002",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(second_expand.get("result", "")) != "complete":
        return {"status": "fail", "message": "second expand failed during stability test"}
    second_rows = _micro_identity_rows(state, structure_id=structure_id, roi_id=roi_id)
    if first_rows != second_rows:
        return {"status": "fail", "message": "expand-collapse-expand did not preserve deterministic micro identity"}
    return {"status": "pass", "message": "expand-collapse-expand stability passed"}

