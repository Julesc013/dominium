"""E492 nondeterministic release manifest ordering smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_manifest_common import release_manifest_violations


ANALYZER_ID = "E492_NONDETERMINISTIC_MANIFEST_ORDERING_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_manifest_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "release_manifest_nondeterministic_ordering":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.nondeterministic_manifest_ordering_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "release manifest ordering drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CANONICALIZE_RELEASE_MANIFEST_ORDERING",
                related_invariants=["INV-RELEASE-MANIFEST-DETERMINISTIC"],
                related_paths=[rel_path, "release/release_manifest_engine.py"],
            )
        )
    return findings
