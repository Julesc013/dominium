"""STRICT test: pose_enter enforces interior access-path requirement."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_pose_access_path_required"
TEST_TAGS = ["strict", "pose", "interior", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.pose.path",
        "allowed_processes": ["process.pose_enter"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.pose_enter": "entitlement.tool.operating",
        },
        "process_privilege_requirements": {
            "process.pose_enter": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state = base_state()
    state["agent_states"] = [
        {
            "agent_id": "agent.alpha",
            "body_id": "body.agent.alpha",
            "interior_volume_id": "volume.a",
            "extensions": {"interior_volume_id": "volume.a"},
        }
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.driver.alpha",
            "parent_assembly_id": "assembly.vehicle.alpha",
            "interior_volume_id": "volume.b",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": True,
            "control_binding_id": "binding.driver_basic",
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {"interior_graph_id": "interior.graph.alpha"},
        }
    ]
    state["interior_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.alpha",
            "volumes": ["volume.a", "volume.b"],
            "portals": ["portal.ab"],
            "extensions": {},
        }
    ]
    state["interior_volumes"] = [
        {"volume_id": "volume.a"},
        {"volume_id": "volume.b"},
    ]
    state["interior_portals"] = [
        {
            "portal_id": "portal.ab",
            "from_volume_id": "volume.a",
            "to_volume_id": "volume.b",
            "portal_type_id": "portal.door",
            "state_machine_id": "state.portal.ab",
            "sealing_coefficient": 1000,
            "tags": [],
            "extensions": {},
        }
    ]
    state["interior_portal_state_machines"] = [
        {
            "machine_id": "state.portal.ab",
            "state_id": "closed",
            "extensions": {},
        }
    ]

    intent = {
        "intent_id": "intent.pose.enter.path.001",
        "process_id": "process.pose_enter",
        "inputs": {
            "agent_id": "agent.alpha",
            "pose_slot_id": "pose.slot.driver.alpha",
            "posture": "posture.sit",
        },
    }
    auth = authority_context(entitlements=["entitlement.tool.operating"], privilege_level="operator")
    law = _law_profile()
    policy = policy_context()
    out = execute_intent(
        state=state,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(out.get("result", "")) != "refused":
        return {"status": "fail", "message": "pose_enter should refuse when portal path is closed"}
    reason_code = str((dict(out.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.pose.no_access_path":
        return {"status": "fail", "message": "pose_enter refusal reason mismatch: {}".format(reason_code)}
    return {"status": "pass", "message": "pose access-path requirement enforced"}

