"""FAST test: GuideGeometry snap policy resolution is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.snap_policy_deterministic"
TEST_TAGS = ["fast", "mobility", "geometry", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mobility.geometry import build_guide_geometry, snap_geometry_parameters

    existing_rows = [
        build_guide_geometry(
            geometry_id="geometry.snap.anchor",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.test.geometry",
            parameters={
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 10000, "y": 0, "z": 0},
                ]
            },
            bounds=None,
            junction_refs=[],
            extensions={},
        )
    ]
    parameters = {
        "control_points_mm": [
            {"x": 140, "y": 60, "z": 0},
            {"x": 5000, "y": 200, "z": 0},
        ]
    }
    registry = {
        "snap_policies": [
            {
                "schema_version": "1.0.0",
                "snap_policy_id": "snap.endpoint",
                "schema_ref": "dominium.schema.mobility.geometry_snap_policy_registry.v1",
                "extensions": {"endpoint_tolerance_mm": 500, "grid_size_mm": 1000},
            }
        ]
    }
    first = snap_geometry_parameters(
        parameters=copy.deepcopy(parameters),
        snap_policy_id="snap.endpoint",
        existing_geometry_rows=copy.deepcopy(existing_rows),
        snap_policy_registry=copy.deepcopy(registry),
        spec_tolerance_mm=500,
    )
    second = snap_geometry_parameters(
        parameters=copy.deepcopy(parameters),
        snap_policy_id="snap.endpoint",
        existing_geometry_rows=copy.deepcopy(existing_rows),
        snap_policy_registry=copy.deepcopy(registry),
        spec_tolerance_mm=500,
    )
    if first != second:
        return {"status": "fail", "message": "snap policy output drifted across equivalent invocations"}
    snapped_points = list(dict(first).get("control_points_mm") or [])
    if not snapped_points or dict(snapped_points[0]) != {"x": 0, "y": 0, "z": 0}:
        return {"status": "fail", "message": "snap.endpoint did not deterministically select nearest endpoint"}
    return {"status": "pass", "message": "snap policy deterministic and stable"}
