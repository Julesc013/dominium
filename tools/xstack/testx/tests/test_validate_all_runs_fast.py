"""FAST test: unified validation runs clean under FAST profile."""

from __future__ import annotations


TEST_ID = "test_validate_all_runs_fast"
TEST_TAGS = ["fast", "validation", "unify"]


def run(repo_root: str):
    from tools.xstack.testx.tests.validation_unify_testlib import build_report

    report = build_report(repo_root, "FAST")
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "validate --all FAST did not complete cleanly"}
    if int(dict(report.get("metrics") or {}).get("suite_count", 0) or 0) < 9:
        return {"status": "fail", "message": "validate --all FAST did not run the expected suite count"}
    return {"status": "pass", "message": "validate --all FAST completed cleanly"}
