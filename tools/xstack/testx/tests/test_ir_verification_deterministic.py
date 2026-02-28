"""STRICT test: Control IR static verification must be deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control_ir.verification_deterministic"
TEST_TAGS = ["strict", "control", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import verify_control_ir
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.control_ir_testlib import (
        authority_context,
        autopilot_ir,
        capability_registry,
        control_policy_row,
    )

    ir_program = autopilot_ir()
    control_policy = control_policy_row()
    auth = authority_context()
    caps = capability_registry()

    first = verify_control_ir(
        ir_program=copy.deepcopy(ir_program),
        control_policy=copy.deepcopy(control_policy),
        authority_context=copy.deepcopy(auth),
        capability_registry=copy.deepcopy(caps),
    )
    second = verify_control_ir(
        ir_program=copy.deepcopy(ir_program),
        control_policy=copy.deepcopy(control_policy),
        authority_context=copy.deepcopy(auth),
        capability_registry=copy.deepcopy(caps),
    )
    if not bool(first.get("valid", False)):
        return {"status": "fail", "message": "verification unexpectedly invalid for baseline autopilot IR"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "verification report hash drift for identical IR inputs"}
    return {"status": "pass", "message": "Control IR verification deterministic for identical inputs"}

