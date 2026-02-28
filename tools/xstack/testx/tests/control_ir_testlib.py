"""Shared deterministic fixtures for Control IR TestX coverage."""

from __future__ import annotations

import copy


def capability_registry() -> dict:
    return {
        "capabilities": [
            {"capability_id": "capability.pose.enter"},
            {"capability_id": "capability.pose.exit"},
            {"capability_id": "capability.surface.execute"},
        ]
    }


def control_action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.pose.enter",
                "display_name": "Enter Pose",
                "produces": {"process_id": "process.pose_enter", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.agent.move"],
                "required_capabilities": ["capability.pose.enter"],
                "target_kinds": ["pose_slot"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.pose.exit",
                "display_name": "Exit Pose",
                "produces": {"process_id": "process.pose_exit", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.agent.move"],
                "required_capabilities": ["capability.pose.exit"],
                "target_kinds": ["pose_slot"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.surface.execute_task",
                "display_name": "Surface Task",
                "produces": {"process_id": "process.task_create", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.tool.use"],
                "required_capabilities": ["capability.surface.execute"],
                "target_kinds": ["surface"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "surface", "pose_slot", "mount_point", "machine", "structure", "graph"],
                "extensions": {"adapter": "legacy.process_id"},
            },
        ]
    }


def control_policy_row() -> dict:
    return {
        "schema_version": "1.0.0",
        "control_policy_id": "ctrl.policy.player.assisted",
        "description": "AL1 assisted control policy",
        "allowed_actions": ["action.interaction.*", "action.surface.*", "action.pose.*"],
        "allowed_abstraction_levels": ["AL0", "AL1"],
        "allowed_view_policies": ["view.mode.first_person", "view.mode.third_person"],
        "allowed_fidelity_ranges": ["macro", "meso", "micro"],
        "downgrade_rules": {},
        "strictness": "C0",
        "extensions": {},
    }


def control_policy_registry() -> dict:
    return {"policies": [dict(control_policy_row())]}


def authority_context() -> dict:
    return {
        "authority_origin": "client",
        "peer_id": "peer.test.ir",
        "subject_id": "agent.alpha",
        "law_profile_id": "law.test.ir",
        "entitlements": [
            "entitlement.tool.operating",
            "entitlement.tool.use",
            "entitlement.agent.move",
        ],
        "epistemic_scope": {"scope_id": "scope.test.ir", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }


def law_profile() -> dict:
    return {
        "law_profile_id": "law.test.ir",
        "allowed_processes": [
            "process.pose_enter",
            "process.task_create",
            "process.pose_exit",
            "process.commitment_create",
        ],
        "forbidden_processes": [],
    }


def base_policy_context() -> dict:
    return {
        "control_policy_id": "ctrl.policy.player.assisted",
        "submission_tick": 4,
        "deterministic_sequence_number": 1,
        "pack_lock_hash": "a" * 64,
    }


def autopilot_ir() -> dict:
    from src.control import build_autopilot_stub_ir

    return build_autopilot_stub_ir(controller_id="agent.alpha", tick=4)


def deep_copy_inputs() -> dict:
    return {
        "ir_program": copy.deepcopy(autopilot_ir()),
        "control_policy": copy.deepcopy(control_policy_row()),
        "authority_context": copy.deepcopy(authority_context()),
        "capability_registry": copy.deepcopy(capability_registry()),
        "law_profile": copy.deepcopy(law_profile()),
        "control_action_registry": copy.deepcopy(control_action_registry()),
        "control_policy_registry": copy.deepcopy(control_policy_registry()),
        "policy_context": copy.deepcopy(base_policy_context()),
    }

