"""FAST test: PROC-9 capsule executions are recorded canonically."""

from __future__ import annotations

import sys


TEST_ID = "test_capsule_exec_logged_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "capsule", "logging"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(repo_root=repo_root, seed=99111)
    report = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(report.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "PROC-9 stress run did not pass"}

    metrics = dict(report.get("metrics") or {})
    state = dict((dict(report.get("extensions") or {})).get("final_state_snapshot") or {})
    capsule_rows = list(state.get("capsule_execution_record_rows") or [])
    expected = int(metrics.get("capsule_execution_count", 0) or 0)
    observed = len([row for row in capsule_rows if isinstance(row, dict)])
    if expected != observed:
        return {
            "status": "fail",
            "message": "capsule execution count mismatch (metrics={}, rows={})".format(expected, observed),
        }
    return {"status": "pass", "message": "PROC-9 capsule execution logging verified"}
