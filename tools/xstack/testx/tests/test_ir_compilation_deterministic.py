"""STRICT test: Control IR verification+compilation must be deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control_ir.compilation_deterministic"
TEST_TAGS = ["strict", "control", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import verify_and_compile_control_ir
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.control_ir_testlib import deep_copy_inputs

    fixture = deep_copy_inputs()
    first = verify_and_compile_control_ir(
        ir_program=copy.deepcopy(fixture["ir_program"]),
        control_policy=copy.deepcopy(fixture["control_policy"]),
        authority_context=copy.deepcopy(fixture["authority_context"]),
        capability_registry=copy.deepcopy(fixture["capability_registry"]),
        law_profile=copy.deepcopy(fixture["law_profile"]),
        control_action_registry=copy.deepcopy(fixture["control_action_registry"]),
        control_policy_registry=copy.deepcopy(fixture["control_policy_registry"]),
        policy_context=copy.deepcopy(fixture["policy_context"]),
        repo_root="",
        rs5_budget_units=10,
    )
    second = verify_and_compile_control_ir(
        ir_program=copy.deepcopy(fixture["ir_program"]),
        control_policy=copy.deepcopy(fixture["control_policy"]),
        authority_context=copy.deepcopy(fixture["authority_context"]),
        capability_registry=copy.deepcopy(fixture["capability_registry"]),
        law_profile=copy.deepcopy(fixture["law_profile"]),
        control_action_registry=copy.deepcopy(fixture["control_action_registry"]),
        control_policy_registry=copy.deepcopy(fixture["control_policy_registry"]),
        policy_context=copy.deepcopy(fixture["policy_context"]),
        repo_root="",
        rs5_budget_units=10,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline compile unexpectedly refused"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "compile payload drift for identical Control IR inputs"}
    return {"status": "pass", "message": "Control IR compilation deterministic for identical inputs"}

