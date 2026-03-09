"""FAST test: EARTH-1 hydrology sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_hydrology_hash_match"
TEST_TAGS = ["fast", "earth", "hydrology", "hash", "determinism"]
EXPECTED_HASH = "04f917f853b6b572ac16408c2318292609d3da2f196b9a740765f13ac8c2fda1"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth1_testlib import earth_hydrology_hash

    actual_hash = earth_hydrology_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-1 expected hydrology hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-1 hydrology hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-1 hydrology hash matches expected fixture"}
