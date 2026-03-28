"""STRICT test: control resolution enforces action-required capabilities."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_control_resolution_uses_capability"
TEST_TAGS = ["strict", "control", "capability"]


def _control_action_registry() -> dict:
    return {
        "record": {
            "actions": [
                {
                    "schema_version": "1.0.0",
                    "action_id": "action.vehicle.drive",
                    "display_name": "Drive Vehicle",
                    "produces": {
                        "process_id": "process.vehicle_drive",
                        "task_type_id": "",
                        "plan_intent_type": "",
                    },
                    "required_entitlements": [],
                    "required_capabilities": ["capability.can_be_driven"],
                    "target_kinds": ["machine", "structure"],
                    "extensions": {},
                }
            ]
        }
    }


def _control_policy_registry() -> dict:
    return {
        "record": {
            "policies": [
                {
                    "schema_version": "1.0.0",
                    "control_policy_id": "ctrl.policy.player.diegetic",
                    "description": "Test policy",
                    "allowed_actions": ["action.vehicle.drive"],
                    "allowed_abstraction_levels": ["AL0", "AL1"],
                    "allowed_view_policies": ["view.mode.first_person"],
                    "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                    "downgrade_rules": {},
                    "strictness": "C0",
                    "extensions": {},
                }
            ]
        }
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.control.capability",
        "allowed_processes": ["process.vehicle_drive"],
        "forbidden_processes": [],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "client",
        "peer_id": "peer.test.control.capability",
        "subject_id": "subject.driver",
        "law_profile_id": "law.test.control.capability",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }


def _policy_context(bindings: list[dict]) -> dict:
    return {
        "control_policy_id": "ctrl.policy.player.diegetic",
        "pack_lock_hash": "a" * 64,
        "registry_hashes": {},
        "source_shard_id": "shard.0",
        "target_shard_id": "shard.0",
        "submission_tick": 20,
        "deterministic_sequence_number": 1,
        "peer_id": "peer.test.control.capability",
        "capability_bindings": [dict(row) for row in list(bindings or []) if isinstance(row, dict)],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control import build_control_intent, build_control_resolution

    intent = build_control_intent(
        requester_subject_id="subject.driver",
        requested_action_id="action.vehicle.drive",
        target_kind="machine",
        target_id="machine.alpha",
        parameters={"throttle_permille": 350},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=20,
    )
    missing_capability = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context(
            [
                {
                    "entity_id": "machine.alpha",
                    "capability_id": "capability.has_ports",
                    "parameters": {},
                    "created_tick": 20,
                }
            ]
        ),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root=repo_root,
    )
    if str(missing_capability.get("result", "")) != "refused":
        return {"status": "fail", "message": "control resolution should refuse when required capability is missing"}

    refusal = dict(missing_capability.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "refusal.ctrl.forbidden_by_law":
        return {"status": "fail", "message": "capability refusal reason code mismatch: {}".format(str(refusal.get("reason_code", "")))}

    with_capability = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context(
            [
                {
                    "entity_id": "machine.alpha",
                    "capability_id": "capability.can_be_driven",
                    "parameters": {"control_binding_id": "binding.driver.alpha"},
                    "created_tick": 20,
                }
            ]
        ),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root=repo_root,
    )
    if str(with_capability.get("result", "")) != "complete":
        return {"status": "fail", "message": "control resolution unexpectedly refused with required capability bound"}
    emitted = list((dict(with_capability.get("resolution") or {})).get("emitted_intents") or [])
    if not emitted or str((dict(emitted[0])).get("process_id", "")) != "process.vehicle_drive":
        return {"status": "fail", "message": "control resolution did not emit expected process for capability-valid action"}

    return {"status": "pass", "message": "control resolution capability enforcement passed"}

