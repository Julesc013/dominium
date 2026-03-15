"""FAST test: ARCH-AUDIT-2 catches hardcoded component-set composition fixtures."""

from __future__ import annotations


TEST_ID = "test_arch_audit2_detects_hardcoded_bundle_list"
TEST_TAGS = ["fast", "audit", "architecture", "dist", "fixtures"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_audit2_testlib import hardcoded_bundle_scan

    report = hardcoded_bundle_scan(repo_root)
    if int(report.get("blocking_finding_count", 0) or 0) < 1:
        return {"status": "fail", "message": "ARCH-AUDIT-2 did not detect the hardcoded bundle-list fixture"}
    return {"status": "pass", "message": "ARCH-AUDIT-2 detects hardcoded bundle lists"}
