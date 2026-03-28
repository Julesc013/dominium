"""FAST test: GEO-3 Euclidean distance is deterministic and bounded."""

from __future__ import annotations

from geo import geo_distance


TEST_ID = "test_euclidean_distance_deterministic"
TEST_TAGS = ["fast", "geo", "metric", "determinism"]


def run(repo_root: str):
    del repo_root
    pos_a = {"x": 0, "y": 0, "z": 0}
    pos_b = {"x": 3000, "y": 4000, "z": 0}
    first = geo_distance(pos_a, pos_b, "geo.topology.r3_infinite", "geo.metric.euclidean")
    second = geo_distance(pos_a, pos_b, "geo.topology.r3_infinite", "geo.metric.euclidean")
    if first != second:
        return {"status": "fail", "message": "euclidean distance is not deterministic"}
    if int(first.get("distance_mm", -1)) != 5000:
        return {"status": "fail", "message": "unexpected euclidean distance: {}".format(first.get("distance_mm"))}
    if int(first.get("error_bound_mm", -1)) != 0:
        return {"status": "fail", "message": "unexpected euclidean error bound: {}".format(first.get("error_bound_mm"))}
    return {"status": "pass", "message": "euclidean distance deterministic and exact"}
