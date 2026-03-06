"""FAST test: PROC-6 revalidation success resets drift state and forced invalidation."""

from __future__ import annotations

import sys


TEST_ID = "test_revalidation_resets_on_success"
TEST_TAGS = ["fast", "proc", "proc6", "drift", "revalidation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.drift import build_process_drift_state_row, build_revalidation_run_row
    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    preloaded_drift = build_process_drift_state_row(
        process_id="proc.test.proc3.qc",
        version="1.0.0",
        drift_score=820,
        drift_band="drift.critical",
        last_update_tick=200,
        extensions={"source": "test.proc6"},
    )
    preloaded_revalidation = build_revalidation_run_row(
        revalidation_id="",
        process_id="proc.test.proc3.qc",
        version="1.0.0",
        trial_index=1,
        scheduled_tick=200,
        status="scheduled",
        extensions={"source": "test.proc6"},
    )
    payload = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc6.revalidation_reset",
        qc_policy_id="qc.none",
        run_state_overrides={
            "process_drift_state_rows": [preloaded_drift],
            "revalidation_run_rows": [preloaded_revalidation],
            "process_capsule_forced_invalid": True,
            "base_qc_policy_id": "qc.basic_sampling",
            "qc_policy_id": "qc.strict_sampling",
        },
        drift_update_stride=999,
        force_drift_update=False,
    )
    end = dict(payload.get("end") or {})
    state = dict(payload.get("state") or {})
    if str(end.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process run end failed for revalidation fixture"}
    if bool(state.get("process_capsule_forced_invalid", True)):
        return {"status": "fail", "message": "revalidation success should clear forced invalid flag"}

    drift_rows = [
        dict(row)
        for row in list(state.get("process_drift_state_rows") or [])
        if isinstance(row, dict)
    ]
    if not drift_rows:
        return {"status": "fail", "message": "missing drift state rows after revalidation"}
    latest = drift_rows[-1]
    if str(latest.get("drift_band", "")).strip() != "drift.normal":
        return {"status": "fail", "message": "revalidation success should reset drift band to normal"}
    if int(latest.get("drift_score", -1)) != 0:
        return {"status": "fail", "message": "revalidation success should reset drift score to zero"}
    if str(state.get("qc_policy_id", "")).strip() != "qc.basic_sampling":
        return {"status": "fail", "message": "revalidation success should restore base QC policy"}
    return {"status": "pass", "message": "revalidation success resets drift and capsule invalidation state"}

