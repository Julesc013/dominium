"""Shared MOB-4 macro travel TestX fixtures."""

from __future__ import annotations

import copy


def _spec_rows(*, vehicle_gauge_mm: int, edge_gauge_mm: int) -> list[dict]:
    return [
        {
            "spec_id": "spec.mob.travel.vehicle",
            "spec_type_id": "spec.track",
            "description": "Vehicle interface fixture spec for MOB-4 tests.",
            "parameters": {
                "gauge_mm": int(max(1, int(vehicle_gauge_mm))),
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
        {
            "spec_id": "spec.mob.travel.edge",
            "spec_type_id": "spec.track",
            "description": "Edge interface fixture spec for MOB-4 tests.",
            "parameters": {
                "gauge_mm": int(max(1, int(edge_gauge_mm))),
                "max_speed_mm_per_tick": 1600,
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
    ]


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    admin_processes = (
        "process.itinerary_create",
        "process.mobility_reserve_edge",
        "process.travel_schedule_set",
        "process.travel_start",
    )
    for process_id in admin_processes:
        if process_id in set(law.get("allowed_processes") or []):
            entitlements[process_id] = "entitlement.control.admin"
            privileges[process_id] = "operator"
    if "process.travel_tick" in set(law.get("allowed_processes") or []):
        entitlements["process.travel_tick"] = "session.boot"
        privileges["process.travel_tick"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context(*, vehicle_gauge_mm: int = 1000, edge_gauge_mm: int = 1000) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    policy = copy.deepcopy(construction_policy_context())
    policy["spec_sheet_rows"] = _spec_rows(
        vehicle_gauge_mm=int(vehicle_gauge_mm),
        edge_gauge_mm=int(edge_gauge_mm),
    )
    return policy


def seed_state(*, vehicle_gauge_mm: int = 1000, edge_gauge_mm: int = 1000) -> dict:
    from src.mobility.geometry import build_guide_geometry
    from src.mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.construction_testlib import base_state

    del edge_gauge_mm
    state = base_state()
    state["network_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "graph.mob.travel.alpha",
            "node_type_schema_id": "dominium.schema.mobility.mobility_node_payload.v1",
            "edge_type_schema_id": "dominium.schema.mobility.mobility_edge_payload.v1",
            "payload_schema_versions": {
                "dominium.schema.mobility.mobility_node_payload.v1": "1.0.0",
                "dominium.schema.mobility.mobility_edge_payload.v1": "1.0.0",
            },
            "validation_mode": "strict",
            "deterministic_routing_policy_id": "route.shortest_delay",
            "graph_partition_id": None,
            "nodes": [
                {
                    "node_id": "node.mob.travel.a",
                    "node_type_id": "node.mobility.endpoint",
                    "tags": ["mobility", "endpoint"],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "endpoint",
                        "parent_spatial_id": "spatial.mob.travel.alpha",
                        "position_ref": None,
                        "junction_id": None,
                        "state_machine_id": None,
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                },
                {
                    "node_id": "node.mob.travel.b",
                    "node_type_id": "node.mobility.endpoint",
                    "tags": ["mobility", "endpoint"],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "endpoint",
                        "parent_spatial_id": "spatial.mob.travel.alpha",
                        "position_ref": None,
                        "junction_id": None,
                        "state_machine_id": None,
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                },
            ],
            "edges": [
                {
                    "edge_id": "edge.mob.travel.ab",
                    "from_node_id": "node.mob.travel.a",
                    "to_node_id": "node.mob.travel.b",
                    "edge_type_id": "edge.mobility.track",
                    "capacity": 1,
                    "delay_ticks": 1,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "track",
                        "guide_geometry_id": "geometry.mob.travel.ab",
                        "spec_id": "spec.mob.travel.edge",
                        "capacity_units": 1,
                        "max_speed_policy_id": "speed_policy.spec_based",
                        "tags": ["mobility"],
                        "extensions": {},
                    },
                }
            ],
            "extensions": {},
        }
    ]
    state["guide_geometries"] = [
        build_guide_geometry(
            geometry_id="geometry.mob.travel.ab",
            geometry_type_id="geo.spline1D",
            parent_spatial_id="spatial.mob.travel.alpha",
            spec_id="spec.mob.travel.edge",
            parameters={
                "control_points_mm": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 12000, "y": 0, "z": 0},
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
            "geometry_id": "geometry.mob.travel.ab",
            "geometry_hash": "geometry_hash.mob.travel.ab",
            "computed_tick": 0,
            "length_mm": 12000,
            "min_curvature_radius_mm": 24000,
            "curvature_bands": {"low": 1, "medium": 0, "high": 0},
            "clearance_envelope": {"width_mm": 3000, "height_mm": 4000},
            "cost_units_used": 3,
            "degraded": False,
            "degrade_reason": None,
            "deterministic_fingerprint": "det.mob.travel.metric",
            "extensions": {},
        }
    ]
    vehicle_id = "vehicle.mob.travel.alpha"
    motion_state_ref = deterministic_motion_state_ref(vehicle_id=vehicle_id)
    state["vehicles"] = [
        build_vehicle(
            vehicle_id=vehicle_id,
            parent_structure_instance_id=None,
            vehicle_class_id="veh.rail_handcart",
            spatial_id="spatial.mob.travel.alpha",
            spec_ids=["spec.mob.travel.vehicle"],
            capability_bindings={},
            port_ids=[],
            interior_graph_id=None,
            pose_slot_ids=[],
            mount_point_ids=[],
            motion_state_ref=motion_state_ref,
            hazard_ids=[],
            maintenance_policy_id="maintenance.policy.default",
            extensions={"fixture_vehicle_gauge_mm": int(max(1, int(vehicle_gauge_mm)))},
        )
    ]
    state["vehicle_motion_states"] = [
        build_motion_state(
            vehicle_id=vehicle_id,
            tier="macro",
            macro_state={},
            meso_state={},
            micro_state={},
            last_update_tick=0,
            extensions={},
        )
    ]
    state.setdefault("mobility_switch_state_machines", [])
    return state
