"""E536 missing archive record smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.archive_policy_common import RULE_ARCHIVE_RECORD, archive_policy_violations


ANALYZER_ID = "E536_MISSING_ARCHIVE_RECORD_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in archive_policy_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_ARCHIVE_RECORD:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.missing_archive_record_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "tools/release/tool_archive_release.py",
                evidence=[
                    str(item.get("code", "")).strip() or "archive_record_missing",
                    str(item.get("message", "")).strip() or "archive publication policy is missing a required archive record or offline verification hook",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="GENERATE_ARCHIVE_RECORD_AND_ARCHIVE_POLICY_BASELINE_FOR_PUBLISHED_RELEASES",
                related_invariants=[RULE_ARCHIVE_RECORD],
                related_paths=[
                    rel_path or "tools/release/tool_archive_release.py",
                    "tools/release/archive_policy_common.py",
                    "docs/release/ARCHIVE_AND_RETENTION_POLICY.md",
                ],
            )
        )
    return findings
