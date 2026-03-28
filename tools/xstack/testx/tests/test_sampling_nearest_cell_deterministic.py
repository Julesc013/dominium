"""FAST test: GEO-bound nearest-cell sampling stays deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_sampling_nearest_cell_deterministic"
TEST_TAGS = ["fast", "fields", "geo", "determinism"]


def _fixture():
    geo_cell_key = {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global",
        "index_tuple": [1, 0, 0],
        "refinement_level": 0,
        "extensions": {},
    }
    layer = {
        "field_id": "field.temperature.global",
        "field_type_id": "field.temperature",
        "spatial_scope_id": "spatial.global",
        "resolution_level": "macro",
        "update_policy_id": "field.static",
        "extensions": {
            "topology_profile_id": "geo.topology.r3_infinite",
            "partition_profile_id": "geo.partition.grid_zd",
            "chart_id": "chart.global",
        },
    }
    field_type_registry = {
        "field_types": [
            {
                "field_type_id": "field.temperature",
                "field_id": "field.temperature",
                "value_kind": "scalar",
                "default_value": 20,
                "update_policy_id": "field.static_default",
                "extensions": {},
            }
        ]
    }
    field_binding_registry = {
        "field_bindings": [
            {
                "field_id": "field.temperature.global",
                "topology_profile_id": "geo.topology.r3_infinite",
                "partition_profile_id": "geo.partition.grid_zd",
                "storage_kind": "cell",
                "interpolation_policy_id": "interp.nearest",
                "extensions": {"chart_id": "chart.global"},
            }
        ]
    }
    interpolation_policy_registry = {
        "interpolation_policies": [
            {"policy_id": "interp.nearest", "kind": "nearest", "extensions": {}},
        ]
    }
    return geo_cell_key, layer, field_type_registry, field_binding_registry, interpolation_policy_registry


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer, get_field_value

    geo_cell_key, layer_row, field_type_registry, field_binding_registry, interpolation_policy_registry = _fixture()
    layer = build_field_layer(**layer_row)
    cells = [
        build_field_cell(
            field_id="field.temperature.global",
            value=44,
            last_updated_tick=0,
            geo_cell_key=geo_cell_key,
        ),
        build_field_cell(
            field_id="field.temperature.global",
            value=20,
            last_updated_tick=0,
            geo_cell_key={
                **geo_cell_key,
                "index_tuple": [0, 0, 0],
            },
        ),
    ]
    position = {"position_mm": {"x": 15000, "y": 0, "z": 0}}
    first = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.global",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cells[0]), dict(cells[1])],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
        interpolation_policy_registry=copy.deepcopy(interpolation_policy_registry),
    )
    second = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.global",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cells[1]), dict(cells[0])],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
        interpolation_policy_registry=copy.deepcopy(interpolation_policy_registry),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "nearest-cell sampling drifted across equivalent input orderings"}
    if int(first.get("value", -999)) != 44:
        return {"status": "fail", "message": "nearest-cell sampling did not select the expected GEO cell"}
    if str(first.get("interpolation_policy_id", "")) != "interp.nearest":
        return {"status": "fail", "message": "sampling did not report nearest interpolation policy"}
    return {"status": "pass", "message": "nearest GEO cell sampling remains deterministic"}

