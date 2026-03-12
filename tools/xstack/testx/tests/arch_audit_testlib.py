"""Helpers for ARCH-AUDIT-0 TestX coverage."""

from __future__ import annotations


def load_report(repo_root: str) -> tuple[dict, str]:
    from tools.audit.arch_audit_common import load_or_run_arch_audit_report, run_arch_audit, write_arch_audit_outputs

    report = load_or_run_arch_audit_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        report = run_arch_audit(repo_root)
        write_arch_audit_outputs(repo_root, report=report)
    if str(report.get("result", "")).strip() != "complete":
        return report, "ARCH-AUDIT report is not complete"
    if not str(report.get("deterministic_fingerprint", "")).strip():
        return report, "ARCH-AUDIT report is missing deterministic_fingerprint"
    return report, ""
