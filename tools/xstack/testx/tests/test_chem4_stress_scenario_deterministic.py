"""FAST test: CHEM-4 stress scenario generation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_chem4_stress_scenario_deterministic"
TEST_TAGS = ["fast", "chem", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem4_testlib import make_stress_scenario

    a = make_stress_scenario(
        repo_root=repo_root,
        seed=9121,
        species_pools=24,
        reactions=18,
        process_runs=24,
        ticks=36,
    )
    b = make_stress_scenario(
        repo_root=repo_root,
        seed=9121,
        species_pools=24,
        reactions=18,
        process_runs=24,
        ticks=36,
    )
    if a != b:
        return {"status": "fail", "message": "CHEM stress scenario drifted across equivalent generation inputs"}
    if str(a.get("deterministic_fingerprint", "")).strip() != str(b.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "CHEM stress scenario deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "CHEM stress scenario generation deterministic"}

