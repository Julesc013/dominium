"""FAST test: vehicle registration validates and persists port/pose/interior refs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.vehicle_ports_pose_interior_refs_valid"
TEST_TAGS = ["fast", "mobility", "vehicle", "ports", "pose", "interior"]


def _law_profile() -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile

    law = law_profile(["process.vehicle_register_from_structure"])
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    entitlements["process.vehicle_register_from_structure"] = "entitlement.control.admin"
    privileges["process.vehicle_register_from_structure"] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _seed_state() -> dict:
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = base_state()
    state["installed_structure_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "assembly.structure_instance.vehicle.refs",
            "project_id": "project.construction.vehicle.refs",
            "ag_id": "ag.vehicle.refs",
            "site_ref": "site.vehicle.refs",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {"spatial_id": "spatial.vehicle.refs"},
        }
    ]
    state["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": "port.vehicle.refs.cargo",
            "machine_id": None,
            "parent_structure_id": "assembly.structure_instance.vehicle.refs",
            "port_type_id": "port.cargo",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": 1000,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": None,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "port_id": "port.vehicle.refs.fuel",
            "machine_id": None,
            "parent_structure_id": "assembly.structure_instance.vehicle.refs",
            "port_type_id": "port.fluid",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": 500,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": None,
            "extensions": {},
        },
    ]
    state["interior_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.vehicle.refs",
            "volumes": ["interior.volume.vehicle.refs"],
            "portals": [],
            "extensions": {},
        }
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.vehicle.refs.driver",
            "parent_assembly_id": "assembly.structure_instance.vehicle.refs",
            "interior_volume_id": "interior.volume.vehicle.refs",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": False,
            "control_binding_id": "control.binding.driver",
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {"driver_station": True},
        },
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.vehicle.refs.passenger",
            "parent_assembly_id": "assembly.structure_instance.vehicle.refs",
            "interior_volume_id": "interior.volume.vehicle.refs",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": False,
            "control_binding_id": None,
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {},
        },
    ]
    state["mount_points"] = [
        {
            "schema_version": "1.0.0",
            "mount_point_id": "mount.point.vehicle.refs.front",
            "parent_assembly_id": "assembly.structure_instance.vehicle.refs",
            "mount_tags": ["mount.coupler"],
            "alignment_constraints": {},
            "state_machine_id": "sm.mount.vehicle.refs.front",
            "connected_to_mount_point_id": None,
            "extensions": {},
        }
    ]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, policy_context

    state = _seed_state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.vehicle.refs.register.001",
            "process_id": "process.vehicle_register_from_structure",
            "inputs": {
                "parent_structure_instance_id": "assembly.structure_instance.vehicle.refs",
                "vehicle_class_id": "veh.road_cart",
                "created_tick_bucket": 2,
                "spec_ids": ["spec.vehicle.refs.base"],
                "port_ids": ["port.vehicle.refs.cargo", "port.vehicle.refs.fuel"],
                "interior_graph_id": "interior.graph.vehicle.refs",
                "pose_slot_ids": [
                    "pose.slot.vehicle.refs.driver",
                    "pose.slot.vehicle.refs.passenger",
                ],
                "mount_point_ids": ["mount.point.vehicle.refs.front"],
                "maintenance_policy_id": "maintenance.policy.default",
            },
        },
        law_profile=_law_profile(),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle registration refused with valid refs fixture"}

    vehicle_id = str(result.get("vehicle_id", "")).strip()
    if not vehicle_id:
        return {"status": "fail", "message": "vehicle registration did not return vehicle_id"}
    driver_pose_slots = sorted(
        set(str(item).strip() for item in list(result.get("driver_pose_slot_ids") or []) if str(item).strip())
    )
    if driver_pose_slots != [
        "pose.slot.vehicle.refs.driver",
        "pose.slot.vehicle.refs.passenger",
    ]:
        return {
            "status": "fail",
            "message": "driver pose slot metadata did not resolve declared pose slot references",
        }
    returned_ports = sorted(set(str(item).strip() for item in list(result.get("vehicle_ports") or []) if str(item).strip()))
    if returned_ports != ["port.vehicle.refs.cargo", "port.vehicle.refs.fuel"]:
        return {"status": "fail", "message": "vehicle_ports result metadata did not preserve declared ports"}
    if str(result.get("interior_graph_id", "")).strip() != "interior.graph.vehicle.refs":
        return {"status": "fail", "message": "interior_graph_id metadata missing or incorrect"}

    vehicle_rows = [
        dict(row) for row in list(state.get("vehicles") or []) if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == vehicle_id
    ]
    if len(vehicle_rows) != 1:
        return {"status": "fail", "message": "vehicle row missing after successful registration"}
    vehicle_row = dict(vehicle_rows[0])
    if sorted(list(vehicle_row.get("port_ids") or [])) != ["port.vehicle.refs.cargo", "port.vehicle.refs.fuel"]:
        return {"status": "fail", "message": "vehicle row port_ids mismatch after normalization"}
    if str(vehicle_row.get("interior_graph_id", "")).strip() != "interior.graph.vehicle.refs":
        return {"status": "fail", "message": "vehicle row interior_graph_id mismatch after normalization"}
    if sorted(list(vehicle_row.get("pose_slot_ids") or [])) != [
        "pose.slot.vehicle.refs.driver",
        "pose.slot.vehicle.refs.passenger",
    ]:
        return {"status": "fail", "message": "vehicle row pose_slot_ids mismatch after normalization"}
    if sorted(list(vehicle_row.get("mount_point_ids") or [])) != ["mount.point.vehicle.refs.front"]:
        return {"status": "fail", "message": "vehicle row mount_point_ids mismatch after normalization"}

    return {"status": "pass", "message": "vehicle registration persists valid port/pose/interior/mount references"}
