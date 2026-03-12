"""FAST test: SOL-2 orbit-view hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_orbit_hash_match"
TEST_TAGS = ["fast", "sol", "orbit", "hash", "determinism"]
EXPECTED_HASH = "2eb03efe5872c134f50911c49221afc791663acd0b3c5cafb5ba910049cd594f"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sol2_testlib import orbit_view_hash

    actual_hash = orbit_view_hash(repo_root)
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "SOL-2 orbit hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "SOL-2 orbit-view hash matches the expected fixture"}
