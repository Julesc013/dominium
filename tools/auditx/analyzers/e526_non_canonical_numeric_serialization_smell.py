"""E526 non-canonical numeric serialization smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_noncanonical_numeric_serialization


ANALYZER_ID = "E526_NON_CANONICAL_NUMERIC_SERIALIZATION_SMELL"
RULE_ID = "INV-CANONICAL-NUMERIC-SERIALIZATION"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_noncanonical_numeric_serialization(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.non_canonical_numeric_serialization_smell",
                severity="RISK",
                confidence=0.95,
                file_path=str(finding.get("path", "")).strip(),
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "non-canonical numeric serialization detected",
                    str(finding.get("snippet", "")).strip()[:140],
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[str(finding.get("path", "")).strip()],
            )
        )
    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
