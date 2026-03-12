"""E478 truth leak in UI smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.ui_reconcile_common import ui_reconcile_violations


ANALYZER_ID = "E478_TRUTH_LEAK_IN_UI_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ui_reconcile_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "ui_truth_leak":
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui.truth_leak_in_ui_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=[str(item.get("message", "")).strip() or "governed UI surface reads truth directly"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_TRUTH_DEPENDENCY",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-NO-TRUTH-READ-IN-UI"],
                related_paths=[rel_path],
            )
        )
    return findings
