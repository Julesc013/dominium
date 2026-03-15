"""E513 unsupported target in release index smell analyzer for ARCH-MATRIX-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.arch_matrix_common import arch_matrix_violations


ANALYZER_ID = "E513_UNSUPPORTED_TARGET_IN_RELEASE_INDEX_SMELL"
_RULE_IDS = {"INV-TARGET-MATRIX-DECLARED", "INV-TIER3-NOT-IN-DEFAULT-RELEASE_INDEX"}
_CODES = {"release_index_target_unmapped", "tier3_target_in_release_index"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in arch_matrix_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        rule_id = str(item.get("rule_id", "")).strip()
        if code not in _CODES and rule_id not in _RULE_IDS:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.unsupported_target_in_release_index_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/audit/arch_matrix_report.json",
                evidence=[
                    code or "unsupported_target_in_release_index",
                    str(item.get("message", "")).strip()
                    or "release index row is not mapped to a declared target or includes a forbidden Tier 3 target",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGENERATE_RELEASE_INDEX_FROM_TARGET_MATRIX",
                related_invariants=sorted(_RULE_IDS),
                related_paths=[
                    rel_path or "data/audit/arch_matrix_report.json",
                    "tools/release/arch_matrix_common.py",
                    "docs/release/TARGET_MATRIX_v0_0_0_mock.md",
                ],
            )
        )
    return findings
