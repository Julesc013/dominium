"""FAST test: EARTH-0 sampled macro surface output matches the canonical cross-platform hash."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_earth_hash_match"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "cross_platform"]

EXPECTED_EARTH_HASH = "b8864a86235a1bfd88f2d9f00792b70c6ac3731a8c0710fe9b66028c319c70bb"


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
