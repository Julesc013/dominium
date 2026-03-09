"""FAST test: MW-1 star-system artifact hash stays fixed for the canonical solar-band fixture."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_system_hash_match"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism", "cross_platform"]

EXPECTED_ARTIFACT_HASH = "d52412cd0bd3289ab46e53cdfc46c4fd4356751c8e670ba55eb67bae80a31656"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.geo import generate_worldgen_result
    from src.worldgen.mw import star_system_artifact_hash_chain
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=worldgen_request_row(
            request_id="mw1.cross_platform.artifacts",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="query",
        ),
        cache_enabled=False,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-1 cross-platform fixture did not complete"}
    observed_hash = star_system_artifact_hash_chain(result.get("generated_star_system_artifact_rows"))
    if str(observed_hash).strip().lower() != EXPECTED_ARTIFACT_HASH:
        return {
            "status": "fail",
            "message": "MW-1 star-system artifact hash drifted (expected {}, got {})".format(
                EXPECTED_ARTIFACT_HASH,
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "MW-1 canonical star-system artifact hash matches expected cross-platform fixture"}
