"""FAST test: strict trust refuses unsigned update artifacts."""

from __future__ import annotations


TEST_ID = "test_strict_trust_refuses_unsigned"
TEST_TAGS = ["fast", "security", "trust", "update", "omega"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_sim_testlib import build_report

    report = build_report(repo_root, suffix="strict_trust_refuses_unsigned")
    scenario = dict(report.get("strict_trust_refusal") or {})
    if str(scenario.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "strict trust scenario must complete"}
    if str(scenario.get("refusal_code", "")).strip() != "refusal.trust.signature_missing":
        return {"status": "fail", "message": "strict trust scenario must refuse unsigned artifacts with the expected code"}
    return {"status": "pass", "message": "strict trust refuses unsigned update artifacts"}
