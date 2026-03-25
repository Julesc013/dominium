"""E558 toolchain report missing smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_toolchain_matrix


ANALYZER_ID = "E558_TOOLCHAIN_REPORT_MISSING_SMELL"
TARGET_CATEGORIES = {"toolchain_matrix.report_missing", "toolchain_matrix.required_surface"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_toolchain_matrix(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="toolchain_matrix.report_missing_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "toolchain matrix required report surface is missing",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="RESTORE_THE_TOOLCHAIN_MATRIX_REPORT_OR_REQUIRED_SUPPORT_SURFACE",
                related_invariants=["INV-TOOLCHAIN-MATRIX-REGISTRY-PRESENT"],
                related_paths=[rel_path],
            )
        )
    return findings
