"""E452 mixed tick width smell analyzer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from engine.time.time_anchor_scope import SCOPED_TIME_ANCHOR_PATHS
from tools.time.time_anchor_common import scan_tick_width_violations


ANALYZER_ID = "E452_MIXED_TICK_WIDTH_SMELL"
WATCH_PREFIXES = tuple(SCOPED_TIME_ANCHOR_PATHS)
RULE_IDS = ("INV-TICK-TYPE-64BIT-ENFORCED",)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scan_tick_width_violations(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="time.mixed_tick_width_smell",
                severity="RISK",
                confidence=0.96,
                file_path=rel_path,
                line=int(violation.get("line", 0) or 0),
                evidence=[str(violation.get("message", "")).strip() or "mixed-width tick usage detected"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=list(RULE_IDS),
                related_paths=[rel_path],
            )
        )
    return findings
