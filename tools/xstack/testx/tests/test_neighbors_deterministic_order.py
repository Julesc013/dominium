"""FAST test: GEO-3 neighbors preserve deterministic order across query shapes."""

from __future__ import annotations

from src.geo import geo_cell_key_from_position, geo_neighbors


TEST_ID = "test_neighbors_deterministic_order"
TEST_TAGS = ["fast", "geo", "metric", "neighbors", "determinism"]


def run(repo_root: str):
    del repo_root
    legacy = geo_neighbors("cell.0.0", "geo.topology.r2_infinite", 1, "geo.metric.euclidean")
    explicit = geo_neighbors("cell.0.0", 1, "geo.topology.r2_infinite", "geo.metric.euclidean")
    cell_key = geo_cell_key_from_position(
        {"coords": [0, 0]},
        "geo.topology.r2_infinite",
        "geo.partition.grid_zd",
        "chart.global.r2",
    )
    canonical = geo_neighbors(
        cell_key.get("cell_key"),
        1,
        "geo.topology.r2_infinite",
        "geo.metric.euclidean",
        "geo.partition.grid_zd",
    )
    expected_legacy = ["cell.-1.0", "cell.0.-1", "cell.0.1", "cell.1.0"]
    expected_canonical = [[-1, 0], [0, -1], [0, 1], [1, 0]]
    if list(legacy.get("neighbors") or []) != expected_legacy:
        return {"status": "fail", "message": "legacy GEO neighbor ordering drifted"}
    if dict(legacy) != dict(explicit):
        return {"status": "fail", "message": "legacy and explicit neighbor query forms disagree"}
    if [list(row.get("index_tuple") or []) for row in list(canonical.get("neighbors") or [])] != expected_canonical:
        return {"status": "fail", "message": "canonical GEO neighbor ordering drifted"}
    return {"status": "pass", "message": "neighbor ordering stable across legacy and canonical query shapes"}
