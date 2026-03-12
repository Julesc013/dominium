"""E454 renderer-truth-leak smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_renderer_truth_access


ANALYZER_ID = "E454_RENDERER_TRUTH_LEAK_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = scan_renderer_truth_access(repo_root)
    for row in list(report.get("blocking_findings") or []):
        finding = dict(row or {})
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        message = str(finding.get("message", "")).strip() or "renderer truth leak detected"
        evidence = [message]
        snippet = str(finding.get("snippet", "")).strip()
        if snippet:
            evidence.append(snippet[:200])
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="arch.renderer_truth_leak_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                line=int(finding.get("line", 0) or 0),
                evidence=evidence,
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-PRESENTATION-IN-TRUTH", "INV-ARCH-AUDIT-MUST-PASS-BEFORE-RELEASE"],
                related_paths=[rel_path],
            )
        )
    return findings
