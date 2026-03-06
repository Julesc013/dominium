"""FAST test: PROC-2 quality replay verifier produces stable hash matches."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_quality_hash_match"
TEST_TAGS = ["fast", "proc", "quality", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_quality_window import verify_quality_replay_window
    from tools.xstack.testx.tests.proc2_testlib import run_proc2_quality_case

    first = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.replay",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
    )
    second = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.replay",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
    )
    if str((dict(first.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first process_run_end failed"}
    if str((dict(second.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second process_run_end failed"}

    report = verify_quality_replay_window(
        state_payload=dict(first.get("state") or {}),
        expected_payload=dict(second.get("state") or {}),
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "quality replay verifier reported violations: {}".format(report.get("violations", []))}
    for key in ("process_quality_hash_chain", "batch_quality_hash_chain"):
        chain = str((dict(report.get("observed") or {})).get(key, "")).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "PROC-2 quality replay hashes are stable"}
