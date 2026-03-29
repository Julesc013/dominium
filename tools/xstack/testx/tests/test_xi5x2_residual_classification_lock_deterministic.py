from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_classification_lock, recompute_fingerprint

TEST_ID = "test_xi5x2_residual_classification_lock_deterministic"
TEST_TAGS = ["fast", "xi5x2", "determinism"]


def run(repo_root: str):
    payload = committed_classification_lock(repo_root)
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "Xi-5x2 residual classification lock fingerprint mismatch"}
    return {"status": "pass", "message": "Xi-5x2 residual classification lock fingerprint is stable"}
