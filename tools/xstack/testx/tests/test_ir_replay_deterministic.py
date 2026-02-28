"""STRICT test: IR replay sequence reconstruction from decision logs is deterministic."""

from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.control_ir.replay_deterministic"
TEST_TAGS = ["strict", "control", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import reconstruct_ir_action_sequence, verify_and_compile_control_ir
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.control_ir_testlib import deep_copy_inputs

    fixture = deep_copy_inputs()
    temp_root = tempfile.mkdtemp(prefix="xstack_ir_replay_")
    try:
        compiled = verify_and_compile_control_ir(
            ir_program=copy.deepcopy(fixture["ir_program"]),
            control_policy=copy.deepcopy(fixture["control_policy"]),
            authority_context=copy.deepcopy(fixture["authority_context"]),
            capability_registry=copy.deepcopy(fixture["capability_registry"]),
            law_profile=copy.deepcopy(fixture["law_profile"]),
            control_action_registry=copy.deepcopy(fixture["control_action_registry"]),
            control_policy_registry=copy.deepcopy(fixture["control_policy_registry"]),
            policy_context=copy.deepcopy(fixture["policy_context"]),
            repo_root=temp_root,
            rs5_budget_units=10,
        )
        if str(compiled.get("result", "")) != "complete":
            return {"status": "fail", "message": "baseline IR compile refused in replay determinism test"}
        log_refs = list(compiled.get("decision_log_refs") or [])
        if not log_refs:
            return {"status": "fail", "message": "compiled IR missing decision_log_refs for replay reconstruction"}
        log_rows = []
        for rel in log_refs:
            abs_path = os.path.join(temp_root, str(rel).replace("/", os.sep))
            if not os.path.isfile(abs_path):
                return {"status": "fail", "message": "decision log ref path missing on disk during replay reconstruction"}
            log_rows.append(json.load(open(abs_path, "r", encoding="utf-8")))
        first = reconstruct_ir_action_sequence(
            decision_log_rows=copy.deepcopy(log_rows),
            ir_id=str(compiled.get("control_ir_id", "")),
        )
        second = reconstruct_ir_action_sequence(
            decision_log_rows=list(reversed(copy.deepcopy(log_rows))),
            ir_id=str(compiled.get("control_ir_id", "")),
        )
        if canonical_sha256(first) != canonical_sha256(second):
            return {"status": "fail", "message": "reconstructed replay action sequence drifted across row-order variation"}
        if int(len(list(first.get("action_sequence") or []))) < 1:
            return {"status": "fail", "message": "reconstructed replay sequence is empty"}
        return {"status": "pass", "message": "IR replay reconstruction deterministic from decision logs"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

