"""FAST test: MVP stress regression baseline matches the current stress artifacts."""

from __future__ import annotations


TEST_ID = "test_stress_hashes_match_baseline"
TEST_TAGS = ["fast", "mvp", "stress", "baseline"]


def run(repo_root: str):
    from tools.mvp.stress_gate_common import build_mvp_stress_baseline
    from tools.xstack.testx.tests.mvp_stress_testlib import first_mismatch, load_baseline, load_proof_report, load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    proof_report, error = load_proof_report(repo_root, report=report)
    if error:
        return {"status": "fail", "message": error}
    baseline = load_baseline(repo_root)
    if not baseline:
        return {"status": "fail", "message": "missing MVP stress regression baseline"}
    expected_baseline = build_mvp_stress_baseline(report, proof_report)
    mismatch = first_mismatch(expected_baseline, baseline)
    if mismatch:
        return {"status": "fail", "message": "MVP stress baseline drifted: {}".format(mismatch)}
    return {"status": "pass", "message": "MVP stress regression baseline matches the current stress artifacts"}
