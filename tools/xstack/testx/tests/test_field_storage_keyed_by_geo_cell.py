"""FAST test: FIELD storage canonicalizes rows by GEO cell key."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_field_storage_keyed_by_geo_cell"
TEST_TAGS = ["fast", "fields", "geo"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import (
        build_field_cell,
        build_field_layer,
        field_get_value,
        normalize_field_cell_rows,
    )

    geo_cell_key = {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global",
        "index_tuple": [4, 2, 1],
        "refinement_level": 0,
        "extensions": {},
    }
    layer = build_field_layer(
        field_id="field.temperature.global",
        field_type_id="field.temperature",
        spatial_scope_id="spatial.global",
        resolution_level="macro",
        update_policy_id="field.static",
        extensions={
            "topology_profile_id": "geo.topology.r3_infinite",
            "partition_profile_id": "geo.partition.grid_zd",
            "chart_id": "chart.global",
        },
    )
    cell = build_field_cell(
        field_id="field.temperature.global",
        value=37,
        last_updated_tick=12,
        geo_cell_key=geo_cell_key,
        extensions={"source": "test"},
    )
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

    normalized = normalize_field_cell_rows(
        [dict(cell)],
        field_layer_rows=[dict(layer)],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
    )
    if len(normalized) != 1:
        return {"status": "fail", "message": "expected one normalized field cell"}
    row = dict(normalized[0])
    row_ext = dict(row.get("extensions") or {})
    if str(row.get("cell_id", "")).strip() != "cell.4.2.1":
        return {"status": "fail", "message": "legacy compatibility alias did not derive from GEO cell key"}
    if dict(row_ext.get("geo_cell_key") or {}).get("index_tuple") != [4, 2, 1]:
        return {"status": "fail", "message": "normalized field cell missing canonical geo_cell_key"}

    sampled = field_get_value(
        field_id="field.temperature.global",
        geo_cell_key=copy.deepcopy(geo_cell_key),
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(row)],
        field_type_registry=copy.deepcopy(field_type_registry),
        field_binding_registry=copy.deepcopy(field_binding_registry),
    )
    if int(sampled.get("value", -999)) != 37:
        return {"status": "fail", "message": "field_get_value did not resolve GEO-keyed field cell"}
    if dict(sampled.get("sampled_geo_cell_key") or {}).get("index_tuple") != [4, 2, 1]:
        return {"status": "fail", "message": "sample payload missing canonical sampled_geo_cell_key"}
    return {"status": "pass", "message": "FIELD storage is canonicalized by geo_cell_key"}

