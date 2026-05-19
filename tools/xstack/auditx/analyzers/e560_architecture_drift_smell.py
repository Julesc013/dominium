"""E560 Xi-6 architecture drift smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.review.xi6_common import build_architecture_drift_report


ANALYZER_ID = "E560_ARCHITECTURE_DRIFT_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    report = build_architecture_drift_report(repo_root)
    if str(report.get("status", "")).strip().lower() == "pass":
        return []
    return [
        make_finding(
            analyzer_id=ANALYZER_ID,
            category="architecture.architecture_drift_smell",
            severity="RISK",
            confidence=0.99,
            file_path="archive/generated/architecture/architecture_graph.v1.json",
            line=1,
            evidence=[
                str(report.get("reason", "")).strip() or "architecture drift detected without ARCH-GRAPH-UPDATE",
                "frozen={} live={}".format(report.get("frozen_content_hash", ""), report.get("live_content_hash", "")),
            ],
            suggested_classification="INVALID",
            recommended_action="ADD_RULE",
            related_invariants=["INV-ARCH-GRAPH-V1-PRESENT"],
            related_paths=["archive/generated/architecture/architecture_graph.v1.json"],
        )
    ]
