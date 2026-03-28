"""FAST test: GEO cell-key derivation is deterministic for canonical grid inputs."""

from __future__ import annotations

from geo import geo_cell_key_from_position


TEST_ID = "test_cell_key_from_position_deterministic"
TEST_TAGS = ["fast", "geo", "determinism"]


def run(repo_root: str):
    del repo_root
    a = geo_cell_key_from_position(
        {"x": 12345, "y": -23456, "z": 999999},
        "geo.topology.r3_infinite",
        "geo.partition.grid_zd",
        "chart.global.r3",
    )
    b = geo_cell_key_from_position(
        {"x": 12345, "y": -23456, "z": 999999},
        "geo.topology.r3_infinite",
        "geo.partition.grid_zd",
        "chart.global.r3",
    )
    if a != b:
        return {"status": "fail", "message": "cell-key derivation is not deterministic"}
    cell_key = dict(a.get("cell_key") or {})
    if list(cell_key.get("index_tuple") or []) != [1, -3, 99]:
        return {"status": "fail", "message": "unexpected canonical R3 grid index tuple"}
    if str((cell_key.get("extensions") or {}).get("legacy_cell_alias", "")) != "cell.1.-3.99":
        return {"status": "fail", "message": "unexpected legacy cell alias"}
    return {"status": "pass", "message": "cell-key derivation deterministic for canonical grid inputs"}
