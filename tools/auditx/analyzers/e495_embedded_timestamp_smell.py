"""E495 embedded timestamp smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.reproducible_build_common import reproducible_build_violations


ANALYZER_ID = "E495_EMBEDDED_TIMESTAMP_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in reproducible_build_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() not in {
            "wallclock_build_token",
            "host_metadata_build_token",
        }:
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.embedded_timestamp_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "host or time metadata leaked into build identity",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_HOST_OR_TIME_METADATA_FROM_BUILD",
                related_invariants=["INV-NO-WALLCLOCK-IN-BUILD"],
                related_paths=[rel_path, "release/build_id_engine.py"],
            )
        )
    return findings
