"""FAST test: EMB-2 locomotion replay hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_locomotion_hash_match"
TEST_TAGS = ["fast", "embodiment", "locomotion", "cross_platform"]

EXPECTED_LOCOMOTION_HASH = "ea2bac2eaa65c1e073c80a0519c21f3a0b3677090428c7bacfdf9af5af7a8145"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.emb2_testlib import locomotion_hash

    observed = str(locomotion_hash(repo_root)).strip().lower()
    if not EXPECTED_LOCOMOTION_HASH:
        return {"status": "fail", "message": "EMB-2 expected locomotion hash placeholder must be updated"}
    if observed != EXPECTED_LOCOMOTION_HASH:
        return {
            "status": "fail",
            "message": "EMB-2 locomotion hash drifted (expected {}, got {})".format(
                EXPECTED_LOCOMOTION_HASH,
                observed or "<missing>",
            ),
        }
    return {"status": "pass", "message": "EMB-2 locomotion hash matches expected cross-platform fixture"}
