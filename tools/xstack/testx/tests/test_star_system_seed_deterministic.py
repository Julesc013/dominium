"""FAST test: MW-1 star-system seed and artifact rows are deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_star_system_seed_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    request = worldgen_request_row(
        request_id="mw1.seed.deterministic",
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
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-1 deterministic seed fixture did not complete"}
    if list(first.get("generated_system_seed_rows") or []) != list(second.get("generated_system_seed_rows") or []):
        return {"status": "fail", "message": "MW-1 generated_system_seed_rows drifted across repeated runs"}
    if list(first.get("generated_star_system_artifact_rows") or []) != list(second.get("generated_star_system_artifact_rows") or []):
        return {"status": "fail", "message": "MW-1 generated_star_system_artifact_rows drifted across repeated runs"}
    if len(list(first.get("generated_star_system_artifact_rows") or [])) <= 0:
        return {"status": "fail", "message": "MW-1 generated no star-system artifact rows"}
    return {"status": "pass", "message": "MW-1 star-system seed/artifact rows deterministic for identical inputs"}
