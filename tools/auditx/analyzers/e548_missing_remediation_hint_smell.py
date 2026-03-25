"""E548 missing remediation hint smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_disaster_suite


ANALYZER_ID = "E548_MISSING_REMEDIATION_HINT_SMELL"
TARGET_CATEGORIES = {"disaster_suite.remediation_missing"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_disaster_suite(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="disaster_suite.missing_remediation_hint_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "refusal case missing remediation hint",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DISASTER-SUITE-MUST-PASS-BEFORE-DIST"],
                related_paths=[rel_path],
            )
        )
    return findings
