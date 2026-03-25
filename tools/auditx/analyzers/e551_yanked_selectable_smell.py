"""E551 yanked selectable smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_ecosystem_verify, scan_update_sim


ANALYZER_ID = "E551_YANKED_SELECTABLE_SMELL"
TARGET_CATEGORIES = {"ecosystem_verify.yanked_selectable", "update_sim.yanked_selectable"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    for report in (scan_ecosystem_verify(repo_root), scan_update_sim(repo_root)):
        for row in list(dict(report or {}).get("blocking_findings") or []):
            finding = dict(row or {})
            category = str(finding.get("category", "")).strip()
            if category not in TARGET_CATEGORIES:
                continue
            rel_path = str(finding.get("path", "")).replace("\\", "/")
            related_invariant = "INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST" if category.startswith("update_sim.") else "INV-ECOSYSTEM-VERIFY-MUST-PASS-BEFORE-DIST"
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="update_sim.yanked_selectable_smell" if category.startswith("update_sim.") else "ecosystem_verify.yanked_selectable_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    line=int(finding.get("line", 1) or 1),
                    evidence=[
                        str(finding.get("message", "")).strip() or "latest-compatible selection still allows a yanked candidate",
                        str(finding.get("snippet", "")).strip()[:160],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="RESTORE_YANKED_EXCLUSION_FOR_LATEST_COMPATIBLE_SELECTION_AND_RECORD_THE_SKIP_DETERMINISTICALLY",
                    related_invariants=[related_invariant],
                    related_paths=[rel_path],
                )
            )
    return findings
