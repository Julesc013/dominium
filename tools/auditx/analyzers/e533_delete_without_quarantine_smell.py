"""E533 delete without quarantine smell analyzer for STORE-GC-0 safe mode."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.lib.store_gc_common import RULE_POLICY, store_gc_violations


ANALYZER_ID = "E533_DELETE_WITHOUT_QUARANTINE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in store_gc_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_POLICY:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="lib.delete_without_quarantine_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "lib/store/gc_engine.py",
                evidence=[
                    str(item.get("code", "")).strip() or "gc_policy_drift",
                    str(item.get("message", "")).strip() or "store GC policy drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REQUIRE_QUARANTINE_FOR_SAFE_MODE_AND_EXPLICIT_FLAGS_FOR_AGGRESSIVE_DELETION",
                related_invariants=[RULE_POLICY],
                related_paths=[rel_path or "lib/store/gc_engine.py", "docs/lib/STORE_INTEGRITY_AND_GC.md"],
            )
        )
    return findings
