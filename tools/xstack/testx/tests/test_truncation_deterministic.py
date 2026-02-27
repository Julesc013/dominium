"""FAST test: materialization truncation is deterministic under stable budget constraints."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.truncation_deterministic"
TEST_TAGS = ["fast", "materials", "materialization", "budget", "determinism"]


def _run_once() -> dict:
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
        structure_id="assembly.structure_instance.epsilon",
        ag_node_id="ag.node.epsilon",
        total_mass=1500,
        part_count=10,
        batch_id="batch.epsilon",
        material_id="material.steel_basic",
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.epsilon.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {
                "structure_instance_id": "assembly.structure_instance.epsilon",
                "roi_id": "roi.epsilon",
                "max_micro_parts": 3,
                "strict_budget": False,
            },
        },
        law_profile=law_profile(["process.materialize_structure_roi"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(max_micro_parts_per_roi=3),
    )
    micro_ids = sorted(
        str(row.get("micro_part_id", "")).strip()
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict)
        and str(row.get("parent_structure_id", "")).strip() == "assembly.structure_instance.epsilon"
        and str((dict(row.get("extensions") or {})).get("roi_id", "")).strip() == "roi.epsilon"
    )
    metadata = dict(result.get("result_metadata") or {})
    return {"result": result, "micro_ids": micro_ids, "metadata": metadata}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialization truncation fixture must complete"}
    first_meta = dict(first.get("metadata") or {})
    second_meta = dict(second.get("metadata") or {})
    if not bool(first_meta.get("truncated", False)) or not bool(second_meta.get("truncated", False)):
        return {"status": "fail", "message": "materialization should be truncated under strict small budget"}
    if list(first.get("micro_ids") or []) != list(second.get("micro_ids") or []):
        return {"status": "fail", "message": "truncated micro part selection diverged"}
    if int(first_meta.get("truncated_count", 0) or 0) != int(second_meta.get("truncated_count", 0) or 0):
        return {"status": "fail", "message": "truncated count diverged"}
    return {"status": "pass", "message": "deterministic truncation passed"}

