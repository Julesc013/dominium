"""STRICT test: plan creation remains derived-only and does not mutate truth structures."""

from __future__ import annotations

import copy
import sys
import os
import shutil


TEST_ID = "testx.control.plan_does_not_mutate_truth"
TEST_TAGS = ["strict", "control", "planning", "derived_only"]


_TRUTH_KEYS = (
    "installed_structure_instances",
    "construction_projects",
    "construction_steps",
    "construction_commitments",
    "construction_provenance_events",
    "material_commitments",
)


def _reset_control_decisions(repo_root: str) -> None:
    decisions_dir = os.path.join(repo_root, "run_meta", "control_decisions")
    shutil.rmtree(decisions_dir, ignore_errors=True)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

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
    before_hashes = {
        key: canonical_sha256(list(state.get(key) or []))
        for key in _TRUTH_KEYS
    }
    _reset_control_decisions(repo_root)
    executed = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.truth.guard",
            "process_id": "process.plan_create",
            "inputs": copy.deepcopy(structure_plan_create_inputs()),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(executed.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.plan_create refused in derived-only test"}
    for key in _TRUTH_KEYS:
        after_hash = canonical_sha256(list(state.get(key) or []))
        if before_hashes[key] != after_hash:
            return {"status": "fail", "message": "derived-only planning mutated truth key '{}'".format(key)}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    if not plan_rows:
        return {"status": "fail", "message": "plan_artifacts missing after plan_create"}
    return {"status": "pass", "message": "plan_create remained derived-only (no truth mutation)"}
