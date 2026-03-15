"""E519 tier policy violation smell analyzer for ARCH-AUDIT-2."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import build_arch_audit2_report, run_arch_audit


ANALYZER_ID = "E519_TIER_POLICY_VIOLATION_SMELL"
RULE_ID = "INV-TIER3-NOT-DOWNLOADABLE"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_arch_audit2_report(run_arch_audit(repo_root))
    for row in list(report.get("blocking_findings") or []):
        item = dict(row or {})
        if str(item.get("category", "")).strip() != "target_matrix":
            continue
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.tier_policy_violation_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "data/registries/target_matrix_registry.json",
                evidence=[
                    str(item.get("message", "")).strip() or "target-tier policy violation detected",
                    str(item.get("snippet", "")).strip() or "tier mismatch",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ALIGN_RELEASE_INDEX_AND_PLATFORM_CLAIMS_WITH_TARGET_MATRIX_TIER_POLICY",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "data/registries/target_matrix_registry.json", "tools/release/arch_matrix_common.py"],
            )
        )
    return findings
