"""E466 untagged stub smell analyzer for the GAL-1 galaxy object layer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from tools.worldgen.gal1_audit_common import GAL1_SCOPE_PATHS, scan_gal1_untagged_stubs


ANALYZER_ID = "E466_GALAXY_OBJECT_UNTAGGED_STUB_SMELL"
WATCH_PREFIXES = tuple(GAL1_SCOPE_PATHS)
RULE_IDS = ("INV-GAL-OBJECTS-PROVISIONAL-TAGGED",)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in scan_gal1_untagged_stubs(repo_root):
        violation = dict(row or {})
        rel_path = str(violation.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="galaxy.object.untagged_stub_smell",
                severity="RISK",
                confidence=0.96,
                file_path=rel_path,
                line=int(violation.get("line", 0) or 0),
                evidence=[str(violation.get("message", "")).strip()],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=list(RULE_IDS),
                related_paths=[rel_path],
            )
        )
    return findings
