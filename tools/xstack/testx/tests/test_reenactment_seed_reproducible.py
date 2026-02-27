"""FAST test: materialization deterministic seeds and reenactment descriptor are reproducible."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.reenactment_seed_reproducible"
TEST_TAGS = ["fast", "materials", "materialization", "reenactment", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.materialization_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_structure_aggregate,
    )

    structure_id = "assembly.structure_instance.zeta"
    roi_id = "roi.zeta"
    state = with_structure_aggregate(
        base_state(),
        structure_id=structure_id,
        ag_node_id="ag.node.zeta",
        total_mass=1000,
        part_count=5,
        batch_id="batch.zeta",
        material_id="material.steel_basic",
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.zeta.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {"structure_instance_id": structure_id, "roi_id": roi_id, "max_micro_parts": 64},
        },
        law_profile=law_profile(["process.materialize_structure_roi"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(max_micro_parts_per_roi=64),
    )
    seeds = sorted(
        str(row.get("deterministic_seed", "")).strip()
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict)
        and str(row.get("parent_structure_id", "")).strip() == structure_id
        and str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() == roi_id
    )
    descriptors = sorted(
        [
            dict(row)
            for row in list(state.get("materialization_reenactment_descriptors") or [])
            if isinstance(row, dict)
            and str(row.get("structure_id", "")).strip() == structure_id
            and str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() == roi_id
        ],
        key=lambda row: str(row.get("seed_reference", "")),
    )
    descriptor = dict(descriptors[0]) if descriptors else {}
    return {
        "result": result,
        "seeds": seeds,
        "descriptor_seed_reference": str(descriptor.get("seed_reference", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialize_structure_roi must complete for reenactment seed test"}
    if list(first.get("seeds") or []) != list(second.get("seeds") or []):
        return {"status": "fail", "message": "deterministic_seed values diverged across equivalent runs"}
    if str(first.get("descriptor_seed_reference", "")) != str(second.get("descriptor_seed_reference", "")):
        return {"status": "fail", "message": "reenactment descriptor seed_reference diverged"}
    if not list(first.get("seeds") or []):
        return {"status": "fail", "message": "no seeds produced for reenactment reproducibility validation"}
    if not str(first.get("descriptor_seed_reference", "")):
        return {"status": "fail", "message": "reenactment descriptor seed_reference missing"}
    return {"status": "pass", "message": "reenactment seeds reproducible"}

