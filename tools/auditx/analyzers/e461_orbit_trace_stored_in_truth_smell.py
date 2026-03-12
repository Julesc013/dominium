"""E461 orbit-trace-stored-in-truth smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.astro.sol2_audit_common import SOL2_SCOPE_PATHS, scan_orbit_trace_storage


ANALYZER_ID = "E461_ORBIT_TRACE_STORED_IN_TRUTH_SMELL"
WATCH_PREFIXES = tuple(SOL2_SCOPE_PATHS)
RULE_IDS = ("INV-ORBIT-VIEWS-DERIVED-ONLY",)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scan_orbit_trace_storage(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="sol.orbit_trace_stored_in_truth_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                line=int(violation.get("line", 0) or 0),
                evidence=[str(violation.get("message", "")).strip(), str(violation.get("snippet", "")).strip()],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=list(RULE_IDS),
                related_paths=[rel_path],
            )
        )
    return findings
