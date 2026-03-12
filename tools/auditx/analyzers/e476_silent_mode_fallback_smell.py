"""E476 silent mode fallback smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.ui_mode_resolution_common import ui_mode_resolution_violations


ANALYZER_ID = "E476_SILENT_MODE_FALLBACK_SMELL"
TARGET_CODES = {"mode_not_logged", "degrade_not_logged", "silent_mode_fallback"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ui_mode_resolution_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in TARGET_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.silent_mode_fallback_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=["code={}".format(code), str(item.get("message", "")).strip() or "mode fallback is not surfaced explicitly"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="LOG_MODE_SELECTION",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-FALLBACK-DETERMINISTIC"],
                related_paths=[rel_path],
            )
        )
    return findings
