"""E539 yanked build selectable smell analyzer for RELEASE-INDEX-POLICY-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_index_policy_common import RULE_YANKED_EXCLUDED, release_index_policy_violations


ANALYZER_ID = "E539_YANKED_BUILD_SELECTABLE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_index_policy_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_YANKED_EXCLUDED:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.yanked_build_selectable_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "release/update_resolver.py",
                evidence=[
                    str(item.get("code", "")).strip() or "yanked_build_selectable",
                    str(item.get("message", "")).strip() or "latest-compatible selection still permits or hides yanked candidates",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="EXCLUDE_YANKED_COMPONENTS_FROM_LATEST_COMPATIBLE_SELECTION_AND_LOG_THE_SKIP_EXPLICITLY",
                related_invariants=[RULE_YANKED_EXCLUDED],
                related_paths=[
                    rel_path or "release/update_resolver.py",
                    "tools/release/release_index_policy_common.py",
                    "docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md",
                ],
            )
        )
    return findings
