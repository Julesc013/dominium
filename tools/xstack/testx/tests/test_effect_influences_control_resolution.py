"""STRICT test: CTRL-8 effects influence control resolution and decision logging."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.control.effects.influences_control_resolution"
TEST_TAGS = ["strict", "control", "effects"]


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
                "target_kinds": ["interior_portal", "machine", "structure", "none"],
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
                "description": "Test diegetic policy.",
                "allowed_actions": ["action.interaction.execute_process"],
                "allowed_abstraction_levels": ["AL0"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            }
        ]
    }


def _effect_type_registry() -> dict:
    return {
        "effect_types": [
            {
                "schema_version": "1.0.0",
                "effect_type_id": "effect.access_restricted",
                "description": "Test access restriction.",
                "applies_to": ["interior_portal"],
                "modifies": ["access_restricted"],
                "default_visibility_policy_id": "effect.visibility.diegetic_alarm",
                "extensions": {},
            }
        ]
    }


def _stacking_policy_registry() -> dict:
    return {
        "stacking_policies": [
            {
                "schema_version": "1.0.0",
                "stacking_policy_id": "stack.replace_latest",
                "mode": "replace",
                "tie_break_rule": "order.effect_type_applied_tick_effect_id",
                "extensions": {},
            }
        ]
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution, build_effect

    intent = build_control_intent(
        requester_subject_id="subject.operator",
        requested_action_id="action.interaction.execute_process",
        target_kind="interior_portal",
        target_id="portal.ab",
        parameters={"process_id": "process.portal_open"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=20,
    )
    restricted_effect = build_effect(
        effect_type_id="effect.access_restricted",
        target_id="portal.ab",
        applied_tick=20,
        duration_ticks=5,
        magnitude={"access_restricted": 1000},
        stacking_policy_id="stack.replace_latest",
    )
    result = build_control_resolution(
        control_intent=dict(intent),
        law_profile={
            "law_profile_id": "law.test.effects.control",
            "allowed_processes": ["process.portal_open"],
            "forbidden_processes": [],
        },
        authority_context={
            "authority_origin": "client",
            "peer_id": "peer.test.effects",
            "subject_id": "subject.operator",
            "law_profile_id": "law.test.effects.control",
            "entitlements": [],
            "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
            "privilege_level": "operator",
        },
        policy_context={
            "control_policy_id": "ctrl.policy.player.diegetic",
            "source_shard_id": "shard.0",
            "target_shard_id": "shard.0",
            "submission_tick": 20,
            "deterministic_sequence_number": 1,
            "peer_id": "peer.test.effects",
            "pack_lock_hash": "a" * 64,
            "effect_rows": [dict(restricted_effect)],
            "effect_type_registry": _effect_type_registry(),
            "stacking_policy_registry": _stacking_policy_registry(),
        },
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        repo_root=repo_root,
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected control refusal when access_restricted effect is active"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.effect.forbidden":
        return {
            "status": "fail",
            "message": "unexpected refusal code '{}'".format(str(refusal_payload.get("reason_code", ""))),
        }

    resolution = dict(result.get("resolution") or {})
    log_ref = str(resolution.get("decision_log_ref", "")).strip()
    if not log_ref:
        return {"status": "fail", "message": "missing decision_log_ref for effect-based refusal"}
    log_abs = os.path.join(repo_root, log_ref.replace("/", os.sep))
    try:
        log_payload = json.load(open(log_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "unable to parse decision log payload at '{}'".format(log_ref)}
    extensions = dict(log_payload.get("extensions") or {})
    effect_influence = dict(extensions.get("effect_influence") or {})
    modifiers = dict(effect_influence.get("modifiers") or {})
    access_modifier = dict(modifiers.get("access_restricted") or {})
    if not bool(access_modifier.get("present", False)):
        return {"status": "fail", "message": "decision log missing access_restricted effect influence"}
    return {"status": "pass", "message": "control resolution refused with effect influence recorded"}

