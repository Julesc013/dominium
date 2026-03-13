"""FAST test: DIST-1 assembly produces a deterministic file list."""

from __future__ import annotations

import os


TEST_ID = "test_dist_tree_assembly_deterministic_filelist"
TEST_TAGS = ["fast", "dist", "release", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist1_testlib import bundle_root, filelist_text, rebuilt_bundle

    canonical_root = bundle_root(repo_root)
    if not os.path.isfile(os.path.join(canonical_root, "manifests", "filelist.txt")):
        return {"status": "fail", "message": "canonical DIST-1 file list is missing"}
    canonical_text = filelist_text(canonical_root)
    with rebuilt_bundle(repo_root) as report:
        rebuilt_root = str(report.get("bundle_root_abs", "")).strip()
        rebuilt_text = filelist_text(rebuilt_root)
    if canonical_text != rebuilt_text:
        return {"status": "fail", "message": "DIST-1 file list drifted across repeated deterministic assembly"}
    return {"status": "pass", "message": "DIST-1 file list is deterministic across repeated assembly"}
