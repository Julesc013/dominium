"""FAST test: EARTH-0 sampled macro surface output matches the canonical cross-platform hash."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_earth_hash_match"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "cross_platform"]

EXPECTED_EARTH_HASH = "e4a088eb4b6664e4060f42a634308a0ed2f92c3c16c20f49756685b628d44652"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth0_testlib import earth_surface_hash

    observed = earth_surface_hash(repo_root)
    if str(observed).strip().lower() != EXPECTED_EARTH_HASH:
        return {
            "status": "fail",
            "message": "EARTH-0 cross-platform hash drifted (expected {}, got {})".format(
                EXPECTED_EARTH_HASH,
                observed or "<missing>",
            ),
        }
    return {"status": "pass", "message": "EARTH-0 sampled macro surface hash matches expected cross-platform fixture"}
