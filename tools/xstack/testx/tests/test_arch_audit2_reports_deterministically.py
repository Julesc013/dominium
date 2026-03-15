"""FAST test: ARCH-AUDIT-2 report is deterministic across repeated runs."""

from __future__ import annotations


TEST_ID = "test_arch_audit2_reports_deterministically"
TEST_TAGS = ["fast", "audit", "architecture", "determinism"]


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_json_text
    from tools.xstack.testx.tests.arch_audit2_testlib import build_report

    first = build_report(repo_root)
    second = build_report(repo_root)
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "ARCH-AUDIT-2 fingerprint drifted across repeated runs"}
    if canonical_json_text(first) != canonical_json_text(second):
        return {"status": "fail", "message": "ARCH-AUDIT-2 canonical JSON drifted across repeated runs"}
    return {"status": "pass", "message": "ARCH-AUDIT-2 report is deterministic"}
