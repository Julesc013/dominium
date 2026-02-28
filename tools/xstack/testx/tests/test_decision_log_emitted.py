"""STRICT test: control resolutions must emit deterministic decision log artifacts."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_decision_log_emitted"
TEST_TAGS = ["strict", "control", "audit"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution
    from tools.xstack.compatx.validator import validate_instance

    intent = build_control_intent(
        requester_subject_id="agent.alpha",
        requested_action_id="action.interaction.execute_process",
        target_kind="none",
        parameters={"process_id": "process.pose_enter", "pose_slot_id": "pose.slot.alpha"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=10,
    )
    resolved = build_control_resolution(
        control_intent=intent,
        law_profile={"law_profile_id": "law.test", "allowed_processes": ["process.pose_enter"], "forbidden_processes": []},
        authority_context={
            "authority_origin": "client",
            "peer_id": "peer.test",
            "subject_id": "agent.alpha",
            "law_profile_id": "law.test",
            "entitlements": [],
            "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
            "privilege_level": "operator",
        },
        policy_context={
            "control_policy_id": "ctrl.policy.player.diegetic",
            "pack_lock_hash": "a" * 64,
        },
        control_action_registry={
            "actions": [
                {
                    "schema_version": "1.0.0",
                    "action_id": "action.interaction.execute_process",
                    "display_name": "Execute Process",
                    "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                    "required_entitlements": [],
                    "required_capabilities": [],
                    "target_kinds": ["none", "surface"],
                    "extensions": {"adapter": "legacy.process_id"},
                }
            ]
        },
        control_policy_registry={
            "policies": [
                {
                    "schema_version": "1.0.0",
                    "control_policy_id": "ctrl.policy.player.diegetic",
                    "description": "Diegetic baseline policy.",
                    "allowed_actions": ["action.interaction.*"],
                    "allowed_abstraction_levels": ["AL0"],
                    "allowed_view_policies": ["view.mode.first_person"],
                    "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                    "downgrade_rules": {},
                    "strictness": "C0",
                    "extensions": {},
                }
            ]
        },
        repo_root=repo_root,
    )
    if str(resolved.get("result", "")) != "complete":
        return {"status": "fail", "message": "control resolution unexpectedly refused"}

    resolution = dict(resolved.get("resolution") or {})
    log_ref = str(resolution.get("decision_log_ref", "")).strip()
    if not log_ref:
        return {"status": "fail", "message": "decision_log_ref missing from control resolution"}
    log_abs = os.path.join(repo_root, log_ref.replace("/", os.sep))
    if not os.path.isfile(log_abs):
        return {"status": "fail", "message": "decision log file does not exist at decision_log_ref"}
    try:
        payload = json.load(open(log_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "decision log payload is not valid JSON"}

    valid = validate_instance(
        repo_root=repo_root,
        schema_name="control_decision_log",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(valid.get("valid", False)):
        return {"status": "fail", "message": "decision log failed control_decision_log schema validation"}
    if str(payload.get("control_intent_id", "")).strip() != str(intent.get("control_intent_id", "")).strip():
        return {"status": "fail", "message": "decision log control_intent_id mismatch"}
    return {"status": "pass", "message": "control decision log emitted and schema-valid"}
