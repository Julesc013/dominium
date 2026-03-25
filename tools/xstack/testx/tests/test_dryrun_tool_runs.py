"""FAST test: Ω-10 dry-run tool executes and reports a complete gate."""

from __future__ import annotations


TEST_ID = "test_dryrun_tool_runs"
TEST_TAGS = ["fast", "omega", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist_final_testlib import run_dryrun_tool

    proc, payload = run_dryrun_tool(repo_root)
    if int(proc.returncode) != 0:
        return {"status": "fail", "message": "Ω-10 dry-run tool failed: {}".format((proc.stdout or "").strip()[:200])}
    if str(payload.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "Ω-10 dry-run result must be complete"}
    missing_count = payload.get("missing_count", -1)
    artifact_issue_count = payload.get("artifact_issue_count", -1)
    if int(missing_count) != 0:
        return {"status": "fail", "message": "Ω-10 dry-run missing_count must be zero"}
    if int(artifact_issue_count) != 0:
        return {"status": "fail", "message": "Ω-10 dry-run artifact_issue_count must be zero"}
    return {"status": "pass", "message": "Ω-10 dry-run tool executes and reports a complete gate"}
