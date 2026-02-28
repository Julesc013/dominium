"""STRICT test: Control IR compiler enforces RS-5 budget limits deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control_ir.cost_budget_enforced"
TEST_TAGS = ["strict", "control", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import REFUSAL_CTRL_IR_COST_EXCEEDED, verify_and_compile_control_ir
    from tools.xstack.testx.tests.control_ir_testlib import deep_copy_inputs

    fixture = deep_copy_inputs()
    compiled = verify_and_compile_control_ir(
        ir_program=copy.deepcopy(fixture["ir_program"]),
        control_policy=copy.deepcopy(fixture["control_policy"]),
        authority_context=copy.deepcopy(fixture["authority_context"]),
        capability_registry=copy.deepcopy(fixture["capability_registry"]),
        law_profile=copy.deepcopy(fixture["law_profile"]),
        control_action_registry=copy.deepcopy(fixture["control_action_registry"]),
        control_policy_registry=copy.deepcopy(fixture["control_policy_registry"]),
        policy_context=copy.deepcopy(fixture["policy_context"]),
        repo_root="",
        rs5_budget_units=3,
    )
    if str(compiled.get("result", "")) != "refused":
        return {"status": "fail", "message": "compile unexpectedly completed despite RS-5 budget shortfall"}
    refusal_row = dict(compiled.get("refusal") or {})
    if str(refusal_row.get("reason_code", "")) != REFUSAL_CTRL_IR_COST_EXCEEDED:
        return {"status": "fail", "message": "expected refusal.ctrl.ir_cost_exceeded for budget overflow"}
    return {"status": "pass", "message": "Control IR budget enforcement emits deterministic refusal"}

