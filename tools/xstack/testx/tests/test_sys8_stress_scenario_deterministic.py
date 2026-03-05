"""FAST test: SYS-8 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_stress_scenario_deterministic_sys8"
TEST_TAGS = ["fast", "system", "sys8", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys8_testlib import make_stress_scenario

    first = make_stress_scenario(repo_root=repo_root, seed=88017)
    second = make_stress_scenario(repo_root=repo_root, seed=88017)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "SYS-8 stress scenario drifted across equivalent inputs"}
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "SYS-8 scenario fingerprint mismatch across equivalent runs"}
    return {"status": "pass", "message": "SYS-8 stress scenario generation deterministic"}
