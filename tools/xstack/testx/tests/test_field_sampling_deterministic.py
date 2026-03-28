"""FAST test: Field sampling returns deterministic values for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_field_sampling_deterministic"
TEST_TAGS = ["fast", "fields", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer, get_field_value

    layer = build_field_layer(
        field_id="field.temperature.global",
        field_type_id="field.temperature",
        spatial_scope_id="spatial.global",
        resolution_level="macro",
        update_policy_id="field.static",
        extensions={"default_value": 22, "cell_size_mm": 1000},
    )
    cells = [
        build_field_cell(field_id="field.temperature.global", cell_id="cell.default", value=22, last_updated_tick=0),
        build_field_cell(field_id="field.temperature.global", cell_id="cell.0.0.0", value=13, last_updated_tick=0),
    ]
    field_type_registry = {
        "field_types": [
            {
                "schema_version": "1.0.0",
                "field_type_id": "field.temperature",
                "description": "temperature",
                "value_kind": "scalar",
                "extensions": {},
            }
        ]
    }

    position = {"position_mm": {"x": 10, "y": 20, "z": 30}}
    first = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.global",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cells[1]), dict(cells[0])],
        field_type_registry=copy.deepcopy(field_type_registry),
    )
    second = get_field_value(
        spatial_position=copy.deepcopy(position),
        field_id="field.temperature.global",
        field_layer_rows=[dict(layer)],
        field_cell_rows=[dict(cells[0]), dict(cells[1])],
        field_type_registry=copy.deepcopy(field_type_registry),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "field sample payload diverged for identical deterministic inputs"}
    if int(first.get("value", -999)) != 13:
        return {"status": "fail", "message": "expected sampled value 13 from cell.0.0.0"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "field sample fingerprint mismatch"}
    return {"status": "pass", "message": "field sampling deterministic"}

