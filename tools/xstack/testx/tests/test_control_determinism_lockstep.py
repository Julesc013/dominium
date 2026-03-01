"""STRICT test: lockstep control decisions remain deterministic across peers."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_control_determinism_lockstep"
TEST_TAGS = ["strict", "control", "multiplayer", "determinism"]


def _control_action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "surface", "structure"],
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
                "description": "Lockstep deterministic baseline policy.",
                "allowed_actions": ["action.interaction.*"],
                "allowed_abstraction_levels": ["AL0", "AL1"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {},
            }
        ]
    }


def _decision_surface_hash(resolution: dict, canonical_sha256) -> str:
    payload = {
        "allowed": bool(resolution.get("allowed", False)),
        "resolved_vector": dict(resolution.get("resolved_vector") or {}),
        "downgrade_reasons": list(resolution.get("downgrade_reasons") or []),
        "refusal_reason_code": str((dict(resolution.get("refusal") or {})).get("reason_code", "")),
    }
    return canonical_sha256(payload)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import (
        build_control_intent,
        build_control_resolution,
        validate_control_ir_multiplayer,
    )
    from tools.xstack.compatx.canonical_json import canonical_sha256

    intent = build_control_intent(
        requester_subject_id="subject.lockstep",
        requested_action_id="action.interaction.execute_process",
        target_kind="none",
        target_id=None,
        parameters={"process_id": "process.inspect_generate_snapshot", "target_id": "structure.alpha"},
        abstraction_level_requested="AL1",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=44,
    )
    law_profile = {
        "law_profile_id": "law.ctrl9.lockstep",
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "forbidden_processes": [],
    }
    authority_template = {
        "authority_origin": "client",
        "subject_id": "subject.lockstep",
        "law_profile_id": "law.ctrl9.lockstep",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }
    policy_template = {
        "control_policy_id": "ctrl.policy.player.diegetic",
        "server_profile_id": "server.profile.lockstep.strict",
        "net_policy_id": "policy.net.lockstep",
        "pack_lock_hash": "a" * 64,
        "submission_tick": 44,
        "deterministic_sequence_number": 9,
    }

    peer_one = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law_profile),
        authority_context=dict(authority_template) | {"peer_id": "peer.one"},
        policy_context=dict(policy_template) | {"peer_id": "peer.one"},
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root="",
    )
    peer_two = build_control_resolution(
        control_intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law_profile),
        authority_context=dict(authority_template) | {"peer_id": "peer.two"},
        policy_context=dict(policy_template) | {"peer_id": "peer.two"},
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root="",
    )
    if str(peer_one.get("result", "")) != "complete" or str(peer_two.get("result", "")) != "complete":
        return {"status": "fail", "message": "lockstep control decision refused unexpectedly"}

    one_resolution = dict(peer_one.get("resolution") or {})
    two_resolution = dict(peer_two.get("resolution") or {})
    if _decision_surface_hash(one_resolution, canonical_sha256) != _decision_surface_hash(two_resolution, canonical_sha256):
        return {"status": "fail", "message": "lockstep decision surface drifted across peers"}

    mp_mode = validate_control_ir_multiplayer(
        ir_program={"control_ir_id": "control.ir.lockstep.demo"},
        verification_report={"valid": True, "deterministic_fingerprint": "b" * 64},
        policy_context={"net_policy_id": "policy.net.lockstep"},
    )
    if str(mp_mode.get("result", "")) != "complete":
        return {"status": "fail", "message": "lockstep multiplayer validation unexpectedly refused"}
    if str(mp_mode.get("client_resolution_payload", "")) != "resolved_vector_only":
        return {"status": "fail", "message": "lockstep mode must expose resolved_vector_only payload to clients"}

    return {"status": "pass", "message": "lockstep control determinism baseline passed"}

