"""STRICT test: single-exclusivity pose slot rejects second occupant."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_pose_exclusivity"
TEST_TAGS = ["strict", "pose", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.pose.exclusivity",
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
            "interior_volume_id": "volume.cabin",
            "extensions": {"interior_volume_id": "volume.cabin"},
        },
        {
            "agent_id": "agent.beta",
            "body_id": "body.agent.beta",
            "interior_volume_id": "volume.cabin",
            "extensions": {"interior_volume_id": "volume.cabin"},
        },
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.driver.beta",
            "parent_assembly_id": "assembly.vehicle.beta",
            "interior_volume_id": "volume.cabin",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": False,
            "control_binding_id": "binding.driver_basic",
            "exclusivity": "single",
            "current_occupant_id": "agent.beta",
            "extensions": {"occupant_ids": ["agent.beta"]},
        }
    ]

    intent = {
        "intent_id": "intent.pose.enter.exclusive.001",
        "process_id": "process.pose_enter",
        "inputs": {
            "agent_id": "agent.alpha",
            "pose_slot_id": "pose.slot.driver.beta",
            "posture": "posture.sit",
        },
    }
    auth = authority_context(entitlements=["entitlement.tool.operating"], privilege_level="operator")
    out = execute_intent(
        state=state,
        intent=copy.deepcopy(intent),
        law_profile=_law_profile(),
        authority_context=auth,
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(out.get("result", "")) != "refused":
        return {"status": "fail", "message": "pose_enter should refuse occupied exclusive slot"}
    reason_code = str((dict(out.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.pose.occupied":
        return {"status": "fail", "message": "pose occupied refusal reason mismatch: {}".format(reason_code)}
    return {"status": "pass", "message": "pose exclusivity enforced"}

