"""FAST test: PROC-6 critical drift invalidates process capsules deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_capsule_invalidated_on_critical"
TEST_TAGS = ["fast", "proc", "proc6", "drift", "capsule"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.maturity.metrics_engine import build_process_metrics_state_row
    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    previous_metrics = build_process_metrics_state_row(
        process_id="proc.test.proc3.qc",
        version="1.0.0",
        runs_count=1,
        yield_mean=1000,
        yield_variance=0,
        defect_rate=0,
        qc_pass_rate=1000,
        env_deviation_score=0,
        calibration_deviation_score=0,
        last_update_tick=199,
        extensions={
            "yield_sum": 1000,
            "yield_sq_sum": 1000000,
            "quality_samples": 1,
            "defect_sum": 0,
            "sampled_count": 3,
            "pass_count": 3,
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
        run_id="run.proc6.critical",
        qc_policy_id="qc.strict_sampling",
        quality_inputs={
            "temperature": 2000,
            "pressure_head": 2000,
            "entropy_index": 1000,
            "tool_wear_permille": 1000,
            "input_batch_quality_permille": 0,
            "spec_score_permille": 0,
            "calibration_state_permille": 0,
        },
        run_state_overrides={"process_metrics_state_rows": [previous_metrics]},
        drift_update_stride=1,
        force_drift_update=True,
    )
    end = dict(payload.get("end") or {})
    state = dict(payload.get("state") or {})
    if str(end.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process run end failed for critical fixture"}
    if str(state.get("current_drift_band", "")).strip() != "drift.critical":
        return {"status": "fail", "message": "expected drift.critical band"}
    if not bool(state.get("process_capsule_forced_invalid", False)):
        return {"status": "fail", "message": "critical drift must force capsule invalidation"}
    invalidation_rows = [
        dict(row)
        for row in list(state.get("process_capsule_invalidation_rows") or [])
        if isinstance(row, dict)
    ]
    if not invalidation_rows:
        return {"status": "fail", "message": "critical drift should log capsule invalidation row"}
    action_tokens = set(
        str(row.get("action_taken", "")).strip()
        for row in list(state.get("drift_event_record_rows") or [])
        if isinstance(row, dict)
    )
    if "capsule_invalidate" not in action_tokens:
        return {"status": "fail", "message": "critical drift event stream missing capsule_invalidate action"}
    return {"status": "pass", "message": "critical drift invalidates process capsules deterministically"}

