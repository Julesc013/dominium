"""FAST test: release manifest behavior stays consistent across normalized path forms."""

from __future__ import annotations

import os


TEST_ID = "test_cross_platform_manifest_behavior_consistent"
TEST_TAGS = ["fast", "release", "cross_platform"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release1_testlib import build_manifest_text, release_fixture

    with release_fixture() as dist_root:
        first = build_manifest_text(dist_root)
        alt_path = os.path.join(dist_root, ".", "subdir", "..")
        second = build_manifest_text(alt_path)
    if first != second:
        return {"status": "fail", "message": "manifest output changed across equivalent normalized path forms"}
    return {"status": "pass", "message": "manifest behavior is consistent across normalized path forms"}
