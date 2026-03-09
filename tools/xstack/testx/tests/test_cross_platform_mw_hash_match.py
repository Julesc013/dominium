"""FAST test: MW-0 worldgen result hash remains fixed for the canonical solar-band fixture."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_mw_hash_match"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism", "cross_platform"]

EXPECTED_RESULT_HASH = "60f30e610b9dc117985d356a4f96181682576b094d29b003b0ddc874290904b0"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=worldgen_request_row(
            request_id="mw0.fixture.cross_platform",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="query",
        ),
        cache_enabled=False,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "cross-platform MW fixture did not complete"}
    worldgen_result = dict(result.get("worldgen_result") or {})
    observed_hash = str(worldgen_result.get("deterministic_fingerprint", "")).strip().lower()
    if observed_hash != EXPECTED_RESULT_HASH:
        return {
            "status": "fail",
            "message": "MW-0 result hash drifted (expected {}, got {})".format(EXPECTED_RESULT_HASH, observed_hash or "<missing>"),
        }
    return {"status": "pass", "message": "MW-0 canonical result hash matches the expected cross-platform fixture"}
