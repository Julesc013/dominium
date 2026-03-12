"""FAST test: MVP smoke regression baseline matches the current smoke report."""

from __future__ import annotations


TEST_ID = "test_smoke_hashes_match_baseline"
TEST_TAGS = ["fast", "mvp", "smoke", "baseline"]


def run(repo_root: str):
    from tools.mvp.mvp_smoke_common import build_mvp_smoke_baseline
    from tools.xstack.testx.tests.mvp_smoke_testlib import first_mismatch, load_baseline, load_complete_report

    report, error = load_complete_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    baseline = load_baseline(repo_root)
    if not baseline:
        return {"status": "fail", "message": "missing MVP smoke regression baseline"}
    expected_baseline = build_mvp_smoke_baseline(report)
    mismatch = first_mismatch(expected_baseline, baseline)
    if mismatch:
        return {"status": "fail", "message": "MVP smoke baseline drifted: {}".format(mismatch)}
    return {"status": "pass", "message": "MVP smoke regression baseline matches the current smoke report"}
