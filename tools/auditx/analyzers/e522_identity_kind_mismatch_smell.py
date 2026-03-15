"""E522 identity kind mismatch smell analyzer for UNIVERSAL-ID0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.meta.identity_common import RULE_CANONICAL, RULE_NAMESPACED, identity_violations


ANALYZER_ID = "E522_IDENTITY_KIND_MISMATCH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in identity_violations(repo_root, strict_missing=False):
        item = dict(row or {})
        rule_id = str(item.get("rule_id", "")).strip()
        if rule_id not in {RULE_CANONICAL, RULE_NAMESPACED}:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.identity_kind_mismatch_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "src/meta/identity/identity_validator.py",
                evidence=[
                    str(item.get("code", "")).strip() or "identity_validation_error",
                    str(item.get("message", "")).strip() or "universal identity block does not match canonical artifact expectations",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ALIGN_IDENTITY_KIND_ID_AND_REQUIRED_FIELDS_WITH_ARTIFACT_KIND",
                related_invariants=[rule_id],
                related_paths=[rel_path or "src/meta/identity/identity_validator.py", "docs/meta/UNIVERSAL_IDENTITY_MODEL.md"],
            )
        )
    return findings
