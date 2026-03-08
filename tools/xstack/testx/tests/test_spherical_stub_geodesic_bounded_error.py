"""FAST test: GEO-3 spherical stub geodesic is deterministic within declared bounds."""

from __future__ import annotations

from src.geo import geo_geodesic


TEST_ID = "test_spherical_stub_geodesic_bounded_error"
TEST_TAGS = ["fast", "geo", "metric", "geodesic", "determinism"]


def run(repo_root: str):
    del repo_root
    pos_a = {"coords": [0, 0]}
    pos_b = {"coords": [0, 1000]}
    first = geo_geodesic(pos_a, pos_b, "geo.topology.sphere_surface_s2", "geo.metric.spherical_geodesic_stub")
    second = geo_geodesic(pos_a, pos_b, "geo.topology.sphere_surface_s2", "geo.metric.spherical_geodesic_stub")
    if first != second:
        return {"status": "fail", "message": "spherical stub geodesic is not deterministic"}
    geodesic_mm = int(first.get("geodesic_mm", -1))
    raw_value_mm = int(first.get("raw_value_mm", -1))
    error_bound_mm = int(first.get("error_bound_mm", -1))
    if geodesic_mm <= 0:
        return {"status": "fail", "message": "spherical stub geodesic missing positive distance"}
    if error_bound_mm < 0:
        return {"status": "fail", "message": "spherical stub error bound missing"}
    if abs(raw_value_mm - geodesic_mm) > error_bound_mm:
        return {"status": "fail", "message": "spherical stub geodesic exceeds declared error bound"}
    return {"status": "pass", "message": "spherical stub geodesic deterministic within declared bound"}
