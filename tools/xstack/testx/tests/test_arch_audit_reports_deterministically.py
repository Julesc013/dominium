"""FAST test: ARCH-AUDIT report output is deterministic."""

from __future__ import annotations


TEST_ID = "test_arch_audit_reports_deterministically"
TEST_TAGS = ["fast", "audit", "architecture"]


def run(repo_root: str):
    from tools.audit.arch_audit_common import run_arch_audit

    first = run_arch_audit(repo_root)
    second = run_arch_audit(repo_root)
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "ARCH-AUDIT deterministic_fingerprint diverged"}
    if dict(first) != dict(second):
        return {"status": "fail", "message": "ARCH-AUDIT report payload diverged between identical runs"}
    return {"status": "pass", "message": "ARCH-AUDIT report is deterministic"}
