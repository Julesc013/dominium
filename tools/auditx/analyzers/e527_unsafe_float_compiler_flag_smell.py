"""E527 unsafe float compiler flag smell analyzer."""

from __future__ import annotations

from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_compiler_flags


ANALYZER_ID = "E527_UNSAFE_FLOAT_COMPILER_FLAG_SMELL"
RULE_ID = "INV-SAFE-FLOAT-COMPILER-FLAGS"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    report = scan_compiler_flags(repo_root)
    for row in list(dict(report or {}).get("blocking_findings") or []):
        finding = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="build.unsafe_float_compiler_flag_smell",
                severity="RISK",
                confidence=0.97,
                file_path=str(finding.get("path", "")).strip(),
                line=int(finding.get("line", 1) or 1),
                evidence=[
                    str(finding.get("message", "")).strip() or "unsafe float compiler flag detected",
                    str(finding.get("snippet", "")).strip()[:140],
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[str(finding.get("path", "")).strip()],
            )
        )
    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
