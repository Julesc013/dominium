"""E508 negotiation record missing smell analyzer for DIST-6."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.dist6_interop_common import version_interop_violations


ANALYZER_ID = "E508_NEGOTIATION_RECORD_MISSING_SMELL"
_RELEVANT_CODES = {"negotiation_record_missing"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in version_interop_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in _RELEVANT_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist.negotiation_record_missing_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "docs/audit/DIST6_FINAL.md",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "negotiation record is missing from a DIST-6 case",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RECORD_CANONICAL_NEGOTIATION_HASH",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-VERSION-INTEROP-MUST-PASS-BEFORE-DIST"],
                related_paths=[rel_path or "docs/audit/DIST6_FINAL.md", "tools/dist/dist6_interop_common.py"],
            )
        )
    return findings
