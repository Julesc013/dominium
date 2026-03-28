"""E511 update-without-verification smell analyzer for UPDATE-MODEL-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.update_model_common import update_model_violations


ANALYZER_ID = "E511_UPDATE_WITHOUT_VERIFICATION_SMELL"
_RULE_IDS = {
    "INV-UPDATE-MUST-USE-COMPONENT-GRAPH",
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
                category="release.update_without_verification_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "tools/setup/setup_cli.py",
                evidence=[
                    str(item.get("code", "")).strip() or "update_without_verification",
                    str(item.get("message", "")).strip() or "update flow does not verify the release surface through the governed component graph",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_UPDATES_THROUGH_RELEASE_INDEX_AND_MANIFEST_VERIFICATION",
                related_invariants=sorted(_RULE_IDS),
                related_paths=[rel_path or "tools/setup/setup_cli.py", "release/update_resolver.py"],
            )
        )
    return findings
