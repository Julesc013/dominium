"""FAST test: MW-2 L2 artifact-chain hash remains fixed for the canonical solar-band fixture."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_l2_hash_match"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism", "cross_platform", "l2"]

EXPECTED_L2_HASH = "1e197bb1089acc92bc6f0fe054e9265f24c176a135a14273a6e3c9f759f4f193"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from src.geo import generate_worldgen_result
    from src.worldgen.mw import (
        planet_basic_artifact_hash_chain,
        planet_orbit_artifact_hash_chain,
        star_artifact_hash_chain,
        system_l2_summary_hash_chain,
    )
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=worldgen_request_row(
            request_id="mw2.fixture.cross_platform",
            index_tuple=[800, 0, 0],
            refinement_level=2,
            reason="query",
        ),
        cache_enabled=False,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-2 cross-platform fixture did not complete"}
    observed_hash = canonical_sha256(
        {
            "star_artifact_hash_chain": star_artifact_hash_chain(result.get("generated_star_artifact_rows")),
            "planet_orbit_artifact_hash_chain": planet_orbit_artifact_hash_chain(result.get("generated_planet_orbit_artifact_rows")),
            "planet_basic_artifact_hash_chain": planet_basic_artifact_hash_chain(result.get("generated_planet_basic_artifact_rows")),
            "system_l2_summary_hash_chain": system_l2_summary_hash_chain(result.get("generated_system_l2_summary_rows")),
        }
    )
    if str(observed_hash).strip().lower() != EXPECTED_L2_HASH:
        return {
            "status": "fail",
            "message": "MW-2 L2 artifact hash drifted (expected {}, got {})".format(
                EXPECTED_L2_HASH or "<unset>",
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "MW-2 canonical L2 artifact hash matches expected cross-platform fixture"}
