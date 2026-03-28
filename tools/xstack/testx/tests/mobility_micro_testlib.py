"""Shared MOB-6 micro constrained-motion TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    for process_id in ("process.mob_derail", "process.switch_set_state"):
        if process_id in set(law.get("allowed_processes") or []):
            entitlements[process_id] = "entitlement.control.admin"
            privileges[process_id] = "operator"
    if "process.coupler_attach" in set(law.get("allowed_processes") or []):
        entitlements["process.coupler_attach"] = "entitlement.tool.operating"
        privileges["process.coupler_attach"] = "operator"
    if "process.mobility_micro_tick" in set(law.get("allowed_processes") or []):
        entitlements["process.mobility_micro_tick"] = "session.boot"
        privileges["process.mobility_micro_tick"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.tool.operating", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return copy.deepcopy(construction_policy_context(max_compute_units_per_tick=4096))


def _build_network_graph(*, graph_id: str, edges: list[dict]) -> dict:
    nodes = {}
    for row in list(edges or []):
        from_node_id = str((dict(row).get("from_node_id", ""))).strip()
        to_node_id = str((dict(row).get("to_node_id", ""))).strip()
        if from_node_id:
            nodes[from_node_id] = {
                "node_id": from_node_id,
                "node_type_id": "node.mobility.endpoint",
                "tags": ["mobility", "endpoint"],
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "endpoint",
                    "parent_spatial_id": "spatial.mob.micro.alpha",
                    "position_ref": None,
                    "junction_id": None,
                    "state_machine_id": None,
                    "tags": ["mobility"],
                    "extensions": {},
                },
            }
        if to_node_id:
            nodes[to_node_id] = {
                "node_id": to_node_id,
                "node_type_id": "node.mobility.endpoint",
                "tags": ["mobility", "endpoint"],
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "endpoint",
                    "parent_spatial_id": "spatial.mob.micro.alpha",
                    "position_ref": None,
                    "junction_id": None,
                    "state_machine_id": None,
                    "tags": ["mobility"],
                    "extensions": {},
                },
            }
    return {
        "schema_version": "1.0.0",
        "graph_id": str(graph_id),
        "node_type_schema_id": "dominium.schema.mobility.mobility_node_payload.v1",
        "edge_type_schema_id": "dominium.schema.mobility.mobility_edge_payload.v1",
        "payload_schema_versions": {
            "dominium.schema.mobility.mobility_node_payload.v1": "1.0.0",
            "dominium.schema.mobility.mobility_edge_payload.v1": "1.0.0",
        },
        "validation_mode": "strict",
        "deterministic_routing_policy_id": "route.shortest_delay",
        "graph_partition_id": None,
        "nodes": [dict(nodes[key]) for key in sorted(nodes.keys())],
        "edges": [dict(row) for row in list(edges or [])],
        "extensions": {},
    }


def seed_micro_state(
    *,
    length_mm: int = 12000,
    min_curvature_radius_mm: int = 24000,
    initial_s_param: int = 0,
    initial_velocity: int = 0,
    include_second_vehicle: bool = False,
) -> dict:
    from mobility.geometry import build_guide_geometry
    from mobility.micro import build_micro_motion_state
    from mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    geometry_id = "geometry.mob.micro.main"
    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id=geometry_id,
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.micro.alpha",
            spec_id=None,
            parameters={
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": int(max(1, int(length_mm))), "y": 0, "z": 0},
                ]
            },
            bounds={},
            junction_refs=[],
            extensions={},
        )
    ]
    state["geometry_derived_metrics"] = [
        {
            "schema_version": "1.0.0",
            "geometry_id": geometry_id,
            "geometry_hash": "geometry.hash.mob.micro.main",
            "computed_tick": 0,
            "length_mm": int(max(1, int(length_mm))),
            "min_curvature_radius_mm": int(max(1, int(min_curvature_radius_mm))),
            "curvature_bands": {"low": 1, "medium": 0, "high": 0},
            "clearance_envelope": {"width_mm": 3200, "height_mm": 4200},
            "cost_units_used": 1,
            "degraded": False,
            "degrade_reason": None,
            "deterministic_fingerprint": "metric.det.mob.micro.main",
            "extensions": {},
        }
    ]
    state["network_graphs"] = [
        _build_network_graph(
            graph_id="graph.mob.micro.alpha",
            edges=[
                {
                    "edge_id": "edge.mob.micro.main",
                    "from_node_id": "node.mob.micro.a",
                    "to_node_id": "node.mob.micro.b",
                    "edge_type_id": "edge.mobility.track",
                    "capacity": 1,
                    "delay_ticks": 1,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "track",
                        "guide_geometry_id": geometry_id,
                        "spec_id": None,
                        "capacity_units": 1,
                        "max_speed_policy_id": "speed_policy.spec_based",
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                }
            ],
        )
    ]

    vehicle_ids = ["vehicle.mob.micro.alpha"]
    if bool(include_second_vehicle):
        vehicle_ids.append("vehicle.mob.micro.beta")

    state["vehicles"] = []
    state["vehicle_motion_states"] = []
    state["micro_motion_states"] = []
    for index, vehicle_id in enumerate(vehicle_ids):
        s_value = int(max(0, int(initial_s_param) - (index * 200)))
        velocity = int(initial_velocity if index == 0 else 0)
        state["vehicles"].append(
            build_vehicle(
                vehicle_id=vehicle_id,
                parent_structure_instance_id=None,
                vehicle_class_id="veh.rail_handcart",
                spatial_id="spatial.mob.micro.alpha",
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
                macro_state={},
                meso_state={},
                micro_state={
                    "geometry_id": geometry_id,
                    "s_param": int(s_value),
                    "body_ref": None,
                    "position_mm": {"x": int(s_value), "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "velocity_mm_per_tick": {"x": int(velocity), "y": 0, "z": 0},
                    "accel_mm_per_tick2": {"x": 0, "y": 0, "z": 0},
                },
                last_update_tick=0,
                extensions={},
            )
        )
        state["micro_motion_states"].append(
            build_micro_motion_state(
                vehicle_id=vehicle_id,
                geometry_id=geometry_id,
                s_param=int(s_value),
                velocity=int(velocity),
                acceleration=0,
                direction="forward",
                last_update_tick=0,
                extensions={},
            )
        )

    state.setdefault("mobility_junctions", [])
    state.setdefault("mobility_switch_state_machines", [])
    state.setdefault("coupling_constraints", [])
    return state


def seed_switch_handoff_state() -> dict:
    from mobility.geometry import build_guide_geometry, build_junction
    from mobility.micro import build_micro_motion_state
    from mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    main_geometry_id = "geometry.mob.micro.main"
    branch_geometry_id = "geometry.mob.micro.branch"
    switch_machine_id = "state_machine.mob.micro.switch"

    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id=main_geometry_id,
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.micro.alpha",
            spec_id=None,
            parameters={"control_points_mm": [{"x": 0, "y": 0, "z": 0}, {"x": 12000, "y": 0, "z": 0}]},
            bounds={},
            junction_refs=["junction.mob.micro.switch"],
            extensions={},
        ),
        build_guide_geometry(
            geometry_id=branch_geometry_id,
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.micro.alpha",
            spec_id=None,
            parameters={"control_points_mm": [{"x": 12000, "y": 0, "z": 0}, {"x": 18000, "y": 1600, "z": 0}]},
            bounds={},
            junction_refs=["junction.mob.micro.switch"],
            extensions={},
        ),
    ]
    state["geometry_derived_metrics"] = [
        {
            "schema_version": "1.0.0",
            "geometry_id": main_geometry_id,
            "geometry_hash": "geometry.hash.mob.micro.main",
            "computed_tick": 0,
            "length_mm": 12000,
            "min_curvature_radius_mm": 24000,
            "curvature_bands": {"low": 1, "medium": 0, "high": 0},
            "clearance_envelope": {"width_mm": 3200, "height_mm": 4200},
            "cost_units_used": 1,
            "degraded": False,
            "degrade_reason": None,
            "deterministic_fingerprint": "metric.det.mob.micro.main",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "geometry_id": branch_geometry_id,
            "geometry_hash": "geometry.hash.mob.micro.branch",
            "computed_tick": 0,
            "length_mm": 6400,
            "min_curvature_radius_mm": 30000,
            "curvature_bands": {"low": 1, "medium": 0, "high": 0},
            "clearance_envelope": {"width_mm": 3200, "height_mm": 4200},
            "cost_units_used": 1,
            "degraded": False,
            "degrade_reason": None,
            "deterministic_fingerprint": "metric.det.mob.micro.branch",
            "extensions": {},
        },
    ]
    state["mobility_junctions"] = [
        build_junction(
            junction_id="junction.mob.micro.switch",
            parent_spatial_id="spatial.mob.micro.alpha",
            connected_geometry_ids=[main_geometry_id, branch_geometry_id],
            junction_type_id="junc.switch",
            state_machine_id=switch_machine_id,
            extensions={},
        )
    ]
    state["mobility_switch_state_machines"] = [
        {
            "schema_version": "1.0.0",
            "machine_id": switch_machine_id,
            "machine_type_id": "state_machine.mobility.switch",
            "state_id": "edge.mob.micro.branch",
            "transitions": [],
            "transition_rows": [],
            "extensions": {},
        }
    ]
    state["network_graphs"] = [
        _build_network_graph(
            graph_id="graph.mob.micro.switch",
            edges=[
                {
                    "edge_id": "edge.mob.micro.main",
                    "from_node_id": "node.mob.micro.main.a",
                    "to_node_id": "node.mob.micro.main.b",
                    "edge_type_id": "edge.mobility.track",
                    "capacity": 1,
                    "delay_ticks": 1,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "track",
                        "guide_geometry_id": main_geometry_id,
                        "spec_id": None,
                        "capacity_units": 1,
                        "max_speed_policy_id": "speed_policy.spec_based",
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                },
                {
                    "edge_id": "edge.mob.micro.branch",
                    "from_node_id": "node.mob.micro.main.b",
                    "to_node_id": "node.mob.micro.branch.b",
                    "edge_type_id": "edge.mobility.track",
                    "capacity": 1,
                    "delay_ticks": 1,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "track",
                        "guide_geometry_id": branch_geometry_id,
                        "spec_id": None,
                        "capacity_units": 1,
                        "max_speed_policy_id": "speed_policy.spec_based",
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                },
            ],
        )
    ]
    vehicle_id = "vehicle.mob.micro.alpha"
    state["vehicles"] = [
        build_vehicle(
            vehicle_id=vehicle_id,
            parent_structure_instance_id=None,
            vehicle_class_id="veh.rail_handcart",
            spatial_id="spatial.mob.micro.alpha",
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
    ]
    state["vehicle_motion_states"] = [
        build_motion_state(
            vehicle_id=vehicle_id,
            tier="micro",
            macro_state={},
            meso_state={},
            micro_state={
                "geometry_id": main_geometry_id,
                "s_param": 11980,
                "body_ref": None,
                "position_mm": {"x": 11980, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 240, "y": 0, "z": 0},
                "accel_mm_per_tick2": {"x": 0, "y": 0, "z": 0},
            },
            last_update_tick=0,
            extensions={},
        )
    ]
    state["micro_motion_states"] = [
        build_micro_motion_state(
            vehicle_id=vehicle_id,
            geometry_id=main_geometry_id,
            s_param=11980,
            velocity=240,
            acceleration=0,
            direction="forward",
            last_update_tick=0,
            extensions={},
        )
    ]
    state.setdefault("coupling_constraints", [])
    return state


def attach_speed_cap_effect(state: dict, *, vehicle_id: str, max_speed_permille: int) -> dict:
    from control.effects import build_effect

    out = dict(state)
    out["effect_rows"] = [
        dict(row)
        for row in list(out.get("effect_rows") or [])
        if isinstance(row, dict)
    ]
    out["effect_rows"].append(
        build_effect(
            effect_type_id="effect.speed_cap",
            target_id=str(vehicle_id),
            applied_tick=0,
            magnitude={"max_speed_permille": int(max(0, min(1000, int(max_speed_permille))))},
            stacking_policy_id="stack.min",
            duration_ticks=None,
            expires_tick=None,
            source_event_id="event.test.mob.micro.speed_cap",
            extensions={},
        )
    )
    return out
