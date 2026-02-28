"""STRICT test: ranked control resolution downgrades freecam requests deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_freecam_forbidden_in_ranked"
TEST_TAGS = ["strict", "control", "view", "ranked"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution

    control_intent = build_control_intent(
        requester_subject_id="agent.alpha",
        requested_action_id="action.view.change_policy",
        target_kind="none",
        parameters={
            "process_id": "process.view_bind",
            "subject_id": "agent.alpha",
            "camera_id": "camera.main",
            "view_policy_id": "view.freecam_lab",
        },
        abstraction_level_requested="AL1",
        fidelity_requested="meso",
        view_requested="view.freecam_lab",
        created_tick=40,
    )

    action_registry = {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.view.change_policy",
                "display_name": "Change View Policy",
                "produces": {"process_id": "process.view_bind", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.control.camera"],
                "required_capabilities": [],
                "target_kinds": ["none"],
                "extensions": {},
            }
        ]
    }
    policy_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.ranked",
                "description": "Ranked policy with deterministic freecam downgrade.",
                "allowed_actions": ["action.view.*"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "allowed_view_policies": [
                    "view.freecam_lab",
                    "view.third_person_diegetic",
                    "view.first_person_diegetic",
                ],
                "allowed_fidelity_ranges": ["macro", "meso"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            }
        ]
    }
    policy_context = {
        "control_policy_id": "ctrl.policy.player.ranked",
        "server_profile_id": "server.profile.rank_strict",
        "pack_lock_hash": "a" * 64,
        "submission_tick": 40,
        "deterministic_sequence_number": 1,
    }

    result = build_control_resolution(
        control_intent=control_intent,
        law_profile={
            "law_profile_id": "law.test.view.ranked",
            "allowed_processes": ["process.view_bind"],
            "forbidden_processes": [],
        },
        authority_context={
            "authority_origin": "server",
            "peer_id": "peer.alpha",
            "subject_id": "agent.alpha",
            "law_profile_id": "law.test.view.ranked",
            "entitlements": ["entitlement.control.camera"],
            "epistemic_scope": {"scope_id": "epistemic.rank_restricted", "visibility_level": "diegetic"},
            "privilege_level": "observer",
        },
        policy_context=policy_context,
        control_action_registry=action_registry,
        control_policy_registry=policy_registry,
        repo_root=repo_root,
    )

    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "ranked freecam request should downgrade, not refuse"}

    resolution = dict(result.get("resolution") or {})
    resolved_vector = dict(resolution.get("resolved_vector") or {})
    resolved_view = str(resolved_vector.get("view_resolved", "")).strip()
    if not resolved_view or "freecam" in resolved_view.lower():
        return {"status": "fail", "message": "ranked resolution must not keep freecam view"}

    reasons = set(str(item).strip() for item in list(resolution.get("downgrade_reasons") or []) if str(item).strip())
    if "downgrade.rank_fairness" not in reasons:
        return {"status": "fail", "message": "ranked freecam downgrade must include downgrade.rank_fairness"}
    return {"status": "pass", "message": "ranked freecam downgrade check passed"}

