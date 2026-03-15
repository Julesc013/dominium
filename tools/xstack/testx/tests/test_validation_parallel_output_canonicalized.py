"""FAST test: validation parallel output is canonicalized before reduction."""

from __future__ import annotations


TEST_ID = "test_validation_parallel_output_canonicalized"
TEST_TAGS = ["fast", "concurrency", "validation", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.concurrency_contract_testlib import build_validation_rows

    rows = build_validation_rows()
    node_ids = [str(dict(row).get("node_id", "")).strip() for row in rows]
    if node_ids != ["node.alpha", "node.beta", "node.gamma", "node.delta"]:
        return {"status": "fail", "message": "validation parallel rows were not canonicalized by level/runner/node ordering"}
    return {"status": "pass", "message": "validation parallel output canonicalization passed"}
