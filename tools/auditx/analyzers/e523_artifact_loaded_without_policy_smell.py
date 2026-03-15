"""E523 artifact loaded without policy smell analyzer for MIGRATION-LIFECYCLE-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.compat.migration_lifecycle_common import RULE_POLICY, migration_lifecycle_violations


ANALYZER_ID = "E523_ARTIFACT_LOADED_WITHOUT_POLICY_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in migration_lifecycle_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_POLICY:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.artifact_loaded_without_policy_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "src/compat/migration_lifecycle.py",
                evidence=[
                    str(item.get("code", "")).strip() or "artifact_without_policy",
                    str(item.get("message", "")).strip() or "artifact lifecycle handling drifted outside a declared migration policy",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DECLARE_AND_ENFORCE_MIGRATION_POLICY_BEFORE_LOADING_OR_MUTATING_ARTIFACTS",
                related_invariants=[RULE_POLICY],
                related_paths=[
                    rel_path or "src/compat/migration_lifecycle.py",
                    "tools/compat/migration_lifecycle_common.py",
                ],
            )
        )
    return findings
