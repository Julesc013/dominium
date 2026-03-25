"""E544 baseline pack-lock drift smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_baseline_universe


ANALYZER_ID = "E544_BASELINE_PACK_LOCK_DRIFT_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_baseline_universe(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() != "baseline_universe.pack_lock_drift":
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="baseline_universe.pack_lock_drift_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "baseline universe pack lock drift detected",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-BASELINE-UNIVERSE-REQUIRED"],
                related_paths=[rel_path],
            )
        )
    return findings
