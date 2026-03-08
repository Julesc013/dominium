"""FAST test: GEO-3 torus wrap distance returns minimal wrapped path."""

from __future__ import annotations

from src.geo import geo_distance


TEST_ID = "test_torus_wrap_distance_correct"
TEST_TAGS = ["fast", "geo", "metric", "determinism"]


def run(repo_root: str):
    del repo_root
    pos_a = {"coords": [0, 0]}
    pos_b = {"coords": [990000, 0]}
    distance_row = geo_distance(pos_a, pos_b, "geo.topology.torus_r2", "geo.metric.torus_wrap")
    if str(distance_row.get("result", "")) != "complete":
        return {"status": "fail", "message": "torus distance query refused unexpectedly"}
    if int(distance_row.get("distance_mm", -1)) != 10000:
        return {"status": "fail", "message": "unexpected wrapped torus distance: {}".format(distance_row.get("distance_mm"))}
    if int(distance_row.get("error_bound_mm", -1)) != 0:
        return {"status": "fail", "message": "unexpected torus error bound: {}".format(distance_row.get("error_bound_mm"))}
    return {"status": "pass", "message": "torus distance uses minimal wrapped path"}
