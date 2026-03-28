"""FAST test: PROC-4 metrics aggregation is deterministic for equivalent inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_metrics_aggregation_deterministic"
TEST_TAGS = ["fast", "proc", "maturity", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.maturity.metrics_engine import update_process_metrics_for_run

    kwargs = {
        "current_tick": 512,
        "process_id": "proc.test.proc4.metrics",
        "version": "1.0.0",
        "previous_metrics_row": None,
        "process_quality_row": {
            "run_id": "run.proc4.metrics.1",
            "yield_factor": 910,
            "defect_flags": ["incomplete_process"],
            "quality_grade": "grade.B",
            "extensions": {"defect_severity": 140},
        },
        "qc_result_rows": [
            {"run_id": "run.proc4.metrics.1", "batch_id": "batch.1", "sampled": True, "passed": True},
            {"run_id": "run.proc4.metrics.1", "batch_id": "batch.2", "sampled": True, "passed": False},
        ],
        "environment_snapshot_hash": "env.proc4.metrics.hash",
        "calibration_cert_id": "cert.proc4.metrics.1",
        "update_stride": 1,
        "force_update": True,
        "policy_id": "stab.default",
    }
    first = update_process_metrics_for_run(**kwargs)
    second = update_process_metrics_for_run(**kwargs)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first metrics update did not complete"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second metrics update did not complete"}

    first_row = dict(first.get("metrics_row") or {})
    second_row = dict(second.get("metrics_row") or {})
    if first_row != second_row:
        return {"status": "fail", "message": "metrics rows mismatch across equivalent inputs"}
    if int(first_row.get("runs_count", 0)) != 1:
        return {"status": "fail", "message": "expected runs_count=1 after first quality sample"}
    fingerprint = str(first.get("deterministic_fingerprint", "")).strip().lower()
    if not _HASH64.fullmatch(fingerprint):
        return {"status": "fail", "message": "metrics update deterministic_fingerprint missing/invalid"}
    return {"status": "pass", "message": "PROC-4 metrics aggregation is deterministic"}
