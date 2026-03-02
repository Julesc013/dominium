"""FAST test: vehicle environment hooks do not perform micro motion simulation mutation."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.no_motion_sim_side_effects"
TEST_TAGS = ["fast", "mobility", "vehicle", "field", "effects"]


def _law_profile() -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(
        [
            "process.vehicle_register_from_structure",
            "process.vehicle_apply_environment_hooks",
        ]
    )
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.vehicle_register_from_structure"] = "entitlement.control.admin"
    privileges["process.vehicle_register_from_structure"] = "operator"
    entitlements["process.vehicle_apply_environment_hooks"] = "session.boot"
    privileges["process.vehicle_apply_environment_hooks"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _seed_state() -> dict:
    from src.fields import build_field_cell, build_field_layer
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["installed_structure_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "assembly.structure_instance.vehicle.env",
            "project_id": "project.construction.vehicle.env",
            "ag_id": "ag.vehicle.env",
            "site_ref": "site.vehicle.env",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {"spatial_id": "spatial.vehicle.env"},
        }
    ]
    state["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": "port.vehicle.env.cargo",
            "machine_id": None,
            "parent_structure_id": "assembly.structure_instance.vehicle.env",
            "port_type_id": "port.cargo",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": 500,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": None,
            "extensions": {},
        }
    ]
    state["field_layers"] = [
        build_field_layer(
            field_id="field.temperature.global",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": -10},
        ),
        build_field_layer(
            field_id="field.moisture.global",
            field_type_id="field.moisture",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 900},
        ),
        build_field_layer(
            field_id="field.friction.global",
            field_type_id="field.friction",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 600},
        ),
        build_field_layer(
            field_id="field.radiation.global",
            field_type_id="field.radiation",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 0},
        ),
        build_field_layer(
            field_id="field.visibility.global",
            field_type_id="field.visibility",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": 550},
        ),
        build_field_layer(
            field_id="field.wind.global",
            field_type_id="field.wind",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": {"x": 600, "y": 0, "z": 0}},
        ),
    ]
    state["field_cells"] = [
        build_field_cell(field_id="field.temperature.global", cell_id="cell.vehicle.env", value=-10, last_updated_tick=0),
        build_field_cell(field_id="field.moisture.global", cell_id="cell.vehicle.env", value=900, last_updated_tick=0),
        build_field_cell(field_id="field.friction.global", cell_id="cell.vehicle.env", value=600, last_updated_tick=0),
        build_field_cell(field_id="field.radiation.global", cell_id="cell.vehicle.env", value=0, last_updated_tick=0),
        build_field_cell(field_id="field.visibility.global", cell_id="cell.vehicle.env", value=550, last_updated_tick=0),
        build_field_cell(
            field_id="field.wind.global",
            cell_id="cell.vehicle.env",
            value={"x": 600, "y": 0, "z": 0},
            value_kind="vector",
            last_updated_tick=0,
        ),
    ]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    state = _seed_state()
    law = _law_profile()
    policy = policy_context()

    register_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.vehicle.env.register.001",
            "process_id": "process.vehicle_register_from_structure",
            "inputs": {
                "parent_structure_instance_id": "assembly.structure_instance.vehicle.env",
                "vehicle_class_id": "veh.road_cart",
                "created_tick_bucket": 4,
                "port_ids": ["port.vehicle.env.cargo"],
                "tier": "macro",
                "micro_state": {"geometry_id": None, "s_param": None},
                "extensions": {"field_cell_id": "cell.vehicle.env"},
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(register_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle registration failed in environment hook fixture"}
    vehicle_id = str(register_result.get("vehicle_id", "")).strip()
    if not vehicle_id:
        return {"status": "fail", "message": "registered vehicle_id missing in environment hook fixture"}

    before_motion_states = copy.deepcopy(list(state.get("vehicle_motion_states") or []))
    before_body_rows = copy.deepcopy(list(state.get("body_assemblies") or []))

    hook_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.vehicle.env.hook.001",
            "process_id": "process.vehicle_apply_environment_hooks",
            "inputs": {
                "vehicle_ids": [vehicle_id],
                "effect_duration_ticks": 2,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(hook_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle environment hooks refused unexpectedly"}
    if int(hook_result.get("auto_effect_count", 0)) <= 0:
        return {"status": "fail", "message": "vehicle environment hook fixture produced no effects"}

    after_motion_states = copy.deepcopy(list(state.get("vehicle_motion_states") or []))
    after_body_rows = copy.deepcopy(list(state.get("body_assemblies") or []))
    if before_motion_states != after_motion_states:
        return {"status": "fail", "message": "vehicle motion_state rows changed during environment hooks"}
    if before_body_rows != after_body_rows:
        return {"status": "fail", "message": "body assemblies changed during environment hooks"}

    motion_rows = [
        dict(row)
        for row in list(after_motion_states or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == vehicle_id
    ]
    if len(motion_rows) != 1:
        return {"status": "fail", "message": "vehicle motion_state row missing after environment hooks"}
    micro = dict((motion_rows[0]).get("micro_state") or {})
    if any(micro.get(key) is not None for key in ("geometry_id", "s_param", "body_ref", "position_mm", "orientation_mdeg", "velocity_mm_per_tick", "accel_mm_per_tick2")):
        return {"status": "fail", "message": "environment hooks introduced micro motion state mutation"}

    return {"status": "pass", "message": "environment hooks apply effects without micro motion side effects"}

