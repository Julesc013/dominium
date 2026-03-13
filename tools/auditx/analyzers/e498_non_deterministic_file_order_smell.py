"""E498 nondeterministic DIST-1 file ordering smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.dist_tree_common import dist_tree_violations


ANALYZER_ID = "E498_NON_DETERMINISTIC_FILE_ORDER_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in dist_tree_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "dist_tree_file_order_non_deterministic":
            continue
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.non_deterministic_file_order_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "distribution file list ordering drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CANONICALIZE_DIST_FILE_ORDER",
                related_invariants=["INV-DIST-TREE-DETERMINISTIC"],
                related_paths=[rel_path or "dist/v0.0.0-mock/win64/dominium/manifests/filelist.txt", "tools/dist/dist_tree_common.py"],
            )
        )
    return findings
