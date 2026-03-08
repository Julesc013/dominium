"""FAST test: atlas-tile field sampling remains deterministic."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "test_atlas_tile_field_sampling_deterministic"
TEST_TAGS = ["fast", "fields", "geo", "atlas"]


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return dict(json.load(open(abs_path, "r", encoding="utf-8")))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fields import build_field_cell, build_field_layer, get_field_value

    topology_registry = _read_json(repo_root, "data/registries/space_topology_profile_registry.json")
    partition_registry = _read_json(repo_root, "data/registries/partition_profile_registry.json")
    field_binding_registry = _read_json(repo_root, "data/registries/field_binding_registry.json")
    interpolation_policy_registry = _read_json(repo_root, "data/registries/interpolation_policy_registry.json")
    field_type_registry = _read_json(repo_root, "data/registries/field_type_registry.json")

    layer = build_field_layer(
        field_id="field.temperature.surface",
        field_type_id="field.temperature",
        spatial_scope_id="spatial.surface",
        resolution_level="macro",
        update_policy_id="field.static",
        extensions={
            "topology_profile_id": "geo.topology.sphere_surface_s2",
            "partition_profile_id": "geo.partition.atlas_tiles",
            "chart_id": "chart.atlas.north",
        },
    )
    geo_cell_key = {
        "partition_profile_id": "geo.partition.atlas_tiles",
        "topology_profile_id": "geo.topology.sphere_surface_s2",
        "chart_id": "chart.atlas.north",
        "index_tuple": [1, 2],
        "refinement_level": 0,
        "extensions": {},
    }
    cell = build_field_cell(
        field_id="field.temperature.surface",
        value=9,
        last_updated_tick=0,
        geo_cell_key=geo_cell_key,
    )
    position = {"coords": [300, 700], "chart_id": "chart.atlas.north"}

    first = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.surface",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cell)],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
        interpolation_policy_registry=copy.deepcopy(interpolation_policy_registry),
        topology_registry_payload=copy.deepcopy(topology_registry),
        partition_registry_payload=copy.deepcopy(partition_registry),
    )
    second = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.surface",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cell)],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
        interpolation_policy_registry=copy.deepcopy(interpolation_policy_registry),
        topology_registry_payload=copy.deepcopy(topology_registry),
        partition_registry_payload=copy.deepcopy(partition_registry),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "atlas-tile field sampling drifted across equivalent queries"}
    if int(first.get("value", -999)) != 9:
        return {"status": "fail", "message": "atlas field sampling did not resolve the expected tile value"}
    sampled = dict(first.get("sampled_geo_cell_key") or {})
    if sampled.get("chart_id") != "chart.atlas.north" or sampled.get("index_tuple") != [1, 2]:
        return {"status": "fail", "message": "atlas field sample did not preserve canonical sampled tile identity"}
    return {"status": "pass", "message": "atlas tile field sampling remains deterministic"}

