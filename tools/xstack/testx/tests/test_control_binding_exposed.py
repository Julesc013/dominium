"""STRICT test: occupied pose control binding grants are exposed to affordance metadata."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_control_binding_exposed"
TEST_TAGS = ["strict", "pose", "affordance", "control_binding"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.pose.control_binding",
        "allowed_processes": ["process.pose_enter", "process.machine_operate"],
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

    from src.client.interaction.affordance_generator import build_affordance_list
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state = base_state()
    state["agent_states"] = [
        {
            "agent_id": "agent.alpha",
            "body_id": "body.agent.alpha",
            "interior_volume_id": "volume.driver",
            "extensions": {"interior_volume_id": "volume.driver"},
        }
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.driver.alpha",
            "parent_assembly_id": "assembly.vehicle.alpha",
            "interior_volume_id": "volume.driver",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": False,
            "control_binding_id": "binding.driver_basic",
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {},
        }
    ]

    policy = policy_context()
    policy["control_binding_registry"] = {
        "control_bindings": [
            {
                "schema_version": "1.0.0",
                "control_binding_id": "binding.driver_basic",
                "grants_process_ids": ["process.machine_operate"],
                "grants_surface_ids": ["surface.driver.console"],
                "extensions": {},
            }
        ]
    }
    auth = authority_context(entitlements=["entitlement.tool.operating"], privilege_level="operator")

    enter_intent = {
        "intent_id": "intent.pose.enter.control.001",
        "process_id": "process.pose_enter",
        "inputs": {
            "agent_id": "agent.alpha",
            "pose_slot_id": "pose.slot.driver.alpha",
            "posture": "posture.sit",
        },
    }
    entered = execute_intent(
        state=state,
        intent=copy.deepcopy(enter_intent),
        law_profile=_law_profile(),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=policy,
    )
    if str(entered.get("result", "")) != "complete":
        return {"status": "fail", "message": "pose_enter refused unexpectedly"}
    granted = sorted(set(str(item).strip() for item in list(entered.get("granted_process_ids") or []) if str(item).strip()))
    if "process.machine_operate" not in set(granted):
        return {"status": "fail", "message": "pose_enter result missing granted process id"}

    agent_extensions = {}
    for row in list(state.get("agent_states") or []):
        if str((dict(row)).get("agent_id", "")).strip() == "agent.alpha":
            agent_extensions = dict((dict(row)).get("extensions") or {})
            break
    if "process.machine_operate" not in set(str(item).strip() for item in list(agent_extensions.get("pose_granted_process_ids") or [])):
        return {"status": "fail", "message": "agent state missing pose_granted_process_ids"}

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 5},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "agent.alpha",
                    "semantic_id": "agent.alpha",
                    "entity_kind": "agent",
                    "extensions": dict(agent_extensions),
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }
    interaction_action_registry = {
        "actions": [
            {
                "action_id": "interaction.machine_operate",
                "process_id": "process.machine_operate",
                "display_name": "Operate Machine",
                "target_kinds": ["agent"],
                "parameter_schema_id": None,
                "preview_mode": "cheap",
                "required_lens_channels": [],
                "default_ui_hints": {},
                "extensions": {},
            }
        ]
    }
    affordance_out = build_affordance_list(
        perceived_model=perceived_model,
        target_semantic_id="agent.alpha",
        law_profile=_law_profile(),
        authority_context=auth,
        interaction_action_registry=interaction_action_registry,
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(affordance_out.get("result", "")) != "complete":
        return {"status": "fail", "message": "affordance generation refused unexpectedly"}
    affordance_list = dict(affordance_out.get("affordance_list") or {})
    pose_grants = dict((dict(affordance_list.get("extensions") or {})).get("pose_control_grants") or {})
    granted_process_ids = set(str(item).strip() for item in list(pose_grants.get("granted_process_ids") or []))
    if "process.machine_operate" not in granted_process_ids:
        return {"status": "fail", "message": "affordance list missing pose control grant process metadata"}
    rows = [dict(item) for item in list(affordance_list.get("affordances") or []) if isinstance(item, dict)]
    if not rows:
        return {"status": "fail", "message": "expected affordance row for granted process"}
    if not any(bool(dict(row.get("extensions") or {}).get("pose_control_granted_process", False)) for row in rows):
        return {"status": "fail", "message": "affordance rows missing pose_control_granted_process marker"}
    return {"status": "pass", "message": "pose control binding grants exposed to affordance metadata"}

