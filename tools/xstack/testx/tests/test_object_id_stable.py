"""FAST test: GEO object IDs are stable for identical lineage inputs."""

from __future__ import annotations

from src.geo import geo_cell_key_from_position, geo_object_id


TEST_ID = "test_object_id_stable"
TEST_TAGS = ["fast", "geo", "identity"]


def run(repo_root: str):
    del repo_root
    cell_key = geo_cell_key_from_position(
        {"x": 12345, "y": -23456, "z": 999999},
        "geo.topology.r3_infinite",
        "geo.partition.grid_zd",
        "chart.global.r3",
    ).get("cell_key")
    a = geo_object_id("universe.hash.demo", cell_key, "kind.star_system", "system:0")
    b = geo_object_id("universe.hash.demo", cell_key, "kind.star_system", "system:0")
    c = geo_object_id("universe.hash.demo", cell_key, "kind.star_system", "system:1")
    if a != b:
        return {"status": "fail", "message": "object-id derivation is not deterministic"}
    if str(a.get("object_id_hash", "")) == str(c.get("object_id_hash", "")):
        return {"status": "fail", "message": "local_subkey did not influence object-id derivation"}
    return {"status": "pass", "message": "object-id derivation is stable and local-subkey-sensitive"}
