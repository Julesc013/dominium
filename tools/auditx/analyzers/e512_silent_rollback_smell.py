"""E512 silent-rollback smell analyzer for UPDATE-MODEL-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.update_model_common import update_model_violations


ANALYZER_ID = "E512_SILENT_ROLLBACK_SMELL"
_RULE_IDS = {
    "INV-ROLLBACK-REQUIRES-TRANSACTION-LOG",
    "INV-NO-SILENT-UPGRADE",
}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in update_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() not in _RULE_IDS:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.silent_rollback_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "tools/setup/setup_cli.py",
                evidence=[
                    str(item.get("code", "")).strip() or "silent_rollback",
                    str(item.get("message", "")).strip() or "rollback or upgrade lacks explicit transaction-log or remediation behavior",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RECORD_UPDATE_TRANSACTIONS_AND_EMIT_EXPLICIT_ROLLBACK_REMEDIATION",
                related_invariants=sorted(_RULE_IDS),
                related_paths=[rel_path or "tools/setup/setup_cli.py", "docs/release/SETUP_SELF_UPDATE.md"],
            )
        )
    return findings
