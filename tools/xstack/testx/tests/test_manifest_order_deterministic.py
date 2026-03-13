"""FAST test: release manifest ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_manifest_order_deterministic"
TEST_TAGS = ["fast", "release", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release1_testlib import build_manifest_text, release_fixture

    with release_fixture() as dist_root:
        first = build_manifest_text(dist_root)
        second = build_manifest_text(dist_root)
    if first != second:
        return {"status": "fail", "message": "release manifest canonical JSON drifted across repeated builds"}
    return {"status": "pass", "message": "release manifest ordering is deterministic"}
