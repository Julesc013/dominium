"""FAST test: EARTH-7 wind sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_wind_hash_match"
TEST_TAGS = ["fast", "earth", "wind", "hash", "determinism"]
EXPECTED_HASH = "e034b4334b563882a55eab7116dd5d043cc366de68de91fdaab3a8847e089dc5"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth7_testlib import earth_wind_hash

    actual_hash = earth_wind_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-7 expected wind hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-7 wind hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-7 wind hash matches expected fixture"}
