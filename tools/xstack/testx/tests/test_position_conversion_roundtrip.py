"""FAST test: GEO-2 frame position conversion roundtrips exactly for translation-only frame graphs."""

from __future__ import annotations

import sys


TEST_ID = "test_position_conversion_roundtrip"
TEST_TAGS = ["fast", "geo", "frames", "conversion"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from geo import frame_graph_hash, position_to_frame
    from tools.xstack.testx.tests.geo2_testlib import baseline_frame_nodes, baseline_frame_transforms, surface_position

    nodes = baseline_frame_nodes()
    transforms = baseline_frame_transforms()
    source = surface_position()
    version = frame_graph_hash(frame_nodes=nodes, frame_transform_rows=transforms)

    to_root = position_to_frame(
        source,
        "frame.galaxy_root",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if str(to_root.get("result", "")) != "complete":
        return {"status": "fail", "message": "conversion to galaxy root failed"}
    roundtrip = position_to_frame(
        dict(to_root.get("target_position_ref") or {}),
        "frame.surface_local",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if str(roundtrip.get("result", "")) != "complete":
        return {"status": "fail", "message": "roundtrip conversion failed"}
    if list((dict(roundtrip.get("target_position_ref") or {})).get("local_position") or []) != list(source.get("local_position") or []):
        return {"status": "fail", "message": "roundtrip local position changed unexpectedly"}
    return {"status": "pass", "message": "GEO-2 position roundtrip deterministic"}
