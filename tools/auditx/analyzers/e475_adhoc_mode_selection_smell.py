"""E475 ad hoc mode selection smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.ui_mode_resolution_common import ui_mode_resolution_violations


ANALYZER_ID = "E475_AD_HOC_MODE_SELECTION_SMELL"
TARGET_CODES = {"ad_hoc_mode_selection"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ui_mode_resolution_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() not in TARGET_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.ad_hoc_mode_selection_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=[str(item.get("message", "")).strip() or "mode selection bypasses the governed AppShell selector"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CENTRALIZE_MODE_SELECTION",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-UI-MODE-SELECTOR-SINGLE"],
                related_paths=[rel_path],
            )
        )
    return findings
