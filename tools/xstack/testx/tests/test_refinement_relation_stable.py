"""FAST test: GEO refinement relations are deterministic and preserve lineage."""

from __future__ import annotations

from src.geo import geo_cell_key_from_position, geo_refine_cell_key


TEST_ID = "test_refinement_relation_stable"
TEST_TAGS = ["fast", "geo", "refinement"]


def run(repo_root: str):
    del repo_root
    cell_key = geo_cell_key_from_position(
        {"x": 20000, "y": 20000},
        "geo.topology.r2_infinite",
        "geo.partition.grid_zd",
        "chart.global.r2",
    ).get("cell_key")
    a = geo_refine_cell_key(cell_key, 2)
    b = geo_refine_cell_key(cell_key, 2)
    if a != b:
        return {"status": "fail", "message": "refinement relation is not deterministic"}
    child = dict(a.get("child_cell_key") or {})
    if int(child.get("refinement_level", -1)) != 2:
        return {"status": "fail", "message": "child refinement level mismatch"}
    if list(child.get("index_tuple") or []) != [8, 8]:
        return {"status": "fail", "message": "unexpected refined child index tuple"}
    relation = dict(a.get("relation") or {})
    if dict(relation.get("parent_cell_key") or {}) != dict(cell_key or {}):
        return {"status": "fail", "message": "refinement relation lost parent lineage"}
    return {"status": "pass", "message": "refinement relation deterministic and lineage-preserving"}
