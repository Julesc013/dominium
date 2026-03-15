"""FAST test: convergence gate stops at the first failing step."""

from __future__ import annotations


TEST_ID = "test_failure_stops_immediately"
TEST_TAGS = ["fast", "convergence", "release", "failure"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_gate_testlib import build_report

    report = build_report(
        repo_root,
        selected_step_ids=["meta_stability", "time_anchor", "arch_audit"],
        force_fail_step_id="time_anchor",
        out_root_rel="build/tmp/testx_convergence_gate_failure",
    )
    if str(report.get("result", "")).strip() == "complete":
        return {"status": "fail", "message": "forced convergence failure did not stop the gate"}
    steps = list(report.get("steps") or [])
    if len(steps) != 2:
        return {"status": "fail", "message": "convergence gate did not stop immediately after the forced failure"}
    if str(dict(steps[-1]).get("step_id", "")).strip() != "time_anchor":
        return {"status": "fail", "message": "convergence gate stopped on the wrong step"}
    if str(report.get("stopped_at_step_id", "")).strip() != "time_anchor":
        return {"status": "fail", "message": "convergence gate did not record stopped_at_step_id correctly"}
    return {"status": "pass", "message": "convergence gate stops immediately on failure"}
