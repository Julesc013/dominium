"""FAST test: GEO-6 expansion bounds produce explicit partial results."""

from __future__ import annotations

from src.geo import build_path_request, geo_path_query


TEST_ID = "test_expansion_bound_respected"
TEST_TAGS = ["fast", "geo", "path", "bounded"]


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
        request_id="path.test.bounded",
        start_ref={"geo_cell_key": _cell([0, 0])},
        goal_ref={"geo_cell_key": _cell([20, 0])},
        traversal_policy_id="traverse.portal_allowed_stub",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "max_expansions": 3,
        },
    )
    result = geo_path_query(request)
    if str(result.get("result", "")) != "partial":
        return {"status": "fail", "message": "bounded path query should return explicit partial result"}
    path_result = dict(result.get("path_result") or {})
    if not bool(dict(path_result.get("extensions") or {}).get("partial", False)):
        return {"status": "fail", "message": "partial path result must be marked partial"}
    if int(dict(path_result.get("extensions") or {}).get("max_expansions", 0)) != 3:
        return {"status": "fail", "message": "partial result did not preserve max_expansions"}
    return {"status": "pass", "message": "GEO path expansion bound is enforced explicitly"}
