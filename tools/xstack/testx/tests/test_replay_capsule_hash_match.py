"""FAST test: PROC-5 capsule replay verifier reports stable hash matches."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_capsule_hash_match"
TEST_TAGS = ["fast", "proc", "proc5", "capsule", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_capsule_window import verify_capsule_replay_window
    from tools.xstack.testx.tests.proc5_testlib import run_proc5_capsule_case

    first = run_proc5_capsule_case(repo_root=repo_root, compile_with_compiled_model=True)
    second = run_proc5_capsule_case(repo_root=repo_root, compile_with_compiled_model=True)
    if str((dict(first.get("generation") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first capsule generation did not complete"}
    if str((dict(second.get("generation") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second capsule generation did not complete"}
    if str((dict(first.get("execution") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first capsule execution did not complete"}
    if str((dict(second.get("execution") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second capsule execution did not complete"}

    report = verify_capsule_replay_window(
        state_payload=dict(first.get("state") or {}),
        expected_payload=dict(second.get("state") or {}),
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "capsule replay verifier reported violations: {}".format(
                list(report.get("violations") or [])
            ),
        }
    observed = dict(report.get("observed") or {})
    for key in (
        "capsule_generation_hash_chain",
        "capsule_execution_hash_chain",
        "compiled_model_hash_chain",
    ):
        value = str(observed.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(value):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "PROC-5 replay capsule hash chains match deterministically"}

