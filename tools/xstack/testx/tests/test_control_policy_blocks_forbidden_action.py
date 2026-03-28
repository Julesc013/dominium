"""STRICT test: control policy must refuse actions outside allowed_actions."""

from __future__ import annotations

import sys


TEST_ID = "test_control_policy_blocks_forbidden_action"
TEST_TAGS = ["strict", "control", "policy"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control import build_control_intent, build_control_resolution

    intent = build_control_intent(
        requester_subject_id="agent.alpha",
        requested_action_id="action.mount.attach",
        target_kind="mount_point",
        target_id="mount.a",
        parameters={"process_id": "process.mount_attach", "mount_point_a_id": "mount.a", "mount_point_b_id": "mount.b"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=4,
    )
    control_action_registry = {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.mount.attach",
                "display_name": "Attach Mount",
                "produces": {"process_id": "process.mount_attach", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["mount_point"],
                "extensions": {},
            }
        ]
    }
    control_policy_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "Only pose actions are allowed.",
                "allowed_actions": ["action.pose.*"],
                "allowed_abstraction_levels": ["AL0"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            }
        ]
    }
    resolved = build_control_resolution(
        control_intent=intent,
        law_profile={"law_profile_id": "law.test", "allowed_processes": ["process.mount_attach"], "forbidden_processes": []},
        authority_context={
            "authority_origin": "client",
            "peer_id": "peer.test",
            "subject_id": "agent.alpha",
            "law_profile_id": "law.test",
            "entitlements": [],
            "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
            "privilege_level": "operator",
        },
        policy_context={"control_policy_id": "ctrl.policy.player.diegetic", "pack_lock_hash": "a" * 64},
        control_action_registry=control_action_registry,
        control_policy_registry=control_policy_registry,
        repo_root=repo_root,
    )
    if str(resolved.get("result", "")) != "refused":
        return {"status": "fail", "message": "forbidden action should be refused by control policy"}
    refusal = dict(resolved.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.forbidden_by_law":
        return {"status": "fail", "message": "unexpected refusal code for policy-blocked action"}
    return {"status": "pass", "message": "control policy blocks forbidden actions"}
