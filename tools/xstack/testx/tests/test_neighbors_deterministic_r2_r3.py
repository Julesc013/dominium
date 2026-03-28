"""FAST test: GEO neighbor enumeration is deterministic for R2 and R3 baselines."""

from __future__ import annotations

from geo import geo_neighbors


TEST_ID = "test_neighbors_deterministic_r2_r3"
TEST_TAGS = ["fast", "geo", "determinism"]


def run(repo_root: str):
    del repo_root
    r2_a = geo_neighbors("cell.0.0", "geo.topology.r2_infinite", 1, "geo.metric.euclidean")
    r2_b = geo_neighbors("cell.0.0", "geo.topology.r2_infinite", 1, "geo.metric.euclidean")
    r3_a = geo_neighbors("cell.0.0.0", "geo.topology.r3_infinite", 1, "geo.metric.euclidean")
    r3_b = geo_neighbors("cell.0.0.0", "geo.topology.r3_infinite", 1, "geo.metric.euclidean")
    if r2_a != r2_b or r3_a != r3_b:
        return {"status": "fail", "message": "neighbor queries are not deterministic"}
    if list(r2_a.get("neighbors") or []) != [
        "cell.-1.0",
        "cell.0.-1",
        "cell.0.1",
        "cell.1.0",
    ]:
        return {"status": "fail", "message": "unexpected R2 neighbor ordering"}
    if list(r3_a.get("neighbors") or []) != [
        "cell.-1.0.0",
        "cell.0.-1.0",
        "cell.0.0.-1",
        "cell.0.0.1",
        "cell.0.1.0",
        "cell.1.0.0",
    ]:
        return {"status": "fail", "message": "unexpected R3 neighbor ordering"}
    return {"status": "pass", "message": "neighbors deterministic for R2/R3 baselines"}
