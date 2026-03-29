from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_batch_plan, recompute_fingerprint

TEST_ID = "test_xi5x2_batch_plan_deterministic"
TEST_TAGS = ["fast", "xi5x2", "determinism"]


def run(repo_root: str):
    payload = committed_batch_plan(repo_root)
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "Xi-5x2 batch plan fingerprint mismatch"}
    return {"status": "pass", "message": "Xi-5x2 batch plan fingerprint is stable"}
