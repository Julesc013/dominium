"""FAST test: GEO-2 frame transform resolution is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_frame_transform_deterministic"
TEST_TAGS = ["fast", "geo", "frames", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from geo import frame_get_transform, frame_graph_hash
    from tools.xstack.testx.tests.geo2_testlib import baseline_frame_nodes, baseline_frame_transforms

    nodes = baseline_frame_nodes()
    transforms = baseline_frame_transforms()
    version = frame_graph_hash(frame_nodes=nodes, frame_transform_rows=transforms)
    first = frame_get_transform(
        "frame.surface_local",
        "frame.galaxy_root",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    second = frame_get_transform(
        "frame.surface_local",
        "frame.galaxy_root",
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
    )
    if first != second:
        return {"status": "fail", "message": "frame_get_transform is not deterministic"}
    if list(first.get("path_frame_ids") or []) != [
        "frame.surface_local",
        "frame.planet_root",
        "frame.system_root",
        "frame.galaxy_root",
    ]:
        return {"status": "fail", "message": "unexpected frame transform path ordering"}
    if len(list(first.get("transform_chain") or [])) != 3:
        return {"status": "fail", "message": "unexpected transform chain length"}
    return {"status": "pass", "message": "GEO-2 frame transform deterministic"}
