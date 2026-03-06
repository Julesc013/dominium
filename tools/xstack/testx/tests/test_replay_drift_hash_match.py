"""FAST test: PROC-6 drift replay verifier returns stable hash chains."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_replay_drift_hash_match"
TEST_TAGS = ["fast", "proc", "proc6", "drift", "replay"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.maturity.metrics_engine import build_process_metrics_state_row
    from tools.process.tool_replay_drift_window import verify_drift_replay_window
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
    first = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc6.replay",
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
    second = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc6.replay",
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
    if str((dict(first.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first drift replay fixture failed"}
    if str((dict(second.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second drift replay fixture failed"}

    report = verify_drift_replay_window(
        state_payload=dict(first.get("state") or {}),
        expected_payload=dict(second.get("state") or {}),
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "drift replay verifier reported violations: {}".format(
                report.get("violations", [])
            ),
        }
    for key in (
        "drift_state_hash_chain",
        "drift_event_hash_chain",
        "qc_policy_change_hash_chain",
        "revalidation_run_hash_chain",
    ):
        value = str((dict(report.get("observed") or {}).get(key, ""))).strip().lower()
        if not _HASH64.fullmatch(value):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "PROC-6 drift replay hashes are stable"}

