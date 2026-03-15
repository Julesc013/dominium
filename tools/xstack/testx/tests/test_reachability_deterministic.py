"""FAST test: store reachability traversal is deterministic."""

from __future__ import annotations


TEST_ID = "test_reachability_deterministic"
TEST_TAGS = ["fast", "lib", "store", "gc", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.store_gc_testlib import reachability_fingerprint

    left = reachability_fingerprint(repo_root)
    right = reachability_fingerprint(repo_root)
    if not left or left != right:
        return {"status": "fail", "message": "reachability traversal fingerprint drifted across repeated runs"}
    return {"status": "pass", "message": "store reachability traversal is deterministic"}
