"""FAST test: MW-2 primary-star artifacts are deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_star_properties_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism", "l2"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    request = worldgen_request_row(
        request_id="mw2.star_properties.deterministic",
        index_tuple=[800, 0, 0],
        refinement_level=2,
        reason="query",
    )
    first = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=request,
        cache_enabled=False,
    )
    second = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=request,
        cache_enabled=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-2 star-property fixture did not complete"}
    first_rows = list(first.get("generated_star_artifact_rows") or [])
    second_rows = list(second.get("generated_star_artifact_rows") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "MW-2 generated_star_artifact_rows drifted across repeated runs"}
    if len(first_rows) <= 0:
        return {"status": "fail", "message": "MW-2 generated no star artifacts"}
    return {"status": "pass", "message": "MW-2 primary-star artifacts deterministic for identical inputs"}
