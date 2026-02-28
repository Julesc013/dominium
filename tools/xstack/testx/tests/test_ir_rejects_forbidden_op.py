"""STRICT test: Control IR verifier rejects forbidden op types."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control_ir.rejects_forbidden_op"
TEST_TAGS = ["strict", "control", "refusal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import REFUSAL_CTRL_IR_FORBIDDEN_OP, verify_control_ir
    from tools.xstack.testx.tests.control_ir_testlib import (
        authority_context,
        autopilot_ir,
        capability_registry,
        control_policy_row,
    )

    ir_program = autopilot_ir()
    ir_ext = dict(ir_program.get("extensions") or {})
    op_rows = [dict(row) for row in list(ir_ext.get("op_rows") or []) if isinstance(row, dict)]
    if not op_rows:
        return {"status": "fail", "message": "baseline autopilot IR missing op_rows payload"}
    op_rows[0]["op_type"] = "op.forbidden.magic"
    ir_ext["op_rows"] = op_rows
    ir_program["extensions"] = ir_ext

    report = verify_control_ir(
        ir_program=copy.deepcopy(ir_program),
        control_policy=copy.deepcopy(control_policy_row()),
        authority_context=copy.deepcopy(authority_context()),
        capability_registry=copy.deepcopy(capability_registry()),
    )
    if bool(report.get("valid", False)):
        return {"status": "fail", "message": "verifier accepted forbidden op_type"}
    violations = list(report.get("violations") or [])
    if not any(str((dict(row or {})).get("code", "")) == REFUSAL_CTRL_IR_FORBIDDEN_OP for row in violations):
        return {"status": "fail", "message": "forbidden-op refusal code missing from verification report"}
    return {"status": "pass", "message": "forbidden Control IR ops are rejected deterministically"}

