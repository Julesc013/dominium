from __future__ import annotations

from tools.xstack.testx.tests.xi6_testlib import (
    committed_architecture_graph_v1,
    recompute_content_hash,
    recompute_fingerprint,
)

TEST_ID = "test_arch_graph_v1_hash_stable"
TEST_TAGS = ["fast", "xi6", "determinism"]


def run(repo_root: str):
    payload = committed_architecture_graph_v1(repo_root)
    if payload.get("content_hash") != recompute_content_hash(payload):
        return {"status": "fail", "message": "architecture_graph.v1 content hash mismatch"}
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "architecture_graph.v1 fingerprint mismatch"}
    return {"status": "pass", "message": "architecture_graph.v1 hashes are stable"}
