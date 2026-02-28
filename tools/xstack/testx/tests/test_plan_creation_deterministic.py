"""STRICT test: plan creation is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys
import os
import shutil


TEST_ID = "testx.control.plan_creation_deterministic"
TEST_TAGS = ["strict", "control", "planning", "determinism"]


def _reset_control_decisions(repo_root: str) -> None:
    decisions_dir = os.path.join(repo_root, "run_meta", "control_decisions")
    shutil.rmtree(decisions_dir, ignore_errors=True)


def _normalized_plan_artifact(row: dict) -> dict:
    artifact = dict(row or {})
    ext = dict(artifact.get("extensions") or {})
    ext.pop("control_decision_log_ref", None)
    ext.pop("control_resolution_id", None)
    artifact["extensions"] = ext
    artifact["deterministic_fingerprint"] = ""
    return artifact


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

    law = law_profile()
    auth = authority_context()
    policy = policy_context(repo_root)
    intent_payload = structure_plan_create_inputs()
    hashes = []
    for _ in (0, 1):
        _reset_control_decisions(repo_root)
        state = base_state()
        executed = process_runtime.execute_intent(
            state=state,
            intent={
                "intent_id": "intent.plan.create.test",
                "process_id": "process.plan_create",
                "inputs": copy.deepcopy(intent_payload),
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(auth),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(executed.get("result", "")) != "complete":
            return {"status": "fail", "message": "process.plan_create refused during determinism check"}
        plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
        if len(plan_rows) != 1:
            return {"status": "fail", "message": "expected exactly one plan artifact after deterministic create"}
        hashes.append(canonical_sha256(_normalized_plan_artifact(plan_rows[0])))
    if hashes[0] != hashes[1]:
        return {"status": "fail", "message": "plan artifact hash drifted across identical plan_create inputs"}
    return {"status": "pass", "message": "plan creation deterministic across identical inputs"}
