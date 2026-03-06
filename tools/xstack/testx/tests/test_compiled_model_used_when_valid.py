"""FAST test: PROC-5 capsules use compiled model execution when valid."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_compiled_model_used_when_valid"
TEST_TAGS = ["fast", "proc", "proc5", "capsule", "compile"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc5_testlib import run_proc5_capsule_case

    payload = run_proc5_capsule_case(
        repo_root=repo_root,
        compile_with_compiled_model=True,
    )
    generation = dict(payload.get("generation") or {})
    execution = dict(payload.get("execution") or {})
    state = dict(payload.get("state") or {})

    if str(generation.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compiled capsule generation failed"}
    if not isinstance(generation.get("compiled_model_row"), dict) or not generation.get("compiled_model_row"):
        return {"status": "fail", "message": "compiled capsule generation missing compiled_model_row"}
    if str(execution.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compiled capsule execution did not complete"}
    if not bool(execution.get("compiled_model_used", False)):
        return {"status": "fail", "message": "compiled model should be used when validity checks pass"}

    compiled_validation = dict(execution.get("compiled_model_validation") or {})
    if not bool(compiled_validation.get("valid", False)):
        return {
            "status": "fail",
            "message": "compiled model unexpectedly invalid: {}".format(compiled_validation),
        }
    compiled_execution = dict(execution.get("compiled_model_execution") or {})
    if str(compiled_execution.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compiled model execution path did not complete"}

    chain = str(state.get("compiled_model_hash_chain", "")).strip().lower()
    if not _HASH64.fullmatch(chain):
        return {"status": "fail", "message": "compiled_model_hash_chain missing or invalid"}
    return {"status": "pass", "message": "valid compiled models are used by PROC-5 capsule execution"}

