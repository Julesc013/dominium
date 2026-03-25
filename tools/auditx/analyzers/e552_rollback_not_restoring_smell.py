"""E552 rollback not restoring smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_update_sim


ANALYZER_ID = "E552_ROLLBACK_NOT_RESTORING_SMELL"
TARGET_CATEGORIES = {"update_sim.rollback_not_restoring"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_update_sim(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="update_sim.rollback_not_restoring_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "rollback did not restore the baseline component-set hash",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="RESTORE_DETERMINISTIC_ROLLBACK_SO_THE_BASELINE_COMPONENT_SET_HASH_MATCHES_AFTER_RECOVERY",
                related_invariants=["INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST"],
                related_paths=[rel_path],
            )
        )
    return findings
