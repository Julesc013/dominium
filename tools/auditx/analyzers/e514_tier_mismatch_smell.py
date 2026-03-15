"""E514 tier mismatch smell analyzer for ARCH-MATRIX-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.arch_matrix_common import build_arch_matrix_report


ANALYZER_ID = "E514_TIER_MISMATCH_SMELL"
_RULE_ID = "INV-TIER1-MUST-PASS-ALL-GATES"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    report = dict(build_arch_matrix_report(repo_root) or {})
    findings = []
    for row in list(report.get("tier1_gate_rows") or []):
        item = dict(row or {})
        if str(item.get("result", "")).strip() == "complete":
            continue
        target_id = str(item.get("target_id", "")).strip()
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.tier_mismatch_smell",
                severity="RISK",
                confidence=0.99,
                file_path="docs/audit/ARCH_MATRIX_FINAL.md",
                evidence=[
                    target_id or "tier1_target_gate_incomplete",
                    "convergence={}; clean_room={}; dist4={}; dist4_platform_passed={}".format(
                        str(item.get("convergence_result", "")).strip(),
                        str(item.get("clean_room_result", "")).strip(),
                        str(item.get("dist4_result", "")).strip(),
                        str(item.get("dist4_platform_passed", "")).strip(),
                    ),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RUN_TIER1_GATE_CHAIN_AND_FIX_MISMATCH",
                related_invariants=[_RULE_ID],
                related_paths=[
                    "docs/audit/ARCH_MATRIX_FINAL.md",
                    "data/audit/arch_matrix_report.json",
                    "tools/release/arch_matrix_common.py",
                ],
            )
        )
    return findings
