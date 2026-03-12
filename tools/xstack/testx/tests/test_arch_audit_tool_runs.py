"""FAST test: ARCH-AUDIT tool runs and yields a clean blocking status."""

from __future__ import annotations


TEST_ID = "test_arch_audit_tool_runs"
TEST_TAGS = ["fast", "audit", "architecture"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_audit_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    if int(report.get("blocking_finding_count", 0) or 0) != 0:
        return {"status": "fail", "message": "ARCH-AUDIT report contains blocking findings"}
    return {"status": "pass", "message": "ARCH-AUDIT report completed without blocking findings"}
