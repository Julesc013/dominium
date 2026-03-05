"""FAST test: POLL-3 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_poll3_stress_scenario_deterministic"
TEST_TAGS = ["fast", "pollution", "poll3", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.poll3_testlib import make_stress_scenario

    first = make_stress_scenario(repo_root=repo_root, seed=9301)
    second = make_stress_scenario(repo_root=repo_root, seed=9301)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "POLL-3 stress scenario drifted across equivalent inputs"}
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "POLL-3 stress scenario deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "POLL-3 stress scenario generation deterministic"}

