"""FAST test: EARTH-3 tide sample hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_tide_hash_match"
TEST_TAGS = ["fast", "earth", "tide", "hash", "determinism"]
EXPECTED_HASH = "ec764358786c230cadab45667eda9afa3905ab51eae4ff131eafc18e498f9aef"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth3_testlib import earth_tide_hash

    actual_hash = earth_tide_hash(repo_root)
    if not EXPECTED_HASH:
        return {"status": "fail", "message": "EARTH-3 expected tide hash fixture is not set"}
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "EARTH-3 tide hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "EARTH-3 tide hash matches expected fixture"}
