"""E480 hardcoded relative path smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.virtual_paths_common import virtual_paths_violations


ANALYZER_ID = "E480_HARDCODED_RELATIVE_PATH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in virtual_paths_violations(repo_root):
        if str(dict(row).get("code", "")).strip() != "hardcoded_relative_root":
            continue
        rel_path = str(dict(row).get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="paths.hardcoded_relative_root",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                evidence=[
                    "hardcoded repository-relative root remains in a governed runtime surface",
                    "route store, pack, profile, save, export, log, and IPC access through appshell/paths/virtual_paths.py",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-HARDCODED-PATHS", "INV-VPATH-USED-FOR-STORE_ACCESS"],
                related_paths=[rel_path, "appshell/paths/virtual_paths.py"],
            )
        )
    return findings
