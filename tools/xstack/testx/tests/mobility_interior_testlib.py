"""Shared MOB-10 vehicle interior fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    overrides = {
        "process.vehicle_register_from_structure": ("entitlement.control.admin", "operator"),
        "process.vehicle_apply_environment_hooks": ("session.boot", "observer"),
        "process.compartment_flow_tick": ("session.boot", "observer"),
        "process.portal_seal_breach": ("entitlement.tool.operating", "operator"),
        "process.pose_enter": ("entitlement.tool.operating", "operator"),
    }
    for process_id, tuple_value in sorted(overrides.items()):
        if process_id not in set(law.get("allowed_processes") or []):
            continue
        entitlements[process_id] = str(tuple_value[0])
        privileges[process_id] = str(tuple_value[1])
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context(
    entitlements: list[str] | None = None,
    *,
    privilege_level: str = "operator",
    visibility_level: str = "diegetic",
) -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    base = construction_authority_context(list(entitlements or []), privilege_level=privilege_level)
    scope = dict(base.get("epistemic_scope") or {})
    scope["visibility_level"] = str(visibility_level)
    base["epistemic_scope"] = scope
    return base


def policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return copy.deepcopy(construction_policy_context(max_compute_units_per_tick=4096))


def seed_state(
    *,
    include_vehicle: bool = True,
    vehicle_position_x: int = 100,
) -> dict:
    from src.mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["spatial_nodes"] = [
        {
            "schema_version": "1.0.0",
            "spatial_id": "spatial.root",
            "parent_spatial_id": None,
            "frame_id": "frame.world",
            "transform": {
                "translation_mm": {"x": 0, "y": 0, "z": 0},
                "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "bounds": {},
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "spatial_id": "spatial.vehicle.alpha",
            "parent_spatial_id": "spatial.root",
            "frame_id": "frame.world",
            "transform": {
                "translation_mm": {"x": int(vehicle_position_x), "y": 0, "z": 0},
                "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "bounds": {},
            "extensions": {},
        },
    ]
    state["installed_structure_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "assembly.structure_instance.mob10.alpha",
            "project_id": "project.mob10.alpha",
            "ag_id": "ag.mob10.alpha",
            "site_ref": "site.mob10.alpha",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {"spatial_id": "spatial.vehicle.alpha"},
        }
    ]
    state["interior_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.mob10.alpha",
            "volumes": ["volume.mob10.cabin", "volume.mob10.hold"],
            "portals": ["portal.mob10.cabin_hatch"],
            "extensions": {},
        }
    ]
    state["interior_volumes"] = [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.mob10.cabin",
            "parent_spatial_id": "spatial.legacy.stub",
            "local_transform": {
                "translation_mm": {"x": 20, "y": 0, "z": 0},
                "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 800, "y": 800, "z": 800}}},
            "volume_type_id": "volume.room",
            "tags": ["cabin"],
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.mob10.hold",
            "parent_spatial_id": "spatial.legacy.stub",
            "local_transform": {
                "translation_mm": {"x": 100, "y": 0, "z": 0},
                "rotation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 1000,
            },
            "bounding_shape": {"shape_type": "aabb", "shape_data": {"half_extents_mm": {"x": 1200, "y": 1000, "z": 1000}}},
            "volume_type_id": "volume.hold",
            "tags": ["hold"],
            "extensions": {},
        },
    ]
    state["interior_portals"] = [
        {
            "schema_version": "1.0.0",
            "portal_id": "portal.mob10.cabin_hatch",
            "from_volume_id": "volume.mob10.cabin",
            "to_volume_id": "volume.mob10.hold",
            "portal_type_id": "portal.hatch",
            "state_machine_id": "state.portal.mob10.cabin_hatch",
            "sealing_coefficient": 900,
            "tags": [],
            "extensions": {
                "position_mm": {"x": 25, "y": 0, "z": 0},
            },
        }
    ]
    state["interior_portal_state_machines"] = [
        {
            "schema_version": "1.0.0",
            "machine_id": "state.portal.mob10.cabin_hatch",
            "machine_type_id": "state_machine.portal",
            "state_id": "open",
            "transitions": [],
            "transition_rows": [],
            "extensions": {},
        }
    ]
    state["portal_flow_params"] = [
        {
            "schema_version": "1.0.0",
            "portal_id": "portal.mob10.cabin_hatch",
            "conductance_air": 120,
            "conductance_water": 10,
            "conductance_smoke": 90,
            "sealing_coefficient": 900,
            "open_state_multiplier": 1000,
            "extensions": {},
        }
    ]
    state["compartment_states"] = [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.mob10.cabin",
            "air_mass": 900,
            "water_volume": 0,
            "temperature": None,
            "oxygen_fraction": 205,
            "smoke_density": 0,
            "derived_pressure": 940,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.mob10.hold",
            "air_mass": 850,
            "water_volume": 120,
            "temperature": None,
            "oxygen_fraction": 190,
            "smoke_density": 260,
            "derived_pressure": 760,
            "extensions": {},
        },
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.mob10.driver",
            "parent_assembly_id": "assembly.vehicle.mob10.alpha",
            "interior_volume_id": "volume.mob10.cabin",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": True,
            "control_binding_id": "binding.driver_basic",
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {"interior_graph_id": "interior.graph.mob10.alpha"},
        }
    ]
    state["agent_states"] = [
        {
            "agent_id": "agent.mob10.alpha",
            "body_id": "body.agent.mob10.alpha",
            "interior_volume_id": "volume.mob10.hold",
            "extensions": {"interior_volume_id": "volume.mob10.hold"},
        }
    ]
    if include_vehicle:
        vehicle_id = "vehicle.mob10.alpha"
        state["vehicles"] = [
            build_vehicle(
                vehicle_id=vehicle_id,
                parent_structure_instance_id="assembly.structure_instance.mob10.alpha",
                vehicle_class_id="veh.rail_handcart",
                spatial_id="spatial.vehicle.alpha",
                spec_ids=[],
                capability_bindings={},
                port_ids=[],
                interior_graph_id="interior.graph.mob10.alpha",
                pose_slot_ids=["pose.slot.mob10.driver"],
                mount_point_ids=[],
                motion_state_ref=deterministic_motion_state_ref(vehicle_id=vehicle_id),
                hazard_ids=[],
                maintenance_policy_id="maintenance.policy.default",
                extensions={},
            )
        ]
        state["vehicle_motion_states"] = [
            build_motion_state(
                vehicle_id=vehicle_id,
                tier="micro",
                macro_state={"itinerary_id": "itinerary.mob10.alpha"},
                meso_state={},
                micro_state={
                    "geometry_id": None,
                    "s_param": None,
                    "body_ref": None,
                    "position_mm": {"x": int(vehicle_position_x), "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "velocity_mm_per_tick": {"x": 80, "y": 0, "z": 0},
                    "accel_mm_per_tick2": {"x": 0, "y": 0, "z": 0},
                },
                last_update_tick=0,
                extensions={},
            )
        ]
    return state


def attach_field_layers(
    state: dict,
    *,
    cell_id: str = "cell.mob10.alpha",
    temperature: int = 22,
    moisture: int = 300,
    friction: int = 900,
    radiation: int = 0,
    visibility: int = 1000,
    wind: dict | None = None,
) -> dict:
    from src.fields import build_field_cell, build_field_layer

    wind_vector = dict(wind or {"x": 0, "y": 0, "z": 0})
    out = state
    out["field_layers"] = [
        build_field_layer(
            field_id="field.temperature",
            field_type_id="field.temperature",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": int(temperature)},
        ),
        build_field_layer(
            field_id="field.moisture",
            field_type_id="field.moisture",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": int(moisture)},
        ),
        build_field_layer(
            field_id="field.friction",
            field_type_id="field.friction",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": int(friction)},
        ),
        build_field_layer(
            field_id="field.radiation",
            field_type_id="field.radiation",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": int(radiation)},
        ),
        build_field_layer(
            field_id="field.visibility",
            field_type_id="field.visibility",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": int(visibility)},
        ),
        build_field_layer(
            field_id="field.wind",
            field_type_id="field.wind",
            spatial_scope_id="spatial.root",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={"default_value": dict(wind_vector)},
        ),
    ]
    out["field_cells"] = [
        build_field_cell(
            field_id="field.temperature",
            cell_id=str(cell_id),
            value=int(temperature),
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.moisture",
            cell_id=str(cell_id),
            value=int(moisture),
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.friction",
            cell_id=str(cell_id),
            value=int(friction),
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.radiation",
            cell_id=str(cell_id),
            value=int(radiation),
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.visibility",
            cell_id=str(cell_id),
            value=int(visibility),
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.wind",
            cell_id=str(cell_id),
            value={"x": int(wind_vector.get("x", 0)), "y": int(wind_vector.get("y", 0)), "z": int(wind_vector.get("z", 0))},
            value_kind="vector",
            last_updated_tick=0,
        ),
    ]
    portal_rows = [dict(row) for row in list(out.get("interior_portals") or []) if isinstance(row, dict)]
    for row in portal_rows:
        ext = dict(row.get("extensions") or {})
        ext["field_cell_id"] = str(cell_id)
        row["extensions"] = ext
    out["interior_portals"] = portal_rows
    vehicle_rows = [dict(row) for row in list(out.get("vehicles") or []) if isinstance(row, dict)]
    for row in vehicle_rows:
        ext = dict(row.get("extensions") or {})
        ext["field_cell_id"] = str(cell_id)
        row["extensions"] = ext
    out["vehicles"] = vehicle_rows
    return out


def set_vehicle_position(state: dict, *, vehicle_id: str, x: int, y: int = 0, z: int = 0) -> dict:
    out = state
    updated_motion_rows = []
    for row in list(out.get("vehicle_motion_states") or []):
        if not isinstance(row, dict):
            continue
        item = dict(row)
        if str(item.get("vehicle_id", "")).strip() == str(vehicle_id).strip():
            micro_state = dict(item.get("micro_state") or {})
            micro_state["position_mm"] = {"x": int(x), "y": int(y), "z": int(z)}
            item["micro_state"] = micro_state
        updated_motion_rows.append(item)
    out["vehicle_motion_states"] = updated_motion_rows
    vehicle_row = next(
        (
            dict(row)
            for row in list(out.get("vehicles") or [])
            if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == str(vehicle_id).strip()
        ),
        {},
    )
    spatial_id = str(vehicle_row.get("spatial_id", "")).strip()
    if spatial_id:
        updated_spatial_rows = []
        for row in list(out.get("spatial_nodes") or []):
            if not isinstance(row, dict):
                continue
            item = dict(row)
            if str(item.get("spatial_id", "")).strip() == spatial_id:
                transform = dict(item.get("transform") or {})
                transform["translation_mm"] = {"x": int(x), "y": int(y), "z": int(z)}
                item["transform"] = transform
            updated_spatial_rows.append(item)
        out["spatial_nodes"] = updated_spatial_rows
    return out
