"""FAST test: MOB-10 pose entry requires portal path and respects in-motion transfer policy."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "test_pose_access_requires_portal_path"
TEST_TAGS = ["fast", "mobility", "pose", "interior", "access"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from mobility_interior_testlib import authority_context, law_profile, policy_context, seed_state
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = seed_state(include_vehicle=True, vehicle_position_x=100)
    law = law_profile(["process.pose_enter"])
    auth = authority_context(["entitlement.tool.operating"], privilege_level="operator", visibility_level="diegetic")
    policy = policy_context()
    intent_base = {
        "process_id": "process.pose_enter",
        "inputs": {
            "agent_id": "agent.mob10.alpha",
            "pose_slot_id": "pose.slot.mob10.driver",
            "posture": "posture.sit",
        },
    }

    state["interior_portal_state_machines"] = [
        {
            **dict(row),
            "state_id": "closed"
            if str(dict(row).get("machine_id", "")).strip() == "state.portal.mob10.cabin_hatch"
            else str(dict(row).get("state_id", "closed")),
        }
        for row in list(state.get("interior_portal_state_machines") or [])
        if isinstance(row, dict)
    ]
    state["agent_states"] = [
        {
            **dict(row),
            "interior_volume_id": "volume.mob10.isolated",
            "extensions": {**dict(dict(row).get("extensions") or {}), "interior_volume_id": "volume.mob10.isolated"},
        }
        for row in list(state.get("agent_states") or [])
        if isinstance(row, dict)
    ]

    blocked = execute_intent(
        state=state,
        intent={"intent_id": "intent.mob10.pose.path.blocked.001", **copy.deepcopy(intent_base)},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(blocked.get("result", "")) != "refused":
        return {"status": "fail", "message": "pose_enter should refuse when path portal is closed"}
    if str(dict(blocked.get("refusal") or {}).get("reason_code", "")).strip() != "refusal.pose.no_access_path":
        return {"status": "fail", "message": "closed-path refusal code mismatch"}

    state["agent_states"] = [
        {
            **dict(row),
            "interior_volume_id": "volume.mob10.hold",
            "extensions": {**dict(dict(row).get("extensions") or {}), "interior_volume_id": "volume.mob10.hold"},
        }
        for row in list(state.get("agent_states") or [])
        if isinstance(row, dict)
    ]
    state["interior_portal_state_machines"] = [
        {
            **dict(row),
            "state_id": "open"
            if str(dict(row).get("machine_id", "")).strip() == "state.portal.mob10.cabin_hatch"
            else str(dict(row).get("state_id", "open")),
        }
        for row in list(state.get("interior_portal_state_machines") or [])
        if isinstance(row, dict)
    ]

    moving_restricted = execute_intent(
        state=state,
        intent={"intent_id": "intent.mob10.pose.path.open.001", **copy.deepcopy(intent_base)},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(moving_restricted.get("result", "")) != "refused":
        return {"status": "fail", "message": "pose_enter should refuse cross-compartment transfer while vehicle is moving"}
    if str(dict(moving_restricted.get("refusal") or {}).get("reason_code", "")).strip() != "refusal.pose.movement_restricted":
        return {"status": "fail", "message": "in-motion transfer refusal code mismatch"}

    allowed = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob10.pose.path.open.allowed.001",
            "process_id": "process.pose_enter",
            "inputs": {
                "agent_id": "agent.mob10.alpha",
                "pose_slot_id": "pose.slot.mob10.driver",
                "posture": "posture.sit",
                "allow_compartment_move_while_in_motion": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "pose_enter should succeed when path is open and in-motion transfer policy is allowed"}
    return {"status": "pass", "message": "pose path and moving-seat policy enforcement behaves as expected"}
