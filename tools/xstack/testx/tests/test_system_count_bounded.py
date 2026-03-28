"""FAST test: MW-0 bounded system-count policy caps dense inner-galaxy cells deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_system_count_bounded"
TEST_TAGS = ["fast", "mw", "worldgen", "bounds"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=worldgen_request_row(
            request_id="mw0.fixture.bounded",
            index_tuple=[0, 0, 0],
            refinement_level=0,
            reason="query",
        ),
        cache_enabled=False,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "bounded-count fixture did not complete"}
    summary = dict(result.get("mw_cell_summary") or {})
    system_count = int(summary.get("system_count", -1))
    max_systems = int(summary.get("max_systems_per_cell", -1))
    uncapped = int(summary.get("uncapped_system_count", -1))
    if system_count <= 0 or max_systems <= 0:
        return {"status": "fail", "message": "bounded-count summary missing system cap values"}
    if system_count > max_systems:
        return {"status": "fail", "message": "system_count exceeded max_systems_per_cell"}
    if str(summary.get("count_resolution", "")) != "capped":
        return {"status": "fail", "message": "dense inner-galaxy fixture did not report capped count resolution"}
    if uncapped <= system_count:
        return {"status": "fail", "message": "uncapped_system_count was not greater than bounded system_count"}
    return {"status": "pass", "message": "MW-0 dense-cell system count bounded deterministically"}
