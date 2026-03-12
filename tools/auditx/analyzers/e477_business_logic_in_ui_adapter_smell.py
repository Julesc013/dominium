"""E477 business logic in UI adapter smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.ui_reconcile_common import ui_reconcile_violations


ANALYZER_ID = "E477_BUSINESS_LOGIC_IN_UI_ADAPTER_SMELL"
TARGET_CODES = {"ui_adapter_business_logic", "native_adapter_not_command_only", "ui_missing_shared_model"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ui_reconcile_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in TARGET_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui.business_logic_in_adapter_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    "code={}".format(code),
                    str(item.get("message", "")).strip() or "governed UI adapter contains business logic or bypassed shared binding",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="MOVE_LOGIC_TO_COMMAND_OR_VIEW_MODEL",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-UI-ADAPTERS-COMMAND-ONLY"],
                related_paths=[rel_path],
            )
        )
    return findings

