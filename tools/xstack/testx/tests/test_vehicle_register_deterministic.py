"""FAST test: vehicle registration is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.vehicle_register_deterministic"
TEST_TAGS = ["fast", "mobility", "vehicle", "determinism"]


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
            "instance_id": "assembly.structure_instance.vehicle.det",
            "project_id": "project.construction.vehicle.det",
            "ag_id": "ag.vehicle.det",
            "site_ref": "site.vehicle.det",
            "installed_node_states": [],
            "maintenance_backlog": {},
            "extensions": {"spatial_id": "spatial.vehicle.det"},
        }
    ]
    state["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": "port.vehicle.det.cargo",
            "machine_id": None,
            "parent_structure_id": "assembly.structure_instance.vehicle.det",
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
    state["interior_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.vehicle.det",
            "volumes": ["interior.volume.vehicle.det"],
            "portals": [],
            "extensions": {},
        }
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.vehicle.det.driver",
            "parent_assembly_id": "assembly.structure_instance.vehicle.det",
            "interior_volume_id": "interior.volume.vehicle.det",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": False,
            "control_binding_id": "control.binding.driver",
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {"driver_station": True},
        }
    ]
    state["mount_points"] = [
        {
            "schema_version": "1.0.0",
            "mount_point_id": "mount.point.vehicle.det.coupler",
            "parent_assembly_id": "assembly.structure_instance.vehicle.det",
            "mount_tags": ["mount.coupler"],
            "alignment_constraints": {},
            "state_machine_id": "sm.mount.vehicle.det.coupler",
            "connected_to_mount_point_id": None,
            "extensions": {},
        }
    ]
    return state


def _intent() -> dict:
    return {
        "intent_id": "intent.mob.vehicle.register.det.001",
        "process_id": "process.vehicle_register_from_structure",
        "inputs": {
            "parent_structure_instance_id": "assembly.structure_instance.vehicle.det",
            "vehicle_class_id": "veh.rail_handcart",
            "created_tick_bucket": 5,
            "spec_ids": ["spec.vehicle.det.base"],
            "port_ids": ["port.vehicle.det.cargo"],
            "interior_graph_id": "interior.graph.vehicle.det",
            "pose_slot_ids": ["pose.slot.vehicle.det.driver"],
            "mount_point_ids": ["mount.point.vehicle.det.coupler"],
            "maintenance_policy_id": "maintenance.policy.default",
            "capability_bindings": {"driver_control": "control.binding.driver"},
            "extensions": {"field_cell_id": "cell.vehicle.det"},
        },
    }


def _policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context

    return policy_context()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context

    law = _law_profile()
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    policy = _policy_context()
    intent = _intent()

    state_a = _seed_state()
    state_b = _seed_state()

    first = execute_intent(
        state=state_a,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state_b,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle registration refused in deterministic fixture"}
    if str(first.get("vehicle_id", "")).strip() != str(second.get("vehicle_id", "")).strip():
        return {"status": "fail", "message": "vehicle_id drifted across equivalent registration runs"}
    if list(state_a.get("vehicles") or []) != list(state_b.get("vehicles") or []):
        return {"status": "fail", "message": "vehicle rows drifted across equivalent registration runs"}
    if list(state_a.get("vehicle_motion_states") or []) != list(state_b.get("vehicle_motion_states") or []):
        return {"status": "fail", "message": "vehicle motion-state rows drifted across equivalent runs"}
    if list(state_a.get("vehicle_events") or []) != list(state_b.get("vehicle_events") or []):
        return {"status": "fail", "message": "vehicle event rows drifted across equivalent runs"}
    return {"status": "pass", "message": "vehicle registration deterministic for equivalent structure inputs"}

