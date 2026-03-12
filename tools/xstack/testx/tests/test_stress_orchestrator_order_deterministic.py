"""FAST test: MVP stress orchestrator order is deterministic."""

from __future__ import annotations


TEST_ID = "test_stress_orchestrator_order_deterministic"
TEST_TAGS = ["fast", "mvp", "stress", "orchestrator"]


def run(repo_root: str):
    from tools.mvp.stress_gate_common import GATE_SUITE_ORDER
    from tools.xstack.testx.tests.mvp_stress_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    suite_order = [str(item) for item in list(report.get("suite_order") or [])]
    if suite_order != list(GATE_SUITE_ORDER):
        return {"status": "fail", "message": "MVP stress suite order drifted"}
    suite_results = [str(dict(item).get("suite_id", "")).strip() for item in list(report.get("suite_results") or [])]
    if suite_results != list(GATE_SUITE_ORDER):
        return {"status": "fail", "message": "MVP stress suite result order drifted"}
    if not bool(dict(report.get("assertions") or {}).get("suite_order_deterministic", False)):
        return {"status": "fail", "message": "MVP stress report did not record suite_order_deterministic=true"}
    return {"status": "pass", "message": "MVP stress orchestrator order is deterministic"}
