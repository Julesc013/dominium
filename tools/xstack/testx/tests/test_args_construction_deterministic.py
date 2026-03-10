"""FAST test: APPSHELL-6 launcher args construction stays deterministic."""

from __future__ import annotations


TEST_ID = "test_args_construction_deterministic"
TEST_TAGS = ["fast", "appshell", "supervisor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import build_run_spec

    first = build_run_spec(repo_root, seed="seed.appshell6.args")
    second = build_run_spec(repo_root, seed="seed.appshell6.args")
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor run spec build refused"}
    first_rows = list(first.get("processes") or [])
    second_rows = list(second.get("processes") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "supervisor child arg rows drifted across repeated builds"}
    return {"status": "pass", "message": "supervisor child args remain deterministic"}
