"""E503 platform capability mismatch smell analyzer for DIST-4."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.dist.dist_platform_matrix_common import platform_matrix_violations


ANALYZER_ID = "E503_PLATFORM_CAPABILITIES_MISMATCH_SMELL"
_RELEVANT_CODES = {"platform_capabilities_mismatch"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in platform_matrix_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in _RELEVANT_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist.platform_capabilities_mismatch_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "contracts/audit/dist_platform_matrix.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "descriptor platform capability claims drifted from the canonical probe",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGENERATE_BUNDLE_AND_REALIGN_PLATFORM_CAPABILITY_CLAIMS",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-DIST-PLATFORM-MATRIX-MUST-EXIST"],
                related_paths=[rel_path or "contracts/audit/dist_platform_matrix.json", "tools/release/dist/dist_platform_matrix_common.py"],
            )
        )
    return findings
