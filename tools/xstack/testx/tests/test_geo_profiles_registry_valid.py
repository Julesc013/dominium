"""FAST test: GEO profile registries declare required baseline rows."""

from __future__ import annotations

import json
import os


TEST_ID = "test_geo_profiles_registry_valid"
TEST_TAGS = ["fast", "geo", "registry"]


_REQUIRED = {
    "data/registries/space_topology_profile_registry.json": (
        "topology_profiles",
        "topology_profile_id",
        {
            "geo.topology.r3_infinite",
            "geo.topology.r2_infinite",
            "geo.topology.r1_infinite",
            "geo.topology.torus_r2",
            "geo.topology.torus_r3",
            "geo.topology.sphere_surface_s2",
            "geo.topology.cube_identified_stub",
            "geo.topology.r4_stub",
        },
    ),
    "data/registries/metric_profile_registry.json": (
        "metric_profiles",
        "metric_profile_id",
        {
            "geo.metric.euclidean",
            "geo.metric.torus_wrap",
            "geo.metric.spherical_geodesic_stub",
            "geo.metric.hyperbolic_stub",
        },
    ),
    "data/registries/partition_profile_registry.json": (
        "partition_profiles",
        "partition_profile_id",
        {
            "geo.partition.grid_zd",
            "geo.partition.octree_stub",
            "geo.partition.sphere_tiles_stub",
            "geo.partition.atlas_tiles",
        },
    ),
    "data/registries/projection_profile_registry.json": (
        "projection_profiles",
        "projection_profile_id",
        {
            "geo.projection.ortho_2d",
            "geo.projection.perspective_3d",
            "geo.projection.atlas_unwrap_stub",
            "geo.projection.slice_nd_stub",
        },
    ),
}


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def run(repo_root: str):
    for rel_path, (row_key, id_key, required_ids) in sorted(_REQUIRED.items()):
        try:
            payload = _load_json(repo_root, rel_path)
        except (OSError, ValueError):
            return {"status": "fail", "message": "registry missing or invalid: {}".format(rel_path)}
        rows = list(((payload.get("record") or {}).get(row_key) or []))
        if not rows:
            return {"status": "fail", "message": "registry has no rows: {}".format(rel_path)}
        ids = sorted(
            set(str(row.get(id_key, "")).strip() for row in rows if isinstance(row, dict) and str(row.get(id_key, "")).strip())
        )
        missing = sorted(set(required_ids) - set(ids))
        if missing:
            return {"status": "fail", "message": "registry missing ids in {}: {}".format(rel_path, ",".join(missing))}
    return {"status": "pass", "message": "geo profile registries valid"}
