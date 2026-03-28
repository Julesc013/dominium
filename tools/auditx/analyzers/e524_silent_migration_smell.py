"""E524 silent migration smell analyzer for MIGRATION-LIFECYCLE-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.compat.migration_lifecycle_common import RULE_READ_ONLY, RULE_SILENT, migration_lifecycle_violations


ANALYZER_ID = "E524_SILENT_MIGRATION_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    watched_rules = {RULE_SILENT, RULE_READ_ONLY}
    for row in migration_lifecycle_violations(repo_root):
        item = dict(row or {})
        rule_id = str(item.get("rule_id", "")).strip()
        if rule_id not in watched_rules:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.silent_migration_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "compat/migration_lifecycle.py",
                evidence=[
                    str(item.get("code", "")).strip() or "silent_migration_or_read_only_drift",
                    str(item.get("message", "")).strip() or "migration or read-only fallback path is not being logged and surfaced deterministically",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_ARTIFACT_LOADS_THROUGH_CANONICAL_DECISION_RECORDS_AND_EXPLICIT_READ_ONLY_LOGGING",
                related_invariants=[rule_id],
                related_paths=[
                    rel_path or "compat/migration_lifecycle.py",
                    "tools/compat/migration_lifecycle_common.py",
                ],
            )
        )
    return findings
