"""E559 missing final dist plan smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_dist_final_plan


ANALYZER_ID = "E559_MISSING_FINAL_DIST_PLAN_SMELL"
TARGET_CATEGORIES = {"dist_final_plan.required_surface"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_dist_final_plan(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist_final_plan.missing_final_plan_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "final distribution plan support surface is missing",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="RESTORE_THE_FINAL_DIST_PLAN_SURFACES",
                related_invariants=["INV-DIST-FINAL-PLAN-PRESENT"],
                related_paths=[rel_path],
            )
        )
    return findings
