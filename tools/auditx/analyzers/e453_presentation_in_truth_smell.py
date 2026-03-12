"""E453 presentation-in-truth smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_truth_purity


ANALYZER_ID = "E453_PRESENTATION_IN_TRUTH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = scan_truth_purity(repo_root)
    for row in list(report.get("blocking_findings") or []):
        finding = dict(row or {})
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        message = str(finding.get("message", "")).strip() or "presentation data leaked into canonical truth"
        evidence = [message]
        snippet = str(finding.get("snippet", "")).strip()
        if snippet:
            evidence.append(snippet[:200])
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="arch.presentation_in_truth_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                line=int(finding.get("line", 0) or 0),
                evidence=evidence,
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-PRESENTATION-IN-TRUTH"],
                related_paths=[rel_path],
            )
        )
    return findings
