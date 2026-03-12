"""E465 unbounded galaxy object generation smell analyzer for the GAL-1 stub layer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from tools.worldgen.gal1_audit_common import GAL1_SCOPE_PATHS, scan_gal1_unbounded_generation


ANALYZER_ID = "E465_UNBOUNDED_GALAXY_OBJECT_GEN_SMELL"
WATCH_PREFIXES = tuple(GAL1_SCOPE_PATHS)
RULE_IDS = ("INV-GAL-OBJECTS-BOUNDED",)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scan_gal1_unbounded_generation(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="galaxy.object.unbounded_generation_smell",
                severity="VIOLATION",
                confidence=0.98,
                file_path=rel_path,
                line=int(violation.get("line", 0) or 0),
                evidence=[str(violation.get("message", "")).strip()],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=list(RULE_IDS),
                related_paths=[rel_path],
            )
        )
    return findings
