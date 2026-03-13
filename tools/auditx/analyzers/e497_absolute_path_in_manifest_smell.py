"""E497 absolute path in distribution manifest smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.distribution_model_common import distribution_model_violations


ANALYZER_ID = "E497_ABSOLUTE_PATH_IN_MANIFEST_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in distribution_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "distribution_manifest_absolute_path":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.absolute_path_in_manifest_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "absolute path found in distribution manifest",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="NORMALIZE_MANIFEST_PATH_TO_RELATIVE_OR_LOGICAL_REFERENCE",
                related_invariants=["INV-DIST-INCLUDES-RELEASE-MANIFEST"],
                related_paths=[rel_path or "dist/manifests/release_manifest.json", "docs/release/DISTRIBUTION_MODEL.md"],
            )
        )
    return findings
