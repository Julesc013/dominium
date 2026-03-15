"""E518 trust bypass smell analyzer for ARCH-AUDIT-2."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import build_arch_audit2_report, run_arch_audit


ANALYZER_ID = "E518_TRUST_BYPASS_SMELL"
RULE_ID = "INV-TRUST-VERIFY-NONBYPASS"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_arch_audit2_report(run_arch_audit(repo_root))
    for row in list(report.get("blocking_findings") or []):
        item = dict(row or {})
        if str(item.get("category", "")).strip() != "trust_bypass":
            continue
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="security.trust_bypass_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "src/security/trust/trust_verifier.py",
                evidence=[
                    str(item.get("message", "")).strip() or "trust verification bypass detected",
                    str(item.get("snippet", "")).strip() or "trust bypass token",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_ARTIFACT_ACCEPTANCE_THROUGH_TRUST_VERIFIER",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "src/security/trust/trust_verifier.py", "tools/security/trust_model_common.py"],
            )
        )
    return findings
