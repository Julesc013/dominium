"""E496 development artifacts present in canonical distribution bundle smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.distribution_model_common import distribution_model_violations


ANALYZER_ID = "E496_DEV_ARTIFACT_IN_DIST_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in distribution_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "distribution_bundle_dev_artifact_present":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.dev_artifact_in_dist_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "development artifact present in canonical distribution bundle",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_DEV_ARTIFACT_FROM_DISTRIBUTION",
                related_invariants=["INV-DIST-NO-DEV-ARTIFACTS"],
                related_paths=[rel_path or "dist", "docs/release/DISTRIBUTION_MODEL.md"],
            )
        )
    return findings
