"""FAST test: DIST-1 bundle contains the required portable layout."""

from __future__ import annotations

import os


TEST_ID = "test_dist_tree_contains_required_layout"
TEST_TAGS = ["fast", "dist", "layout"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist1_testlib import REQUIRED_LAYOUT, bundle_root

    root = bundle_root(repo_root)
    missing = [
        rel_path
        for rel_path in REQUIRED_LAYOUT
        if not os.path.exists(os.path.join(root, rel_path.replace("/", os.sep)))
    ]
    if missing:
        return {"status": "fail", "message": "DIST-1 bundle is missing required paths: {}".format(", ".join(missing))}
    return {"status": "pass", "message": "DIST-1 bundle contains the required portable layout"}
