"""STRICT test: ranked control policy forbids AL4 meta overrides."""

from __future__ import annotations

import sys


TEST_ID = "test_ranked_no_meta_override"
TEST_TAGS = ["strict", "control", "ranked"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution

    intent = build_control_intent(
        requester_subject_id="subject.admin",
        requested_action_id="action.admin.meta_override",
        target_kind="structure",
        target_id="structure.alpha",
        parameters={"process_id": "process.meta_pose_override"},
        abstraction_level_requested="AL4",
        fidelity_requested="micro",
        view_requested="view.mode.first_person",
        created_tick=19,
    )
    result = build_control_resolution(
        control_intent=intent,
        law_profile={
            "law_profile_id": "law.ctrl9.ranked",
            "allowed_processes": ["process.meta_pose_override"],
            "forbidden_processes": [],
        },
        authority_context={
            "authority_origin": "client",
            "peer_id": "peer.rank",
            "subject_id": "subject.admin",
            "law_profile_id": "law.ctrl9.ranked",
            "entitlements": ["entitlement.control.admin"],
            "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
            "privilege_level": "admin",
        },
        policy_context={
            "control_policy_id": "ctrl.policy.admin.meta",
            "server_profile_id": "server.profile.ranked.strict",
            "ranked_server": True,
            "pack_lock_hash": "c" * 64,
            "submission_tick": 19,
            "deterministic_sequence_number": 1,
        },
        control_action_registry={
            "actions": [
                {
                    "schema_version": "1.0.0",
                    "action_id": "action.admin.meta_override",
                    "display_name": "Meta Override",
                    "produces": {"process_id": "process.meta_pose_override", "task_type_id": "", "plan_intent_type": ""},
                    "required_entitlements": ["entitlement.control.admin"],
                    "required_capabilities": [],
                    "target_kinds": ["structure"],
                    "extensions": {},
                }
            ]
        },
        control_policy_registry={
            "policies": [
                {
                    "schema_version": "1.0.0",
                    "control_policy_id": "ctrl.policy.admin.meta",
                    "description": "Admin meta policy.",
                    "allowed_actions": ["action.admin.meta_override"],
                    "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                    "allowed_view_policies": ["view.mode.first_person"],
                    "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                    "downgrade_rules": {},
                    "strictness": "C2",
                    "extensions": {},
                }
            ]
        },
        repo_root="",
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "ranked AL4 meta override must be refused"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.meta_forbidden":
        return {"status": "fail", "message": "unexpected refusal code for ranked meta override"}
    return {"status": "pass", "message": "ranked meta override gating passed"}

