"""STRICT test: plan execution emits commitments/provenance and does not install structures directly."""

from __future__ import annotations

import copy
import sys
import os
import shutil


TEST_ID = "testx.control.plan_execute_creates_commitments_only"
TEST_TAGS = ["strict", "control", "planning", "commitment"]


def _reset_control_decisions(repo_root: str) -> None:
    decisions_dir = os.path.join(repo_root, "run_meta", "control_decisions")
    shutil.rmtree(decisions_dir, ignore_errors=True)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

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
    _reset_control_decisions(repo_root)
    created = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.execute.create",
            "process_id": "process.plan_create",
            "inputs": copy.deepcopy(structure_plan_create_inputs()),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "precondition process.plan_create refused"}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    if len(plan_rows) != 1:
        return {"status": "fail", "message": "expected one plan artifact before execute"}
    plan_id = str(plan_rows[0].get("plan_id", "")).strip()
    if not plan_id:
        return {"status": "fail", "message": "created plan artifact is missing plan_id"}

    before_installed = len(list(state.get("installed_structure_instances") or []))
    before_material_commitments = len(list(state.get("material_commitments") or []))
    before_construction_commitments = len(list(state.get("construction_commitments") or []))

    executed = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.execute.run",
            "process_id": "process.plan_execute",
            "inputs": {"plan_id": plan_id, "abstraction_level_requested": "AL2"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(executed.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.plan_execute refused unexpectedly"}
    after_installed = len(list(state.get("installed_structure_instances") or []))
    after_material_commitments = len(list(state.get("material_commitments") or []))
    after_construction_commitments = len(list(state.get("construction_commitments") or []))
    if after_installed != before_installed:
        return {"status": "fail", "message": "plan_execute performed direct structure installation"}
    if after_material_commitments <= before_material_commitments:
        return {"status": "fail", "message": "plan_execute did not emit material commitments"}
    if after_construction_commitments <= before_construction_commitments:
        return {"status": "fail", "message": "plan_execute did not emit construction commitments"}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    matched = [row for row in plan_rows if str(row.get("plan_id", "")).strip() == plan_id]
    if not matched:
        return {"status": "fail", "message": "plan artifact missing after execute"}
    if str(matched[0].get("status", "")).strip() != "approved":
        return {"status": "fail", "message": "plan artifact did not transition to approved status"}
    if int(executed.get("emitted_commitment_count", 0) or 0) < 1:
        return {"status": "fail", "message": "execution metadata missing emitted commitments"}
    return {"status": "pass", "message": "plan execution emitted commitments without direct installation"}
