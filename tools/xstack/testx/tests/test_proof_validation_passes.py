"""FAST test: MVP stress proof validation passes."""

from __future__ import annotations


TEST_ID = "test_proof_validation_passes"
TEST_TAGS = ["fast", "mvp", "stress", "proof"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_stress_testlib import load_proof_report, load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    proof_report, error = load_proof_report(repo_root, report=report)
    if error:
        return {"status": "fail", "message": error}
    checks = dict(proof_report.get("checks") or {})
    failed = sorted(key for key, value in checks.items() if not bool(value))
    if failed:
        return {"status": "fail", "message": "MVP stress proof checks failed: {}".format(", ".join(failed))}
    return {"status": "pass", "message": "MVP stress proof validation passes"}
