"""FAST test: unified validation runs clean under STRICT profile."""

from __future__ import annotations


TEST_ID = "test_validate_all_runs_strict"
TEST_TAGS = ["fast", "validation", "unify", "strict"]


def run(repo_root: str):
    from tools.xstack.testx.tests.validation_unify_testlib import build_report

    report = build_report(repo_root, "STRICT")
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "validate --all STRICT did not complete cleanly"}
    if str(report.get("profile", "")).strip() != "STRICT":
        return {"status": "fail", "message": "validate --all STRICT returned the wrong profile"}
    return {"status": "pass", "message": "validate --all STRICT completed cleanly"}
