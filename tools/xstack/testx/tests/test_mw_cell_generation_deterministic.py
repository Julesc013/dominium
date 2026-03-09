"""FAST test: MW-0 cell generation is deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_mw_cell_generation_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    request = worldgen_request_row(
        request_id="mw0.fixture.deterministic",
        index_tuple=[800, 0, 0],
        refinement_level=1,
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
    if dict(first) != dict(second):
        return {"status": "fail", "message": "MW-0 cell generation drifted across repeated runs"}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-0 cell generation did not complete"}
    if len(list(first.get("generated_system_seed_rows") or [])) <= 0:
        return {"status": "fail", "message": "MW-0 cell generation emitted no system seeds"}
    return {"status": "pass", "message": "MW-0 cell generation deterministic for identical inputs"}
