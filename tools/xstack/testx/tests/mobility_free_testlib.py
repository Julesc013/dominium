"""Shared MOB-7 micro free-motion TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    if "process.mobility_free_tick" in set(law.get("allowed_processes") or []):
        entitlements["process.mobility_free_tick"] = "session.boot"
        privileges["process.mobility_free_tick"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context(*, max_compute_units_per_tick: int = 4096) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return copy.deepcopy(
        construction_policy_context(max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick))))
    )


def seed_free_state(
    *,
    friction_permille: int = 1000,
    wind_vector: dict | None = None,
    visibility_permille: int = 1000,
    initial_velocity_x: int = 0,
    include_second_subject: bool = False,
    corridor_geometry_id: str | None = None,
    with_collision_obstacle: bool = False,
) -> dict:
    from fields import build_field_cell, build_field_layer
    from mobility.geometry import build_guide_geometry
    from mobility.micro import build_free_motion_state
    from mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    wind = dict(wind_vector or {"x": 0, "y": 0, "z": 0})
    state["field_layers"] = [
        build_field_layer(
            field_id="field.layer.friction",
            field_type_id="field.friction",
            spatial_scope_id="spatial.mob.free.alpha",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={},
        ),
        build_field_layer(
            field_id="field.layer.visibility",
            field_type_id="field.visibility",
            spatial_scope_id="spatial.mob.free.alpha",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={},
        ),
        build_field_layer(
            field_id="field.layer.wind",
            field_type_id="field.wind",
            spatial_scope_id="spatial.mob.free.alpha",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={},
        ),
    ]
    state["field_cells"] = [
        build_field_cell(
            field_id="field.layer.friction",
            cell_id="cell.0.0.0",
            value=int(max(100, int(friction_permille))),
            last_updated_tick=0,
            value_kind="scalar",
        ),
        build_field_cell(
            field_id="field.layer.visibility",
            cell_id="cell.0.0.0",
            value=int(max(0, int(visibility_permille))),
            last_updated_tick=0,
            value_kind="scalar",
        ),
        build_field_cell(
            field_id="field.layer.wind",
            cell_id="cell.0.0.0",
            value={"x": int(wind.get("x", 0)), "y": int(wind.get("y", 0)), "z": int(wind.get("z", 0))},
            last_updated_tick=0,
            value_kind="vector",
        ),
    ]

    if str(corridor_geometry_id or "").strip():
        state["guide_geometries"] = [
            build_guide_geometry(
                geometry_id=str(corridor_geometry_id),
                geometry_type_id="geo.corridor2D",
                parent_spatial_id="spatial.mob.free.alpha",
                spec_id=None,
                parameters={},
                bounds={"min_mm": {"x": 0, "y": -200, "z": 0}, "max_mm": {"x": 500, "y": 200, "z": 0}},
                junction_refs=[],
                extensions={},
            )
        ]
    else:
        state.setdefault("guide_geometries", [])

    subject_tokens = ["vehicle.mob.free.alpha"]
    if bool(include_second_subject):
        subject_tokens.append("vehicle.mob.free.beta")

    state["vehicles"] = []
    state["vehicle_motion_states"] = []
    state["free_motion_states"] = []
    state["body_assemblies"] = []
    for index, vehicle_id in enumerate(subject_tokens):
        body_id = "body.{}".format(vehicle_id)
        x_offset = 0 if index == 0 else -40
        speed_x = int(initial_velocity_x if index == 0 else 0)
        state["vehicles"].append(
            build_vehicle(
                vehicle_id=vehicle_id,
                parent_structure_instance_id=None,
                vehicle_class_id="veh.road_car_stub",
                spatial_id="spatial.mob.free.alpha",
                spec_ids=[],
                capability_bindings={},
                port_ids=[],
                interior_graph_id=None,
                pose_slot_ids=[],
                mount_point_ids=[],
                motion_state_ref=deterministic_motion_state_ref(vehicle_id=vehicle_id),
                hazard_ids=[],
                maintenance_policy_id="maintenance.policy.default",
                extensions={},
            )
        )
        state["vehicle_motion_states"].append(
            build_motion_state(
                vehicle_id=vehicle_id,
                tier="micro",
                macro_state={"itinerary_id": "itinerary.none"},
                meso_state={},
                micro_state={
                    "geometry_id": None,
                    "s_param": None,
                    "body_ref": body_id,
                    "position_mm": {"x": int(x_offset), "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "velocity_mm_per_tick": {"x": int(speed_x), "y": 0, "z": 0},
                    "accel_mm_per_tick2": {"x": 0, "y": 0, "z": 0},
                },
                last_update_tick=0,
                extensions={},
            )
        )
        state["free_motion_states"].append(
            build_free_motion_state(
                vehicle_id=vehicle_id,
                agent_id=None,
                body_id=body_id,
                velocity={"x": int(speed_x), "y": 0, "z": 0},
                acceleration={"x": 0, "y": 0, "z": 0},
                corridor_geometry_id=(str(corridor_geometry_id).strip() if corridor_geometry_id else None),
                volume_geometry_id=None,
                last_update_tick=0,
                extensions={"policy_id": "free.default_ground"},
            )
        )
        state["body_assemblies"].append(
            {
                "assembly_id": body_id,
                "owner_assembly_id": vehicle_id,
                "owner_agent_id": None,
                "shard_id": "shard.0",
                "shape_type": "aabb",
                "shape_parameters": {
                    "radius_mm": 0,
                    "height_mm": 0,
                    "half_extents_mm": {"x": 40, "y": 40, "z": 40},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.vehicle",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": int(x_offset), "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": int(speed_x), "y": 0, "z": 0},
            }
        )

    if bool(with_collision_obstacle):
        state["body_assemblies"].append(
            {
                "assembly_id": "body.mob.free.obstacle",
                "owner_assembly_id": "obstacle.mob.free",
                "owner_agent_id": None,
                "shard_id": "shard.0",
                "shape_type": "aabb",
                "shape_parameters": {
                    "radius_mm": 0,
                    "height_mm": 0,
                    "half_extents_mm": {"x": 50, "y": 50, "z": 50},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.vehicle",
                "dynamic": False,
                "ghost": False,
                "transform_mm": {"x": 220, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        )

    state.setdefault("travel_events", [])
    state.setdefault("effect_rows", [])
    state.setdefault("fidelity_decision_entries", [])
    state.setdefault("collision_state", {})
    return state
