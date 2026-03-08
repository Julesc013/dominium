"""FAST test: GEO sphere-atlas cell keys are deterministic across charted surface inputs."""

from __future__ import annotations

from src.geo import geo_cell_key_from_position


TEST_ID = "test_sphere_atlas_cell_keys_deterministic"
TEST_TAGS = ["fast", "geo", "atlas"]


def run(repo_root: str):
    del repo_root
    north_a = geo_cell_key_from_position(
        {"coords": [45000, 90000]},
        "geo.topology.sphere_surface_s2",
        "geo.partition.sphere_tiles_stub",
        "",
    )
    north_b = geo_cell_key_from_position(
        {"coords": [45000, 90000]},
        "geo.topology.sphere_surface_s2",
        "geo.partition.sphere_tiles_stub",
        "",
    )
    south = geo_cell_key_from_position(
        {"coords": [-45000, 90000]},
        "geo.topology.sphere_surface_s2",
        "geo.partition.sphere_tiles_stub",
        "",
    )
    if north_a != north_b:
        return {"status": "fail", "message": "sphere atlas key derivation is not deterministic"}
    north_key = dict(north_a.get("cell_key") or {})
    south_key = dict(south.get("cell_key") or {})
    if str(north_key.get("chart_id", "")) != "chart.atlas.north":
        return {"status": "fail", "message": "northern sphere position did not resolve to north chart"}
    if str(south_key.get("chart_id", "")) != "chart.atlas.south":
        return {"status": "fail", "message": "southern sphere position did not resolve to south chart"}
    if list(north_key.get("index_tuple") or []) != [3, 2]:
        return {"status": "fail", "message": "unexpected north sphere tile indices"}
    if list(south_key.get("index_tuple") or []) != [3, 2]:
        return {"status": "fail", "message": "unexpected south sphere tile indices"}
    return {"status": "pass", "message": "sphere atlas cell-key derivation deterministic across hemisphere charts"}
