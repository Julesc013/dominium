"""FAST test: update simulation rollback restores the frozen baseline hash."""

from __future__ import annotations


TEST_ID = "test_rollback_restores_baseline"
TEST_TAGS = ["fast", "release", "rollback", "update", "omega"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_sim_testlib import build_report

    report = build_report(repo_root, suffix="rollback_restores_baseline")
    scenario = dict(report.get("rollback_restore") or {})
    if str(scenario.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "rollback scenario must complete"}
    if not bool(scenario.get("rollback_matches_baseline")):
        return {"status": "fail", "message": "rollback scenario did not restore the baseline component-set hash"}
    if str(scenario.get("restored_component_set_hash", "")).strip() != str(scenario.get("baseline_component_set_hash", "")).strip():
        return {"status": "fail", "message": "rollback restored hash does not match the baseline hash"}
    return {"status": "pass", "message": "rollback restores the frozen baseline hash"}
