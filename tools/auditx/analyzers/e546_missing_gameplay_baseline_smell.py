"""E546 missing gameplay baseline smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_gameplay_loop


ANALYZER_ID = "E546_MISSING_GAMEPLAY_BASELINE_SMELL"
TARGET_CATEGORIES = {"gameplay_loop.required_surface", "gameplay_loop.snapshot_fingerprint"}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_gameplay_loop(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() not in TARGET_CATEGORIES:
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="gameplay_loop.missing_baseline_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "required gameplay baseline surface missing",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MVP-GAMEPLAY-HARNESS-REQUIRED"],
                related_paths=[rel_path],
            )
        )
    return findings
