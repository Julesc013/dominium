"""FAST test: EARTH-4 sky sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_sky_hash_match"
TEST_TAGS = ["fast", "earth", "sky", "hash", "determinism"]
EXPECTED_HASH = "7d55f1aaf5d417f1c14e2ad353f2e77c96ff78941cf4dd6648393762a0797c1d"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth4_testlib import earth_sky_hash

    actual_hash = earth_sky_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-4 expected sky hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-4 sky hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-4 sky hash matches expected fixture"}
