"""FAST test: MW-4 refinement pipeline hash summary is stable across repeated runs."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_refinement_hash_match"
TEST_TAGS = ["fast", "mw4", "worldgen", "hash", "cross_platform"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mw4_testlib import refinement_report_hash, refinement_stress_report

    first = refinement_stress_report(repo_root)
    second = refinement_stress_report(repo_root)
    first_hash = refinement_report_hash(first)
    second_hash = refinement_report_hash(second)
    if first_hash != second_hash:
        return {"status": "fail", "message": "MW-4 refinement hash summary drifted across repeated runs"}
    return {
        "status": "pass",
        "message": "MW-4 refinement hash summary is stable",
        "refinement_hash": first_hash,
    }
