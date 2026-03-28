"""FAST test: GEO-6 torus routing uses wrapped adjacency deterministically."""

from __future__ import annotations

from geo import build_path_request, geo_path_query


TEST_ID = "test_torus_wrap_pathing"
TEST_TAGS = ["fast", "geo", "path", "torus"]


def _cell(index_tuple):
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.torus_r2",
        "chart_id": "chart.global.r2",
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def run(repo_root: str):
    del repo_root
    request = build_path_request(
        request_id="path.test.torus",
        start_ref={"geo_cell_key": _cell([0, 0])},
        goal_ref={"geo_cell_key": _cell([99, 0])},
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.torus_r2",
            "metric_profile_id": "geo.metric.torus_wrap",
            "partition_profile_id": "geo.partition.grid_zd",
        },
    )
    result = geo_path_query(request)
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "torus GEO path query did not complete"}
    path_cells = list((dict(result.get("path_result") or {})).get("path_cells") or [])
    observed = [list(dict(row).get("index_tuple") or []) for row in path_cells]
    if observed != [[0, 0], [99, 0]]:
        return {"status": "fail", "message": "torus wrapped path is incorrect: {}".format(observed)}
    return {"status": "pass", "message": "torus wrapped GEO path is deterministic"}
