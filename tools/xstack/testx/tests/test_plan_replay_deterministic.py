"""STRICT test: plan create+execute sequence is deterministic across replay-equivalent runs."""

from __future__ import annotations

import copy
import os
import shutil
import sys


TEST_ID = "testx.control.plan_replay_deterministic"
TEST_TAGS = ["strict", "control", "planning", "replay", "determinism"]


def _run_sequence(*, repo_root: str) -> dict:
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.sessionx import process_runtime
    from tools.xstack.testx.tests.plan_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        structure_plan_create_inputs,
    )

    state = base_state()
    law = law_profile()
    auth = authority_context()
    policy = policy_context(repo_root)
    create_result = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.replay.create",
            "process_id": "process.plan_create",
            "inputs": copy.deepcopy(structure_plan_create_inputs()),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(create_result.get("result", "")) != "complete":
        return {"result": "refused", "message": "plan_create refused in replay sequence"}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    if len(plan_rows) != 1:
        return {"result": "refused", "message": "expected one plan artifact after create in replay sequence"}
    plan_id = str(plan_rows[0].get("plan_id", "")).strip()
    execute_result = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.replay.execute",
            "process_id": "process.plan_execute",
            "inputs": {"plan_id": plan_id, "abstraction_level_requested": "AL2"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(execute_result.get("result", "")) != "complete":
        return {"result": "refused", "message": "plan_execute refused in replay sequence"}
    return {
        "result": "complete",
        "plan_id": plan_id,
        "anchors": [
            str(create_result.get("state_hash_anchor", "")),
            str(execute_result.get("state_hash_anchor", "")),
        ],
        "final_state_hash": canonical_sha256(state),
        "commitment_ids": sorted(
            str(row.get("commitment_id", "")).strip()
            for row in list(state.get("construction_commitments") or [])
            if isinstance(row, dict) and str(row.get("commitment_id", "")).strip()
        ),
        "plan_status": str(
            (
                [
                    dict(row)
                    for row in list(state.get("plan_artifacts") or [])
                    if isinstance(row, dict) and str(row.get("plan_id", "")).strip() == plan_id
                ]
                or [{}]
            )[0].get("status", "")
        ).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256

    decisions_dir = os.path.join(repo_root, "run_meta", "control_decisions")
    shutil.rmtree(decisions_dir, ignore_errors=True)
    first = _run_sequence(repo_root=repo_root)
    shutil.rmtree(decisions_dir, ignore_errors=True)
    second = _run_sequence(repo_root=repo_root)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "plan replay sequence refused unexpectedly"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "plan replay sequence drifted across equivalent runs"}
    return {"status": "pass", "message": "plan create+execute sequence is replay-deterministic"}
