"""FAST test: GEO slice projection stub is deterministic for R4 inputs."""

from __future__ import annotations

from src.geo import geo_project


TEST_ID = "test_projection_stub_deterministic"
TEST_TAGS = ["fast", "geo", "projection", "determinism"]


def run(repo_root: str):
    del repo_root
    pos = {"x": 10, "y": 20, "z": 30, "w": 40}
    request = {"keep_axes": ["x", "z", "w"], "slice_axes": ["y"]}
    result_a = geo_project(
        pos,
        "geo.topology.r4_stub",
        "geo.projection.slice_nd_stub",
        projection_request=request,
    )
    result_b = geo_project(
        pos,
        "geo.topology.r4_stub",
        "geo.projection.slice_nd_stub",
        projection_request=request,
    )
    if result_a != result_b:
        return {"status": "fail", "message": "projection stub is not deterministic"}
    if dict(result_a.get("projected_position") or {}) != {"slice_axes": ["y"], "w": 40, "x": 10, "z": 30}:
        return {"status": "fail", "message": "unexpected slice projection payload"}
    return {"status": "pass", "message": "projection stub deterministic"}
