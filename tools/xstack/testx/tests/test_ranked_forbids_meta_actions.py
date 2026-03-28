"""STRICT test: ranked contexts must reject AL4 meta control actions."""

from __future__ import annotations

import sys


TEST_ID = "test_ranked_forbids_meta_actions"
TEST_TAGS = ["strict", "control", "ranked"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control import build_control_intent, build_control_resolution

    intent = build_control_intent(
        requester_subject_id="agent.admin",
        requested_action_id="action.admin.meta_override",
        target_kind="pose_slot",
        target_id="pose.slot.alpha",
        parameters={"process_id": "process.meta_pose_override"},
        abstraction_level_requested="AL4",
        fidelity_requested="micro",
        view_requested="view.mode.first_person",
        created_tick=9,
    )
    control_action_registry = {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.admin.meta_override",
                "display_name": "Meta Override",
                "produces": {"process_id": "process.meta_pose_override", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.control.admin"],
                "required_capabilities": ["capability.meta.override"],
                "target_kinds": ["pose_slot", "mount_point", "structure"],
                "extensions": {},
            }
        ]
    }
    control_policy_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.admin.meta",
                "description": "Admin meta policy.",
                "allowed_actions": ["*"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {"meta_allowed": True},
            }
        ]
    }
    resolved = build_control_resolution(
        control_intent=intent,
        law_profile={"law_profile_id": "law.test.meta", "allowed_processes": ["process.meta_pose_override"], "forbidden_processes": []},
        authority_context={
            "authority_origin": "client",
            "peer_id": "peer.rank",
            "subject_id": "agent.admin",
            "law_profile_id": "law.test.meta",
            "entitlements": ["entitlement.control.admin"],
            "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
            "privilege_level": "operator",
        },
        policy_context={
            "control_policy_id": "ctrl.policy.admin.meta",
            "ranked_server": True,
            "server_profile_id": "server.policy.ranked.strict",
            "pack_lock_hash": "a" * 64,
        },
        control_action_registry=control_action_registry,
        control_policy_registry=control_policy_registry,
        repo_root=repo_root,
    )
    if str(resolved.get("result", "")) != "refused":
        return {"status": "fail", "message": "ranked AL4 request should be refused"}
    refusal = dict(resolved.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.meta_forbidden":
        return {"status": "fail", "message": "unexpected refusal code for ranked meta action"}
    return {"status": "pass", "message": "ranked servers refuse AL4 meta control actions"}
