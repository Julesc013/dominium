"""FAST test: EARTH-5 lighting sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_lighting_hash_match"
TEST_TAGS = ["fast", "earth", "lighting", "hash", "determinism"]
EXPECTED_HASH = "f5771f9f4f13774f4529b4a0354a03b2bea4224a41a4f3531e7d1771799d8f35"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth5_testlib import earth_lighting_hash

    actual_hash = earth_lighting_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-5 expected lighting hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-5 lighting hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-5 lighting hash matches expected fixture"}
