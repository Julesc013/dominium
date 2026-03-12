"""FAST test: MVP smoke harness report is present and complete."""

from __future__ import annotations


TEST_ID = "test_smoke_harness_passes"
TEST_TAGS = ["fast", "mvp", "smoke", "harness"]


def run(repo_root: str):
    from tools.xstack.testx.tests.mvp_smoke_testlib import load_complete_report

    report, error = load_complete_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    assertions = dict(report.get("assertions") or {})
    failed = sorted(key for key, value in assertions.items() if not bool(value))
    if failed:
        return {"status": "fail", "message": "MVP smoke assertions failed: {}".format(", ".join(failed))}
    return {"status": "pass", "message": "MVP smoke harness report is complete with all assertions passing"}
