"""E532 nondeterministic GC order smell analyzer for STORE-GC-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.lib.store_gc_common import RULE_DETERMINISTIC, store_gc_violations


ANALYZER_ID = "E532_NONDETERMINISTIC_GC_ORDER_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in store_gc_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_DETERMINISTIC:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="lib.nondeterministic_gc_order_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "lib/store/gc_engine.py",
                evidence=[
                    str(item.get("code", "")).strip() or "gc_determinism_drift",
                    str(item.get("message", "")).strip() or "store GC deterministic ordering drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CANONICALIZE_REACHABILITY_TRAVERSAL_AND_GC_ACTION_ORDERING_BEFORE_HASHING_OR_MUTATION",
                related_invariants=[RULE_DETERMINISTIC],
                related_paths=[rel_path or "lib/store/gc_engine.py", "lib/store/reachability_engine.py"],
            )
        )
    return findings
