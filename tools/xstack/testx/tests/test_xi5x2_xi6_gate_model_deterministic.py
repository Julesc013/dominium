from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_xi6_gate_model, recompute_fingerprint

TEST_ID = "test_xi5x2_xi6_gate_model_deterministic"
TEST_TAGS = ["fast", "xi5x2", "determinism"]


def run(repo_root: str):
    payload = committed_xi6_gate_model(repo_root)
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "Xi-5x2 Xi-6 gate model fingerprint mismatch"}
    return {"status": "pass", "message": "Xi-5x2 Xi-6 gate model fingerprint is stable"}
