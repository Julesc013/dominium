"""FAST test: EARTH-2 climate sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_climate_hash_match"
TEST_TAGS = ["fast", "earth", "climate", "hash", "determinism"]
EXPECTED_HASH = "0398b3f1623ff9d63d9b86feda3bb2f30861ba596d4fb56d31eef0ed40e041fc"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import earth_climate_hash

    actual_hash = earth_climate_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-2 expected climate hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-2 climate hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-2 climate hash matches expected fixture"}
