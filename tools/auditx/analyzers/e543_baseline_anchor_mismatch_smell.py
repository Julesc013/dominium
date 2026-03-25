"""E543 baseline proof-anchor mismatch smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_baseline_universe


ANALYZER_ID = "E543_BASELINE_ANCHOR_MISMATCH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_baseline_universe(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() != "baseline_universe.anchor_mismatch":
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="baseline_universe.anchor_mismatch_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "baseline universe proof anchor mismatch detected",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-BASELINE-ANCHORS-MATCH", "INV-BASELINE-UNIVERSE-REQUIRED"],
                related_paths=[rel_path],
            )
        )
    return findings
