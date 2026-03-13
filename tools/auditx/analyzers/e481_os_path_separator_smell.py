"""E481 OS path separator smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.virtual_paths_common import build_virtual_paths_report


ANALYZER_ID = "E481_OS_PATH_SEPARATOR_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_virtual_paths_report(repo_root)
    for row in list(report.get("os_separator_hits") or []):
        rel_path = str(dict(row).get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="paths.os_separator_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                evidence=[
                    "OS-specific path separator literal leaked into a governed path surface",
                    "virtual paths must normalize separators internally and keep command surfaces platform-neutral",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="NORMALIZE_THROUGH_VPATH",
                related_invariants=["INV-NO-HARDCODED-PATHS"],
                related_paths=[rel_path, "src/appshell/paths/virtual_paths.py"],
            )
        )
    return findings
