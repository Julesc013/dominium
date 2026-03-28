"""FAST test: interior volume world transforms compose deterministically from SpatialNode hierarchy."""

from __future__ import annotations

import sys


TEST_ID = "testx.interior.spatial_transform_composition_deterministic"
TEST_TAGS = ["fast", "interior", "spatial", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from interior.interior_engine import resolve_volume_world_transform
    from tools.xstack.compatx.canonical_json import canonical_sha256

    spatial_nodes = [
        {
            "schema_version": "1.0.0",
            "spatial_id": "spatial.root",
            "parent_spatial_id": None,
            "frame_id": "frame.world",
            "transform": {
                "translation_mm": {"x": 100, "y": 200, "z": 300},
                "rotation_mdeg": {"yaw": 10, "pitch": 20, "roll": 30},
                "scale_permille": 1000,
            },
            "bounds": {},
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "spatial_id": "spatial.site.gamma",
            "parent_spatial_id": "spatial.root",
            "frame_id": "frame.world",
            "transform": {
                "translation_mm": {"x": 400, "y": 500, "z": 600},
                "rotation_mdeg": {"yaw": 40, "pitch": 50, "roll": 60},
                "scale_permille": 1000,
            },
            "bounds": {},
            "extensions": {},
        },
    ]
    volume = {
        "schema_version": "1.0.0",
        "volume_id": "volume.gamma",
        "parent_spatial_id": "spatial.site.gamma",
        "local_transform": {
            "translation_mm": {"x": 700, "y": 800, "z": 900},
            "rotation_mdeg": {"yaw": 70, "pitch": 80, "roll": 90},
            "scale_permille": 1000,
        },
        "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 500, "y": 500, "z": 500}}},
        "volume_type_id": "volume.room",
        "tags": [],
        "extensions": {},
    }
    first = resolve_volume_world_transform(volume_row=volume, spatial_nodes=spatial_nodes)
    second = resolve_volume_world_transform(volume_row=volume, spatial_nodes=spatial_nodes)
    if first != second:
        return {"status": "fail", "message": "resolved volume world transform diverged across equivalent runs"}
    world = dict(first.get("world_transform") or {})
    translation = dict(world.get("translation_mm") or {})
    rotation = dict(world.get("rotation_mdeg") or {})
    if translation != {"x": 1200, "y": 1500, "z": 1800}:
        return {"status": "fail", "message": "volume world translation composition mismatch"}
    if rotation != {"yaw": 120, "pitch": 150, "roll": 180}:
        return {"status": "fail", "message": "volume world rotation composition mismatch"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "volume transform result hash diverged across equivalent runs"}
    return {"status": "pass", "message": "interior spatial transform composition deterministic query passed"}

