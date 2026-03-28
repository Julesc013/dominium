"""FAST test: GEO-2 frame conversion remains stable at very large translation scales."""

from __future__ import annotations

import sys


TEST_ID = "test_large_scale_precision_stability"
TEST_TAGS = ["fast", "geo", "precision", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from geo import frame_graph_hash, position_distance, position_to_frame
    from tools.xstack.testx.tests.geo2_testlib import baseline_frame_nodes, large_scale_frame_transforms, poi_position, surface_position

    nodes = baseline_frame_nodes()
    transforms = large_scale_frame_transforms()
    a = surface_position()
    b = poi_position()
    version = frame_graph_hash(frame_nodes=nodes, frame_transform_rows=transforms)

    to_root = position_to_frame(
        a,
        "frame.galaxy_root",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if str(to_root.get("result", "")) != "complete":
        return {"status": "fail", "message": "large-scale conversion failed"}
    back = position_to_frame(
        dict(to_root.get("target_position_ref") or {}),
        "frame.surface_local",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if str(back.get("result", "")) != "complete":
        return {"status": "fail", "message": "large-scale roundtrip failed"}
    if list((dict(back.get("target_position_ref") or {})).get("local_position") or []) != list(a.get("local_position") or []):
        return {"status": "fail", "message": "large-scale roundtrip lost precision"}
    distance = position_distance(
        a,
        b,
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if str(distance.get("result", "")) != "complete":
        return {"status": "fail", "message": "large-scale position_distance failed"}
    if int(distance.get("distance_mm", 0) or 0) <= 0:
        return {"status": "fail", "message": "large-scale distance should be positive"}
    return {"status": "pass", "message": "GEO-2 large-scale precision stable"}
