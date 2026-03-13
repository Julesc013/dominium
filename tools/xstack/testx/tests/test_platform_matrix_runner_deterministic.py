"""FAST test: DIST-4 platform matrix runner is deterministic for identical inputs."""

from __future__ import annotations


TEST_ID = "test_platform_matrix_runner_deterministic"
TEST_TAGS = ["fast", "dist", "release", "platform", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist4_testlib import build_report

    first = build_report(repo_root)
    second = build_report(repo_root)
    if first != second:
        return {"status": "fail", "message": "DIST-4 platform matrix report drifted across repeated identical runs"}
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-4 platform matrix report did not complete successfully"}
    return {"status": "pass", "message": "DIST-4 platform matrix runner is deterministic"}
