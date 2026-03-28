"""FAST test: MW-1 nearest-system query is deterministic and resolves the exact system position."""

from __future__ import annotations

import sys


TEST_ID = "test_query_nearest_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "query", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo.frame.frame_engine import build_position_ref
    from worldgen.mw import list_systems_in_cell, query_nearest_system
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_cell_key

    state = seed_worldgen_state()
    systems_result = list_systems_in_cell(
        universe_identity=state.get("universe_identity"),
        geo_cell_key=worldgen_cell_key([800, 0, 0]),
        cache_enabled=False,
    )
    systems = list(systems_result.get("systems") or [])
    if not systems:
        return {"status": "fail", "message": "MW-1 query fixture produced no systems to target"}
    target = dict(systems[0])
    probe = build_position_ref(
        object_id="probe.query_nearest",
        frame_id="frame.milky_way.galactic",
        local_position=list((dict(target.get("galaxy_position_ref") or {})).get("local_position") or []),
        extensions={"source": "mw1_test"},
    )
    first = query_nearest_system(
        universe_identity=state.get("universe_identity"),
        position_ref=probe,
        radius=10**21,
        cache_enabled=False,
    )
    second = query_nearest_system(
        universe_identity=state.get("universe_identity"),
        position_ref=probe,
        radius=10**21,
        cache_enabled=False,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "MW-1 nearest-system query drifted across repeated runs"}
    nearest = dict(first.get("nearest_system") or {})
    if not bool(first.get("found", False)) or not nearest:
        return {"status": "fail", "message": "MW-1 nearest-system query failed to resolve a result"}
    if str(nearest.get("object_id", "")).strip() != str(target.get("object_id", "")).strip():
        return {"status": "fail", "message": "MW-1 nearest-system query resolved the wrong object_id"}
    if int(nearest.get("distance_mm", -1)) != 0:
        return {"status": "fail", "message": "MW-1 nearest-system query did not return zero distance for exact position"}
    return {"status": "pass", "message": "MW-1 nearest-system query deterministic for exact-position lookup"}
