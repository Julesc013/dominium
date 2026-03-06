"""FAST test: PROC-3 QC replay verifier produces stable hash matches."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_qc_hash_match"
TEST_TAGS = ["fast", "proc", "qc", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_qc_window import verify_qc_replay_window
    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    first = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.replay",
        qc_policy_id="qc.basic_sampling",
        output_batch_ids=["batch.output.01", "batch.output.02", "batch.output.03", "batch.output.04"],
    )
    second = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.replay",
        qc_policy_id="qc.basic_sampling",
        output_batch_ids=["batch.output.01", "batch.output.02", "batch.output.03", "batch.output.04"],
    )
    if str((dict(first.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first process_run_end failed"}
    if str((dict(second.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second process_run_end failed"}

    report = verify_qc_replay_window(
        state_payload=dict(first.get("state") or {}),
        expected_payload=dict(second.get("state") or {}),
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "qc replay verifier reported violations: {}".format(report.get("violations", []))}
    for key in ("qc_result_hash_chain", "sampling_decision_hash_chain"):
        chain = str((dict(report.get("observed") or {}).get(key, ""))).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "PROC-3 QC replay hashes are stable"}
