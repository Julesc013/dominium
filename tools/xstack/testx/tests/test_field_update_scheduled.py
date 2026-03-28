"""FAST test: Scheduled field updates execute deterministically on configured ticks."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_field_update_scheduled"
TEST_TAGS = ["fast", "fields", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer, update_field_layers

    layers = [
        build_field_layer(
            field_id="field.temperature.global",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.scheduled",
            extensions={"schedule_interval_ticks": 2, "scheduled_delta": 5, "default_value": 10},
        )
    ]
    cells = [
        build_field_cell(
            field_id="field.temperature.global",
            cell_id="cell.default",
            value=10,
            last_updated_tick=0,
            value_kind="scalar",
        )
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
    policy_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "update_policy_id": "field.scheduled",
                "description": "scheduled",
                "schedule_id": "schedule.field.default",
                "flow_channel_ref": None,
                "hazard_ref": None,
                "extensions": {},
            }
        ]
    }

    tick_1 = update_field_layers(
        current_tick=1,
        field_layer_rows=copy.deepcopy(layers),
        field_cell_rows=copy.deepcopy(cells),
        field_update_policy_registry=copy.deepcopy(policy_registry),
        field_type_registry=copy.deepcopy(field_type_registry),
        max_cost_units=8,
    )
    tick_2_a = update_field_layers(
        current_tick=2,
        field_layer_rows=copy.deepcopy(layers),
        field_cell_rows=copy.deepcopy(tick_1.get("field_cell_rows") or []),
        field_update_policy_registry=copy.deepcopy(policy_registry),
        field_type_registry=copy.deepcopy(field_type_registry),
        max_cost_units=8,
    )
    tick_2_b = update_field_layers(
        current_tick=2,
        field_layer_rows=copy.deepcopy(layers),
        field_cell_rows=copy.deepcopy(tick_1.get("field_cell_rows") or []),
        field_update_policy_registry=copy.deepcopy(policy_registry),
        field_type_registry=copy.deepcopy(field_type_registry),
        max_cost_units=8,
    )

    value_tick_1 = int((list(tick_1.get("field_cell_rows") or [{}])[0]).get("value", -1))
    value_tick_2 = int((list(tick_2_a.get("field_cell_rows") or [{}])[0]).get("value", -1))
    if value_tick_1 != 10:
        return {"status": "fail", "message": "scheduled field should not update at tick 1 with interval 2"}
    if value_tick_2 != 15:
        return {"status": "fail", "message": "scheduled field expected value 15 at tick 2, got {}".format(value_tick_2)}
    if dict(tick_2_a) != dict(tick_2_b):
        return {"status": "fail", "message": "scheduled field update output drifted for identical inputs"}
    return {"status": "pass", "message": "scheduled field update deterministic"}

