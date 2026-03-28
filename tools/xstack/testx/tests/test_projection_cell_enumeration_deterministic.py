"""FAST test: GEO-5 projection cell enumeration is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_projection_cell_enumeration_deterministic"
TEST_TAGS = ["fast", "geo", "projection", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from geo import build_position_ref, build_projection_request, project_view_cells

    origin = build_position_ref(
        object_id="object.camera.geo5.test",
        frame_id="frame.surface_local",
        local_position=[0, 0, 0],
        extensions={"source": "GEO5-9"},
    )
    request = build_projection_request(
        request_id="projection_request.geo5.test",
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec={"radius_cells": 1, "axis_order": ["x", "y"]},
        resolution_spec={"width": 3, "height": 3},
        extensions={
            "view_type_id": "view.map_ortho",
            "topology_profile_id": "geo.topology.r3_infinite",
            "partition_profile_id": "geo.partition.grid_zd",
            "chart_id": "chart.global.r3",
        },
    )
    first = project_view_cells(
        request,
        topology_profile_id="geo.topology.r3_infinite",
        partition_profile_id="geo.partition.grid_zd",
        metric_profile_id="geo.metric.euclidean",
    )
    second = project_view_cells(
        request,
        topology_profile_id="geo.topology.r3_infinite",
        partition_profile_id="geo.partition.grid_zd",
        metric_profile_id="geo.metric.euclidean",
    )
    if first != second:
        return {"status": "fail", "message": "projection cell enumeration is not deterministic"}
    cells = list(first.get("projected_cells") or [])
    if len(cells) != 9:
        return {"status": "fail", "message": "unexpected projected cell count for 3x3 ortho request"}
    center_key = dict(cells[4].get("geo_cell_key") or {})
    if list(center_key.get("index_tuple") or []) != [0, 0, 0]:
        return {"status": "fail", "message": "projection center cell did not resolve to origin cell key"}
    return {"status": "pass", "message": "GEO-5 projection enumeration deterministic"}
