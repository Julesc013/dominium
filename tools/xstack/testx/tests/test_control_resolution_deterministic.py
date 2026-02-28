"""STRICT test: control resolution must be deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_control_resolution_deterministic"
TEST_TAGS = ["strict", "control", "determinism"]


def _control_action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {
                    "process_id": "",
                    "task_type_id": "",
                    "plan_intent_type": "",
                },
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "surface", "pose_slot", "mount_point", "machine", "structure", "graph"],
                "extensions": {"adapter": "legacy.process_id"},
            }
        ]
    }


def _control_policy_registry() -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "Diegetic AL0 baseline policy.",
                "allowed_actions": ["action.interaction.*"],
                "allowed_abstraction_levels": ["AL0"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            }
        ]
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution
    from tools.xstack.compatx.canonical_json import canonical_sha256

    law_profile = {
        "law_profile_id": "law.test.control.det",
        "allowed_processes": ["process.pose_enter"],
        "forbidden_processes": [],
    }
    authority_context = {
        "authority_origin": "client",
        "peer_id": "peer.test.control",
        "subject_id": "agent.alpha",
        "law_profile_id": "law.test.control.det",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }
    policy_context = {
        "control_policy_id": "ctrl.policy.player.diegetic",
        "pack_lock_hash": "a" * 64,
        "registry_hashes": {},
        "source_shard_id": "shard.0",
        "target_shard_id": "shard.0",
        "submission_tick": 12,
        "deterministic_sequence_number": 1,
        "peer_id": "peer.test.control",
    }
    intent = build_control_intent(
        requester_subject_id="agent.alpha",
        requested_action_id="action.interaction.execute_process",
        target_kind="none",
        target_id=None,
        parameters={"process_id": "process.pose_enter", "pose_slot_id": "pose.slot.alpha"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=12,
    )

    first = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(authority_context),
        policy_context=copy.deepcopy(policy_context),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root=repo_root,
    )
    second = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(authority_context),
        policy_context=copy.deepcopy(policy_context),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root=repo_root,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "control resolution unexpectedly refused"}

    first_resolution = dict(first.get("resolution") or {})
    second_resolution = dict(second.get("resolution") or {})
    if canonical_sha256(first_resolution) != canonical_sha256(second_resolution):
        return {"status": "fail", "message": "control resolution payload drift for identical inputs"}
    return {"status": "pass", "message": "control resolution deterministic for identical inputs"}
