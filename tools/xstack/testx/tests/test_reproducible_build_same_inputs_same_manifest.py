"""FAST test: identical release inputs must produce identical release manifests."""

from __future__ import annotations


TEST_ID = "test_reproducible_build_same_inputs_same_manifest"
TEST_TAGS = ["fast", "release", "reproducibility"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release2_testlib import build_manifest_text, release_fixture

    with release_fixture() as dist_root:
        first = build_manifest_text(dist_root)
        second = build_manifest_text(dist_root)
    if first != second:
        return {"status": "fail", "message": "release manifest drifted for identical build inputs"}
    return {"status": "pass", "message": "identical build inputs produce identical release manifests"}
