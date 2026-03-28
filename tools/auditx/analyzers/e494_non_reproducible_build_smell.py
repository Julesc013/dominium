"""E494 non-reproducible build smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.reproducible_build_common import reproducible_build_violations


ANALYZER_ID = "E494_NON_REPRODUCIBLE_BUILD_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in reproducible_build_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() not in {
            "build_id_cross_check_failed",
            "reproducible_manifest_drift",
            "signature_changes_manifest_identity",
            "offline_verification_failed",
        }:
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.non_reproducible_build_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "reproducible build rule violation detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE_REPRODUCIBLE_BUILD_SURFACE",
                related_invariants=["INV-BUILD-ID-MATCHES-MANIFEST"],
                related_paths=[rel_path, "release/release_manifest_engine.py", "tools/release/tool_verify_build_reproducibility.py"],
            )
        )
    return findings
