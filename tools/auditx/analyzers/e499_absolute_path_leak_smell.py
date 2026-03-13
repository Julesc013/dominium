"""E499 absolute path leak in distribution bundle smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.dist_verify_common import distribution_verify_violations


ANALYZER_ID = "E499_ABSOLUTE_PATH_LEAK_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in distribution_verify_violations(repo_root, platform_tag="win64"):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != "INV-NO-ABSOLUTE-PATHS-IN-DIST":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.absolute_path_leak_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "absolute path leak found in distribution",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_ABSOLUTE_PATH_FROM_DISTRIBUTION_ARTIFACT",
                related_invariants=["INV-NO-ABSOLUTE-PATHS-IN-DIST"],
                related_paths=[rel_path or "dist/v0.0.0-mock/win64/dominium", "docs/release/DIST_VERIFICATION_RULES.md"],
            )
        )
    return findings
