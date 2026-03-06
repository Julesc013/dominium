"""FAST test: PROC-9 drift warning/critical actions are logged."""

from __future__ import annotations

import sys


TEST_ID = "test_drift_actions_logged_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "drift", "logging"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(
        repo_root=repo_root,
        seed=99131,
        drifting_count=96,
        tick_horizon=48,
    )
    report = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(report.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "PROC-9 stress run did not pass"}

    metrics = dict(report.get("metrics") or {})
    state = dict((dict(report.get("extensions") or {})).get("final_state_snapshot") or {})
    drift_rows = [dict(row) for row in list(state.get("drift_event_record_rows") or []) if isinstance(row, dict)]
    warning_count = int(metrics.get("drift_warning_count", 0) or 0)
    critical_count = int(metrics.get("drift_critical_count", 0) or 0)
    if (warning_count + critical_count) <= 0:
        return {"status": "fail", "message": "drift metrics produced no warning/critical events"}
    if len(drift_rows) < (warning_count + critical_count):
        return {"status": "fail", "message": "drift event rows missing for warning/critical metrics"}
    return {"status": "pass", "message": "PROC-9 drift actions logged"}
