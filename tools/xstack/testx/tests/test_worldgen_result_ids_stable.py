"""FAST test: GEO-8 result and object IDs are stable across equivalent requests."""

from __future__ import annotations

import sys


TEST_ID = "test_worldgen_result_ids_stable"
TEST_TAGS = ["fast", "geo", "worldgen", "identity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import reset_worldgen_cache, seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    identity = dict(state.get("universe_identity") or {})
    reset_worldgen_cache()
    first = generate_worldgen_result(
        universe_identity=identity,
        worldgen_request=worldgen_request_row(
            request_id="worldgen.fixture.ids.first",
            index_tuple=[4, 1, -2],
            refinement_level=3,
            reason="query",
        ),
        cache_enabled=False,
    )
    second = generate_worldgen_result(
        universe_identity=identity,
        worldgen_request=worldgen_request_row(
            request_id="worldgen.fixture.ids.second",
            index_tuple=[4, 1, -2],
            refinement_level=3,
            reason="roi",
        ),
        cache_enabled=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "worldgen result stability fixture did not complete"}
    first_result = dict(first.get("worldgen_result") or {})
    second_result = dict(second.get("worldgen_result") or {})
    if first_result != second_result:
        return {"status": "fail", "message": "canonical worldgen result drifted across equivalent requests"}
    if list(first_result.get("spawned_object_ids") or []) != list(second_result.get("spawned_object_ids") or []):
        return {"status": "fail", "message": "spawned object ids drifted across equivalent requests"}
    if not str(first_result.get("result_id", "")).strip():
        return {"status": "fail", "message": "worldgen result id was missing"}
    return {"status": "pass", "message": "GEO-8 worldgen result and object IDs stable across equivalent requests"}
