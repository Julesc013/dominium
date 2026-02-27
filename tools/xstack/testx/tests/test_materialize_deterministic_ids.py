"""FAST test: materialization emits deterministic micro part ids for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.materialize_deterministic_ids"
TEST_TAGS = ["fast", "materials", "materialization", "determinism"]


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
        structure_id="assembly.structure_instance.alpha",
        ag_node_id="ag.node.alpha",
        total_mass=1200,
        part_count=6,
        batch_id="batch.alpha",
        material_id="material.steel_basic",
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materialize.alpha.001",
            "process_id": "process.materialize_structure_roi",
            "inputs": {
                "structure_instance_id": "assembly.structure_instance.alpha",
                "roi_id": "roi.alpha",
                "max_micro_parts": 32,
            },
        },
        law_profile=law_profile(["process.materialize_structure_roi"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(max_micro_parts_per_roi=32),
    )
    micro_ids = sorted(
        str(row.get("micro_part_id", "")).strip()
        for row in list(state.get("micro_part_instances") or [])
        if isinstance(row, dict) and str(row.get("micro_part_id", "")).strip()
    )
    return {"result": result, "state": state, "micro_ids": micro_ids}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "materialize_structure_roi must complete for valid deterministic fixtures"}
    if list(first.get("micro_ids") or []) != list(second.get("micro_ids") or []):
        return {"status": "fail", "message": "materialized micro part ids diverged across equivalent runs"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "materialization state hash anchor diverged"}
    if copy.deepcopy(dict(first.get("state") or {})) != copy.deepcopy(dict(second.get("state") or {})):
        return {"status": "fail", "message": "materialization mutated state non-deterministically"}
    return {"status": "pass", "message": "materialization deterministic ids passed"}

