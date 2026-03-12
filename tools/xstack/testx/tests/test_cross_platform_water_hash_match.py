"""FAST test: EARTH-8 water sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_water_hash_match"
TEST_TAGS = ["fast", "earth", "water", "hash", "determinism"]
EXPECTED_HASH = "2d15e58d0dcaac1ee08c9a379810f1ef367bc18e8cb974ba2a7a3949ce6dd56d"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth8_testlib import earth_water_hash

    actual_hash = earth_water_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-8 expected water hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-8 water hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-8 water hash matches expected fixture"}
