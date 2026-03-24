"""E541 worldgen unnamed-RNG smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_worldgen_lock


ANALYZER_ID = "E541_WORLDGEN_UNNAMED_RNG_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_worldgen_lock(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() != "worldgen_lock.unnamed_rng":
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.unnamed_rng_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "unnamed RNG detected in worldgen truth path",
                    str(finding.get("snippet", "")).strip()[:160],
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNNAMED-RNG", "INV-WORLDGEN-LOCK-REQUIRED"],
                related_paths=[rel_path],
            )
        )
    return findings
