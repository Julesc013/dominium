"""FAST test: vehicle-edge spec mismatch emits deterministic compatibility refusal."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.spec_compatibility_refusal"
TEST_TAGS = ["fast", "mobility", "vehicle", "spec", "refusal"]


def _law_profile() -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(
        [
            "process.vehicle_register_from_structure",
            "process.vehicle_check_compatibility",
        ]
    )
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.vehicle_register_from_structure"] = "entitlement.control.admin"
    privileges["process.vehicle_register_from_structure"] = "operator"
    entitlements["process.vehicle_check_compatibility"] = "entitlement.inspect"
    privileges["process.vehicle_check_compatibility"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _seed_state() -> dict:
    from mobility.geometry import build_geometry_metric_row, build_guide_geometry
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["installed_structure_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "assembly.structure_instance.vehicle.spec",
            "project_id": "project.construction.vehicle.spec",
            "ag_id": "ag.vehicle.spec",
            "site_ref": "site.vehicle.spec",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {"spatial_id": "spatial.vehicle.spec"},
        }
    ]
    state["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": "port.vehicle.spec.cargo",
            "machine_id": None,
            "parent_structure_id": "assembly.structure_instance.vehicle.spec",
            "port_type_id": "port.cargo",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": 1000,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": None,
            "extensions": {},
        }
    ]
    geometry = build_guide_geometry(
        geometry_id="geometry.vehicle.spec.edge",
        geometry_type_id="geo.spline1D",
        parent_spatial_id="spatial.vehicle.spec",
        spec_id="spec.edge.track.g1435",
        parameters={
            "control_points_mm": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 5000, "y": 0, "z": 0},
            ],
            "clearance_width_mm": 4000,
            "clearance_height_mm": 4500,
        },
        junction_refs=[],
        extensions={},
    )
    state["guide_geometries"] = [geometry]
    state["geometry_derived_metrics"] = [
        build_geometry_metric_row(
            geometry_row=geometry,
            current_tick=0,
            max_cost_units=8,
            cost_units_per_metric=1,
        )
    ]
    state["network_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "graph.mobility.vehicle.spec",
            "validation_mode": "warn",
            "node_type_schema_id": "",
            "edge_type_schema_id": "",
            "payload_schema_versions": {},
            "graph_partition_id": None,
            "deterministic_routing_policy_id": "route.shortest_delay",
            "nodes": [
                {
                    "schema_version": "1.0.0",
                    "node_id": "node.vehicle.spec.a",
                    "node_type_id": "mobility_node",
                    "payload": {"node_kind": "endpoint"},
                    "tags": [],
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "node_id": "node.vehicle.spec.b",
                    "node_type_id": "mobility_node",
                    "payload": {"node_kind": "endpoint"},
                    "tags": [],
                    "extensions": {},
                },
            ],
            "edges": [
                {
                    "schema_version": "1.0.0",
                    "edge_id": "edge.vehicle.spec.main",
                    "from_node_id": "node.vehicle.spec.a",
                    "to_node_id": "node.vehicle.spec.b",
                    "edge_type_id": "mobility_edge",
                    "capacity": None,
                    "delay_ticks": 0,
                    "loss_fraction": 0,
                    "cost_units": 1,
                    "payload": {
                        "edge_kind": "track",
                        "guide_geometry_id": "geometry.vehicle.spec.edge",
                        "spec_id": "spec.edge.track.g1435",
                    },
                    "tags": [],
                    "extensions": {},
                }
            ],
            "extensions": {},
        }
    ]
    return state


def _policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context

    policy = policy_context()
    policy["spec_sheet_rows"] = [
        {
            "schema_version": "1.0.0",
            "spec_id": "spec.vehicle.track.g1000",
            "spec_type_id": "spec.track",
            "description": "Vehicle gauge 1000",
            "parameters": {
                "gauge_mm": 1000,
                "clearance_width_mm": 3000,
                "clearance_height_mm": 3000,
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "spec_id": "spec.edge.track.g1435",
            "spec_type_id": "spec.track",
            "description": "Edge gauge 1435",
            "parameters": {
                "gauge_mm": 1435,
                "clearance_width_mm": 3000,
                "clearance_height_mm": 3000,
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
    ]
    return policy


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context

    state = _seed_state()
    law = _law_profile()
    policy = _policy_context()
    admin_auth = authority_context(["entitlement.control.admin"], privilege_level="operator")
    inspect_auth = authority_context(["entitlement.inspect"], privilege_level="observer")

    register_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.vehicle.spec.register.001",
            "process_id": "process.vehicle_register_from_structure",
            "inputs": {
                "parent_structure_instance_id": "assembly.structure_instance.vehicle.spec",
                "vehicle_class_id": "veh.rail_handcart",
                "created_tick_bucket": 3,
                "spec_ids": ["spec.vehicle.track.g1000"],
                "port_ids": ["port.vehicle.spec.cargo"],
                "tier": "meso",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(admin_auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(register_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle registration failed in spec compatibility fixture"}
    vehicle_id = str(register_result.get("vehicle_id", "")).strip()
    if not vehicle_id:
        return {"status": "fail", "message": "vehicle registration did not return vehicle_id"}

    compatibility_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.vehicle.spec.compat.001",
            "process_id": "process.vehicle_check_compatibility",
            "inputs": {
                "vehicle_id": vehicle_id,
                "target_edge_id": "edge.vehicle.spec.main",
                "enforce": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(inspect_auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(compatibility_result.get("result", "")) == "complete":
        return {"status": "fail", "message": "expected compatibility refusal but process completed"}
    refusal_row = dict(compatibility_result.get("refusal") or {})
    reason_code = str(refusal_row.get("reason_code", "")).strip()
    if reason_code != "refusal.mob.spec_noncompliant":
        return {"status": "fail", "message": "unexpected refusal code '{}'".format(reason_code)}

    result_rows = [dict(row) for row in list(state.get("vehicle_compatibility_results") or []) if isinstance(row, dict)]
    if not result_rows:
        return {"status": "fail", "message": "compatibility result row was not persisted before refusal"}
    latest = sorted(result_rows, key=lambda row: str(row.get("result_id", "")))[-1]
    if bool(latest.get("compatible", True)):
        return {"status": "fail", "message": "persisted compatibility row unexpectedly marked compatible"}
    return {"status": "pass", "message": "spec mismatch emits deterministic refusal.mob.spec_noncompliant"}

