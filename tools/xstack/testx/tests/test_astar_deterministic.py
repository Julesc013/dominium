"""FAST test: GEO-6 A* tie-breaking is deterministic for equivalent paths."""

from __future__ import annotations

from src.geo import build_path_request, geo_path_query


TEST_ID = "test_astar_deterministic"
TEST_TAGS = ["fast", "geo", "path", "determinism"]


def _cell(index_tuple):
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r2_infinite",
        "chart_id": "chart.global.r2",
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def run(repo_root: str):
    del repo_root
    request = build_path_request(
        request_id="path.test.tie_break",
        start_ref={"geo_cell_key": _cell([0, 0])},
        goal_ref={"geo_cell_key": _cell([1, 1])},
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
        },
    )
    first = geo_path_query(request)
    second = geo_path_query(request)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "GEO path query changed across repeated runs"}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "GEO path tie-break fixture did not complete"}
    path_cells = list((dict(first.get("path_result") or {})).get("path_cells") or [])
    observed = [list(dict(row).get("index_tuple") or []) for row in path_cells]
    expected = [[0, 0], [0, 1], [1, 1]]
    if observed != expected:
        return {"status": "fail", "message": "unexpected tie-break path ordering: {}".format(observed)}
    return {"status": "pass", "message": "GEO path tie-break is deterministic"}
