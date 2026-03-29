from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_blocked_preconditions, recompute_fingerprint

TEST_ID = "test_xi5x2_blocked_preconditions_deterministic"
TEST_TAGS = ["fast", "xi5x2", "determinism"]


def run(repo_root: str):
    payload = committed_blocked_preconditions(repo_root)
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "Xi-5x2 blocked preconditions fingerprint mismatch"}
    if int(payload.get("remaining_blocked_row_count", 0) or 0) != 0:
        return {"status": "fail", "message": "Xi-5x2 still has blocked preconditions after policy freeze"}
    return {"status": "pass", "message": "Xi-5x2 blocked preconditions artifact is deterministic and fully cleared"}
