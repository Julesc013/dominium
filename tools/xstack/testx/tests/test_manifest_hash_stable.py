"""FAST test: release manifest hash is stable for identical inputs."""

from __future__ import annotations


TEST_ID = "test_manifest_hash_stable"
TEST_TAGS = ["fast", "release", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release1_testlib import build_manifest_payload, release_fixture

    with release_fixture() as dist_root:
        first = build_manifest_payload(dist_root)
        second = build_manifest_payload(dist_root)
    if str(first.get("manifest_hash", "")).strip() != str(second.get("manifest_hash", "")).strip():
        return {"status": "fail", "message": "manifest_hash changed across repeated builds with identical inputs"}
    return {"status": "pass", "message": "manifest_hash is stable for identical inputs"}
