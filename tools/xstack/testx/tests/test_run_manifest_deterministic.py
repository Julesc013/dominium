"""FAST test: APPSHELL-6 run manifest remains deterministic for the same run spec."""

from __future__ import annotations


TEST_ID = "test_run_manifest_deterministic"
TEST_TAGS = ["fast", "appshell", "supervisor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import build_run_spec

    first = build_run_spec(repo_root, seed="seed.appshell6.manifest")
    second = build_run_spec(repo_root, seed="seed.appshell6.manifest")
    first_manifest = dict(first.get("run_manifest") or {})
    second_manifest = dict(second.get("run_manifest") or {})
    if first_manifest != second_manifest:
        return {"status": "fail", "message": "run manifest drifted across repeated builds"}
    return {"status": "pass", "message": "run manifest remains deterministic"}
