"""FAST test: ARCH-AUDIT-2 catches trust-bypass fixtures."""

from __future__ import annotations


TEST_ID = "test_arch_audit2_detects_trust_bypass"
TEST_TAGS = ["fast", "audit", "architecture", "security", "fixtures"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_audit2_testlib import trust_bypass_scan

    report = trust_bypass_scan(repo_root)
    if int(report.get("blocking_finding_count", 0) or 0) < 1:
        return {"status": "fail", "message": "ARCH-AUDIT-2 did not detect the trust-bypass fixture"}
    return {"status": "pass", "message": "ARCH-AUDIT-2 detects trust bypass paths"}
