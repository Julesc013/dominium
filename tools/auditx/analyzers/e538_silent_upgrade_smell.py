"""E538 silent upgrade smell analyzer for RELEASE-INDEX-POLICY-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_index_policy_common import RULE_POLICY_DECLARED, release_index_policy_violations


ANALYZER_ID = "E538_SILENT_UPGRADE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_index_policy_violations(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        rule_id = str(item.get("rule_id", "")).strip()
        code = str(item.get("code", "")).strip()
        if rule_id != RULE_POLICY_DECLARED and code != "missing_integration_hook":
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.silent_upgrade_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path or "tools/setup/setup_cli.py",
                evidence=[
                    code or "silent_upgrade_risk",
                    str(item.get("message", "")).strip() or "release-index policy integration is incomplete and may allow silent upgrade behavior",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_INSTALL_AND_UPDATE_SELECTION_THROUGH_THE_DECLARED_RELEASE_RESOLUTION_POLICY_WITH_EXPLICIT_EXPLANATIONS",
                related_invariants=[RULE_POLICY_DECLARED],
                related_paths=[
                    rel_path or "tools/setup/setup_cli.py",
                    "tools/release/release_index_policy_common.py",
                    "docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md",
                ],
            )
        )
    return findings
