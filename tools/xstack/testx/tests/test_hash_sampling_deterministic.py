"""FAST test: PROC-3 hash-based QC sampling decisions are deterministic."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_hash_sampling_deterministic"
TEST_TAGS = ["fast", "proc", "qc", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    batch_ids = [
        "batch.output.01",
        "batch.output.02",
        "batch.output.03",
        "batch.output.04",
        "batch.output.05",
    ]
    first = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.hash.det",
        qc_policy_id="qc.basic_sampling",
        output_batch_ids=batch_ids,
    )
    second = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.hash.det",
        qc_policy_id="qc.basic_sampling",
        output_batch_ids=batch_ids,
    )
    if str((dict(first.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first process_run_end failed"}
    if str((dict(second.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second process_run_end failed"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    for key in ("qc_result_hash_chain", "sampling_decision_hash_chain"):
        first_hash = str(first_state.get(key, "")).strip().lower()
        second_hash = str(second_state.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(first_hash):
            return {"status": "fail", "message": "{} missing/invalid on first run".format(key)}
        if first_hash != second_hash:
            return {"status": "fail", "message": "{} mismatch across equivalent runs".format(key)}

    return {"status": "pass", "message": "PROC-3 hash-based sampling is deterministic"}
