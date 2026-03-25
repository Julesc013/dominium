"""E553 silent upgrade smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_update_sim


ANALYZER_ID = "E553_SILENT_UPGRADE_SMELL"
TARGET_CATEGORIES = {"update_sim.silent_upgrade"}


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
                category="update_sim.silent_upgrade_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "installed component set changed without an explicit upgrade delta",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REQUIRE_AN_EXPLICIT_UPDATE_DELTA_BEFORE_ANY_COMPONENT_SET_CHANGE_IS_ACCEPTED",
                related_invariants=["INV-UPDATE-SIM-MUST-PASS-BEFORE-DIST"],
                related_paths=[rel_path],
            )
        )
    return findings
