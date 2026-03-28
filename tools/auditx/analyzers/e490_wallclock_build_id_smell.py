"""E490 wall-clock build identity smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_identity_common import release_identity_violations


ANALYZER_ID = "E490_WALLCLOCK_BUILD_ID_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_identity_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "wallclock_build_id_token":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.wallclock_build_id_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "wall-clock token detected in build identity path",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_WALLCLOCK_FROM_BUILD_ID",
                related_invariants=["INV-NO-WALLCLOCK-IN-BUILD_ID"],
                related_paths=[rel_path, "release/build_id_engine.py"],
            )
        )
    return findings
