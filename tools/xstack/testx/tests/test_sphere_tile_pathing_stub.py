"""FAST test: GEO-6 sphere atlas tile routing is deterministic."""

from __future__ import annotations

from src.geo import build_path_request, geo_path_query


TEST_ID = "test_sphere_tile_pathing_stub"
TEST_TAGS = ["fast", "geo", "path", "sphere"]


def _cell(chart_id, index_tuple):
    return {
        "partition_profile_id": "geo.partition.sphere_tiles_stub",
        "topology_profile_id": "geo.topology.sphere_surface_s2",
        "chart_id": chart_id,
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def run(repo_root: str):
    del repo_root
    request = build_path_request(
        request_id="path.test.sphere",
        start_ref={"geo_cell_key": _cell("chart.atlas.north", [0, 0])},
        goal_ref={"geo_cell_key": _cell("chart.atlas.north", [1, 1])},
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.sphere_surface_s2",
            "metric_profile_id": "geo.metric.spherical_geodesic_stub",
            "partition_profile_id": "geo.partition.sphere_tiles_stub",
        },
    )
    first = geo_path_query(request)
    second = geo_path_query(request)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "sphere GEO path query changed across repeated runs"}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "sphere GEO path query did not complete"}
    path_cells = list((dict(first.get("path_result") or {})).get("path_cells") or [])
    if len(path_cells) < 2:
        return {"status": "fail", "message": "sphere GEO path must contain more than one tile"}
    first_chart = str(dict(path_cells[0]).get("chart_id", ""))
    last_chart = str(dict(path_cells[-1]).get("chart_id", ""))
    if first_chart != "chart.atlas.north" or last_chart != "chart.atlas.north":
        return {"status": "fail", "message": "unexpected sphere tile chart sequence"}
    return {"status": "pass", "message": "sphere GEO tile pathing stub is deterministic"}
