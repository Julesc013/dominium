"""FAST test: GEO torus-wrap distance is deterministic and bounded by wrap period."""

from __future__ import annotations

from geo import geo_distance


TEST_ID = "test_torus_wrap_distance_deterministic"
TEST_TAGS = ["fast", "geo", "metric", "determinism"]


def run(repo_root: str):
    del repo_root
    pos_a = {"x": 0, "y": 0, "z": 0}
    pos_b = {"x": 990000, "y": 0, "z": 0}
    first = geo_distance(pos_a, pos_b, "geo.topology.torus_r3", "geo.metric.torus_wrap")
    second = geo_distance(pos_a, pos_b, "geo.topology.torus_r3", "geo.metric.torus_wrap")
    if first != second:
        return {"status": "fail", "message": "torus wrap distance is not deterministic"}
    if int(first.get("distance_mm", -1)) != 10000:
        return {"status": "fail", "message": "unexpected torus wrap distance: {}".format(first.get("distance_mm"))}
    return {"status": "pass", "message": "torus wrap distance deterministic"}
