"""E525 float-in-truth namespace smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_float_in_truth


ANALYZER_ID = "E525_FLOAT_IN_TRUTH_NAMESPACE_SMELL"
RULE_ID = "INV-FLOAT-ONLY-IN-RENDER"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_float_in_truth(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.float_in_truth_namespace_smell",
                severity="RISK",
                confidence=0.95,
                file_path=str(finding.get("path", "")).strip(),
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "floating-point usage detected in governed truth-side numeric code",
                    str(finding.get("snippet", "")).strip()[:140],
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[str(finding.get("path", "")).strip()],
            )
        )
    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
