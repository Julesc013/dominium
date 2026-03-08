"""FAST test: GEO sphere-surface atlas stub neighbors are deterministic across seams."""

from __future__ import annotations

from src.geo import geo_neighbors


TEST_ID = "test_sphere_surface_stub_neighbors_deterministic"
TEST_TAGS = ["fast", "geo", "atlas", "determinism"]


def run(repo_root: str):
    del repo_root
    result_a = geo_neighbors("atlas.north.0.0", "geo.topology.sphere_surface_s2", 1, "geo.metric.spherical_geodesic_stub")
    result_b = geo_neighbors("atlas.north.0.0", "geo.topology.sphere_surface_s2", 1, "geo.metric.spherical_geodesic_stub")
    expected = [
        "atlas.north.0.1",
        "atlas.north.1.0",
        "atlas.south.0.7",
        "atlas.south.7.0",
    ]
    if result_a != result_b:
        return {"status": "fail", "message": "sphere surface neighbor query is not deterministic"}
    if list(result_a.get("neighbors") or []) != expected:
        return {"status": "fail", "message": "unexpected atlas seam neighbors"}
    return {"status": "pass", "message": "sphere-surface atlas neighbors deterministic"}
