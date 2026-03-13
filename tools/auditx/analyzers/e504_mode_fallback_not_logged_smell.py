"""E504 mode fallback logging smell analyzer for DIST-4."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.dist_platform_matrix_common import platform_matrix_violations


ANALYZER_ID = "E504_MODE_FALLBACK_NOT_LOGGED_SMELL"
_RELEVANT_CODES = {"mode_fallback_not_logged", "fallback_chain_mismatch"}


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
                category="dist.mode_fallback_not_logged_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path or "data/audit/dist_platform_matrix.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "forced fallback mode drifted or failed to emit the required degrade event",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ENSURE_APPSHELL_MODE_DEGRADED_EVENT_IS_EMITTED_FOR_FORCED_FALLBACKS",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-DIST-PLATFORM-MATRIX-MUST-EXIST"],
                related_paths=[rel_path or "data/audit/dist_platform_matrix.json", "tools/dist/dist_platform_matrix_common.py"],
            )
        )
    return findings
