"""STRICT test: replay policy refuses mutating control actions deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_cannot_mutate_truth"
TEST_TAGS = ["strict", "control", "view", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution

    control_intent = build_control_intent(
        requester_subject_id="agent.replay",
        requested_action_id="action.interaction.execute_process",
        target_kind="structure",
        target_id="assembly.structure.alpha",
        parameters={"process_id": "process.structure_install"},
        abstraction_level_requested="AL1",
        fidelity_requested="meso",
        view_requested="view.replay",
        created_tick=55,
    )
    action_registry = {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "process.structure_install", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["structure"],
                "extensions": {},
            }
        ]
    }
    policy_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.replay.read_only",
                "description": "Replay policy: no truth mutation.",
                "allowed_actions": ["*"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3"],
                "allowed_view_policies": ["view.replay"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {"replay_only": True},
            }
        ]
    }

    result = build_control_resolution(
        control_intent=control_intent,
        law_profile={
            "law_profile_id": "law.test.replay",
            "allowed_processes": ["process.structure_install"],
            "forbidden_processes": [],
        },
        authority_context={
            "authority_origin": "replay",
            "peer_id": "peer.replay",
            "subject_id": "agent.replay",
            "law_profile_id": "law.test.replay",
            "entitlements": ["session.boot"],
            "epistemic_scope": {"scope_id": "epistemic.replay_readonly", "visibility_level": "nondiegetic"},
            "privilege_level": "observer",
        },
        policy_context={
            "control_policy_id": "ctrl.policy.replay.read_only",
            "server_profile_id": "server.profile.replay",
            "pack_lock_hash": "b" * 64,
            "submission_tick": 55,
            "deterministic_sequence_number": 1,
        },
        control_action_registry=action_registry,
        control_policy_registry=policy_registry,
        repo_root=repo_root,
    )

    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "replay mutating action must be refused"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.replay_mutation_forbidden":
        return {"status": "fail", "message": "unexpected replay mutation refusal code"}

    resolution = dict(result.get("resolution") or {})
    if list(resolution.get("emitted_intents") or []):
        return {"status": "fail", "message": "replay mutation refusal must not emit executable intents"}
    return {"status": "pass", "message": "replay mutation refusal check passed"}

