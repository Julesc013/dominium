"""FAST test: EARTH-6 terrain-collision replay hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_collision_hash_match"
TEST_TAGS = ["fast", "earth", "embodiment", "collision", "cross_platform"]

EXPECTED_COLLISION_HASH = "8ab5d6d71a672c6af7cae9280ab842183723c262af8a979f0fd7d0e39bcfa7e3"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth6_testlib import earth_collision_hash

    observed = str(earth_collision_hash(repo_root)).strip().lower()
    if observed != EXPECTED_COLLISION_HASH:
        return {
            "status": "fail",
            "message": "EARTH-6 collision hash drifted (expected {}, got {})".format(
                EXPECTED_COLLISION_HASH,
                observed or "<missing>",
            ),
        }
    return {"status": "pass", "message": "EARTH-6 collision hash matches expected fixture"}
