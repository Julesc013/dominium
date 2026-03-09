"""FAST test: EMB-0 canonical motion fixture hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_emb_hash_match"
TEST_TAGS = ["fast", "embodiment", "determinism", "cross_platform"]

EXPECTED_FINAL_STATE_HASH = "84b32bb294b1ae477473893a18d97326ba859e2465d0bb530e7944e43e555eb0"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.emb0_testlib import replay_body_motion

    result = replay_body_motion(gravity_vector={"x": 0, "y": -9, "z": 0}, include_lens_update=True)
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "EMB-0 cross-platform fixture did not complete"}
    observed_hash = str(result.get("final_state_hash", "")).strip().lower()
    if not EXPECTED_FINAL_STATE_HASH:
        return {"status": "fail", "message": "EMB-0 expected cross-platform hash placeholder must be updated"}
    if observed_hash != EXPECTED_FINAL_STATE_HASH:
        return {
            "status": "fail",
            "message": "EMB-0 final state hash drifted (expected {}, got {})".format(
                EXPECTED_FINAL_STATE_HASH,
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "EMB-0 canonical motion hash matches expected cross-platform fixture"}
