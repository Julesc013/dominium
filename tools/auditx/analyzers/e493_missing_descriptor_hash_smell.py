"""E493 missing release descriptor hash smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_manifest_common import release_manifest_violations


ANALYZER_ID = "E493_MISSING_DESCRIPTOR_HASH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_manifest_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() not in {
            "release_manifest_missing_descriptor_hash",
            "release_manifest_offline_verify_failed",
        }:
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.missing_descriptor_hash_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "release manifest verification surface is incomplete",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_DESCRIPTOR_HASH_OR_FIX_OFFLINE_VERIFICATION",
                related_invariants=["INV-VERIFY-OFFLINE"],
                related_paths=[rel_path, "tools/release/tool_verify_release_manifest.py"],
            )
        )
    return findings
