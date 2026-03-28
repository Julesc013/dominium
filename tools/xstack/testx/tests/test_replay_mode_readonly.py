"""STRICT test: replay control policy is read-only."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_mode_readonly"
TEST_TAGS = ["strict", "control", "replay"]


def _action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "structure", "surface"],
                "extensions": {"adapter": "legacy.process_id"},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.view.change_policy",
                "display_name": "View Change",
                "produces": {"process_id": "process.view_bind", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none"],
                "extensions": {},
            },
        ]
    }


def _policy_registry() -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.replay",
                "description": "Replay read-only policy.",
                "allowed_actions": ["action.interaction.*", "action.view.change_policy"],
                "allowed_abstraction_levels": ["AL0", "AL1"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.replay"],
                "allowed_fidelity_ranges": ["macro", "meso"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {"replay_only": True},
            }
        ]
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control import build_control_intent, build_control_resolution

    base_law = {
        "law_profile_id": "law.ctrl9.replay",
        "allowed_processes": ["process.pose_enter", "process.view_bind"],
        "forbidden_processes": [],
    }
    base_authority = {
        "authority_origin": "replay",
        "peer_id": "peer.replay",
        "subject_id": "subject.replay",
        "law_profile_id": "law.ctrl9.replay",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }
    base_policy = {
        "control_policy_id": "ctrl.policy.replay",
        "server_profile_id": "server.profile.replay",
        "pack_lock_hash": "d" * 64,
        "submission_tick": 80,
        "deterministic_sequence_number": 1,
    }

    mutating_intent = build_control_intent(
        requester_subject_id="subject.replay",
        requested_action_id="action.interaction.execute_process",
        parameters={"process_id": "process.pose_enter", "pose_slot_id": "pose.slot.alpha"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.replay",
        created_tick=80,
    )
    mutating = build_control_resolution(
        control_intent=mutating_intent,
        law_profile=base_law,
        authority_context=base_authority,
        policy_context=base_policy,
        control_action_registry=_action_registry(),
        control_policy_registry=_policy_registry(),
        repo_root="",
    )
    if str(mutating.get("result", "")) != "refused":
        return {"status": "fail", "message": "replay policy must refuse mutating process execution"}
    refusal = dict(mutating.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.replay_mutation_forbidden":
        return {"status": "fail", "message": "unexpected replay refusal code for mutating process"}

    readonly_intent = build_control_intent(
        requester_subject_id="subject.replay",
        requested_action_id="action.view.change_policy",
        parameters={"subject_id": "subject.replay", "view_policy_id": "view.mode.first_person"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.replay",
        created_tick=80,
    )
    readonly = build_control_resolution(
        control_intent=readonly_intent,
        law_profile=base_law,
        authority_context=base_authority,
        policy_context=dict(base_policy) | {"deterministic_sequence_number": 2},
        control_action_registry=_action_registry(),
        control_policy_registry=_policy_registry(),
        repo_root="",
    )
    if str(readonly.get("result", "")) != "complete":
        return {"status": "fail", "message": "replay policy should allow view-only control actions"}
    return {"status": "pass", "message": "replay read-only enforcement passed"}

