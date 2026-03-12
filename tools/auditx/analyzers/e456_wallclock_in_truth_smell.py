"""E456 wallclock-in-truth smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_determinism


ANALYZER_ID = "E456_WALLCLOCK_IN_TRUTH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = scan_determinism(repo_root)
    for row in list(report.get("blocking_findings") or []):
        finding = dict(row or {})
        if str(finding.get("category", "")).strip() != "determinism.wallclock":
            continue
        rel_path = str(finding.get("path", "")).replace("\\", "/")
        message = str(finding.get("message", "")).strip() or "wallclock usage detected in a truth path"
        evidence = [message]
        snippet = str(finding.get("snippet", "")).strip()
        if snippet:
            evidence.append(snippet[:200])
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="arch.wallclock_in_truth_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                line=int(finding.get("line", 0) or 0),
                evidence=evidence,
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-ARCH-AUDIT-MUST-PASS-BEFORE-RELEASE"],
                related_paths=[rel_path],
            )
        )
    return findings
