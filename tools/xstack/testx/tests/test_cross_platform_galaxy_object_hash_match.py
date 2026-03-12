"""FAST test: GAL-1 galaxy object replay hash remains stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_galaxy_object_hash_match"
TEST_TAGS = ["fast", "galaxy", "objects", "cross_platform", "hash"]
EXPECTED_HASH = "dd533adb0870f9cad9c9d87a303ab775d617be34f406c577b31a4421a25c0046"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.gal1_testlib import galaxy_object_replay_hash

    actual_hash = galaxy_object_replay_hash(repo_root)
    if actual_hash != EXPECTED_HASH:
        return {
            "status": "fail",
            "message": "GAL-1 galaxy object hash drifted: expected {}, got {}".format(EXPECTED_HASH, actual_hash),
        }
    return {"status": "pass", "message": "GAL-1 galaxy object replay hash matches the expected fixture"}
