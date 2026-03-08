"""FAST test: GEO torus cell keys canonicalize equivalent wrapped positions."""

from __future__ import annotations

from src.geo import geo_cell_key_from_position


TEST_ID = "test_torus_wrap_cell_keys"
TEST_TAGS = ["fast", "geo", "topology"]


def run(repo_root: str):
    del repo_root
    a = geo_cell_key_from_position(
        {"x": 10000, "y": -10000},
        "geo.topology.torus_r2",
        "geo.partition.grid_zd",
        "chart.global.r2",
    )
    b = geo_cell_key_from_position(
        {"x": 1010000, "y": -10000},
        "geo.topology.torus_r2",
        "geo.partition.grid_zd",
        "chart.global.r2",
    )
    if dict(a.get("cell_key") or {}) != dict(b.get("cell_key") or {}):
        return {"status": "fail", "message": "wrapped torus positions did not canonicalize to the same cell key"}
    if list((a.get("cell_key") or {}).get("index_tuple") or []) != [1, 99]:
        return {"status": "fail", "message": "unexpected canonical torus cell index tuple"}
    return {"status": "pass", "message": "torus cell-key canonicalization is deterministic"}
