"""FAST test: gc.none report fingerprints remain stable across root-path changes."""

from __future__ import annotations


TEST_ID = "test_cross_platform_gc_report_hash_match"
TEST_TAGS = ["fast", "lib", "store", "gc", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.store_gc_testlib import gc_cross_root_fingerprints

    left, right = gc_cross_root_fingerprints(repo_root)
    if not left or left != right:
        return {"status": "fail", "message": "gc.none report fingerprints drifted across equivalent fixture roots"}
    return {"status": "pass", "message": "gc.none report fingerprints are path-neutral and deterministic"}
