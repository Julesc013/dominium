"""E521 missing identity block smell analyzer for UNIVERSAL-ID0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.meta.identity_common import RULE_WARN, STRICT_MISSING_POLICY_ACTIVE, identity_violations


ANALYZER_ID = "E521_MISSING_IDENTITY_BLOCK_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    if not STRICT_MISSING_POLICY_ACTIVE:
        return []
    findings = []
    for row in identity_violations(repo_root, strict_missing=False):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_WARN:
            continue
        if str(item.get("code", "")).strip() != "identity_block_missing":
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.missing_identity_block_smell",
                severity="MAJOR",
                confidence=0.99,
                file_path=rel_path or "data",
                evidence=[
                    str(item.get("code", "")).strip() or "identity_block_missing",
                    str(item.get("message", "")).strip() or "governed artifact is missing universal_identity_block",
                ],
                suggested_classification="TODO-PLANNED",
                recommended_action="ADD_UNIVERSAL_IDENTITY_BLOCK_WITH_CANONICAL_FIELDS",
                related_invariants=[RULE_WARN],
                related_paths=[rel_path or "src/meta/identity/identity_validator.py", "tools/meta/identity_common.py"],
            )
        )
    return findings
