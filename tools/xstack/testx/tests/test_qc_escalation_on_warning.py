"""FAST test: PROC-6 warning drift escalates QC policy deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_qc_escalation_on_warning"
TEST_TAGS = ["fast", "proc", "proc6", "drift", "qc"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.maturity.metrics_engine import build_process_metrics_state_row
    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    previous_metrics = build_process_metrics_state_row(
        process_id="proc.test.proc3.qc",
        version="1.0.0",
        runs_count=1,
        yield_mean=0,
        yield_variance=0,
        defect_rate=0,
        qc_pass_rate=1000,
        env_deviation_score=0,
        calibration_deviation_score=0,
        last_update_tick=199,
        extensions={
            "yield_sum": 0,
            "yield_sq_sum": 0,
            "quality_samples": 1,
            "defect_sum": 0,
            "sampled_count": 0,
            "pass_count": 0,
            "env_deviation_sum": 0,
            "env_samples": 0,
            "calibration_deviation_sum": 0,
            "calibration_samples": 0,
            "last_env_snapshot_hash": "",
            "last_calibration_cert_id": "",
        },
    )
    payload = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc6.warning",
        qc_policy_id="qc.none",
        quality_inputs={
            "temperature": 620,
            "pressure_head": 220,
            "entropy_index": 1000,
            "tool_wear_permille": 1000,
            "input_batch_quality_permille": 1000,
            "spec_score_permille": 1000,
            "calibration_state_permille": 0,
        },
        run_state_overrides={"process_metrics_state_rows": [previous_metrics]},
        drift_update_stride=1,
        force_drift_update=True,
    )
    end = dict(payload.get("end") or {})
    state = dict(payload.get("state") or {})
    if str(end.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process run end failed for warning fixture"}
    if str(state.get("current_drift_band", "")).strip() != "drift.warning":
        return {"status": "fail", "message": "expected drift.warning band"}
    qc_changes = [
        dict(row)
        for row in list(state.get("qc_policy_change_rows") or [])
        if isinstance(row, dict)
    ]
    if not qc_changes:
        return {"status": "fail", "message": "warning drift should log QC escalation"}
    to_policy = str(qc_changes[-1].get("to_qc_policy_id", "")).strip()
    if to_policy != "qc.strict_sampling":
        return {"status": "fail", "message": "warning escalation target policy mismatch"}
    if bool(state.get("process_capsule_forced_invalid", False)):
        return {"status": "fail", "message": "warning drift must not force capsule invalidation"}
    return {"status": "pass", "message": "warning drift escalates QC policy deterministically"}

