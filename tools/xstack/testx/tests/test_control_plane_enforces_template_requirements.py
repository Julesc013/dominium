"""STRICT test: control plane enforces action_template requirements deterministically."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "test_control_plane_enforces_template_requirements"
TEST_TAGS = ["strict", "control", "meta"]


def _control_action_registry() -> dict:
    return {
        "record": {
            "actions": [
                {
                    "schema_version": "1.0.0",
                    "action_id": "action.test.execute",
                    "display_name": "Test Execute",
                    "produces": {
                        "process_id": "process.test.execute",
                        "task_type_id": "",
                        "plan_intent_type": "",
                    },
                    "required_entitlements": [],
                    "required_capabilities": [],
                    "target_kinds": ["surface"],
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
                    "description": "Test control policy",
                    "allowed_actions": ["action.test.execute"],
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


def _action_template_registry() -> dict:
    return {
        "record": {
            "templates": [
                {
                    "schema_version": "1.0.0",
                    "action_template_id": "action.test.execute",
                    "action_family_id": "action_family.transform",
                    "required_tool_tags": ["tool_tag.operating"],
                    "required_surface_types": ["surface.panel"],
                    "required_capabilities": ["capability.surface.execute"],
                    "produced_artifact_types": ["artifact.transform"],
                    "produced_hazard_types": [],
                    "affected_substrates": ["Mechanics"],
                    "deterministic_fingerprint": "0" * 64,
                    "extensions": {"template_kind": "control_action"},
                }
            ]
        }
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.action_template",
        "allowed_processes": ["process.test.execute"],
        "forbidden_processes": [],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "client",
        "peer_id": "peer.test.template",
        "subject_id": "subject.operator",
        "law_profile_id": "law.test.action_template",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }


def _policy_context(bindings: list[dict]) -> dict:
    return {
        "control_policy_id": "ctrl.policy.player.diegetic",
        "submission_tick": 50,
        "deterministic_sequence_number": 1,
        "pack_lock_hash": "a" * 64,
        "capability_bindings": [dict(row) for row in list(bindings or []) if isinstance(row, dict)],
    }


def _read_decision_log(repo_root: str, decision_log_ref: str) -> dict:
    abs_path = os.path.join(repo_root, str(decision_log_ref or "").replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution

    base_intent = build_control_intent(
        requester_subject_id="subject.operator",
        requested_action_id="action.test.execute",
        target_kind="surface",
        target_id="surface.alpha",
        parameters={"process_id": "process.test.execute"},
        abstraction_level_requested="AL0",
        fidelity_requested="meso",
        view_requested="view.mode.first_person",
        created_tick=50,
    )

    missing_surface = copy.deepcopy(base_intent)
    missing_surface["extensions"] = {"surface_type_id": "surface.handle", "active_tool_tags": ["tool_tag.operating"]}
    missing_surface["deterministic_fingerprint"] = "0" * 64
    refused_surface = build_control_resolution(
        control_intent=missing_surface,
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context([]),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        action_template_registry=_action_template_registry(),
        repo_root=repo_root,
    )
    if str(refused_surface.get("result", "")) != "refused":
        return {"status": "fail", "message": "control resolution should refuse invalid surface_type_id"}

    missing_capability = copy.deepcopy(base_intent)
    missing_capability["extensions"] = {"surface_type_id": "surface.panel", "active_tool_tags": ["tool_tag.operating"]}
    missing_capability["deterministic_fingerprint"] = "0" * 64
    refused_capability = build_control_resolution(
        control_intent=missing_capability,
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context([]),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        action_template_registry=_action_template_registry(),
        repo_root=repo_root,
    )
    if str(refused_capability.get("result", "")) != "refused":
        return {"status": "fail", "message": "control resolution should refuse missing template capability"}

    valid_intent = copy.deepcopy(base_intent)
    valid_intent["extensions"] = {"surface_type_id": "surface.panel", "active_tool_tags": ["tool_tag.operating"]}
    valid_intent["deterministic_fingerprint"] = "0" * 64
    accepted = build_control_resolution(
        control_intent=valid_intent,
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context(
            [
                {
                    "entity_id": "surface.alpha",
                    "capability_id": "capability.surface.execute",
                    "parameters": {"control_binding_id": "binding.surface.alpha"},
                    "created_tick": 50,
                }
            ]
        ),
        control_action_registry=_control_action_registry(),
        control_policy_registry=_control_policy_registry(),
        action_template_registry=_action_template_registry(),
        repo_root=repo_root,
    )
    if str(accepted.get("result", "")) != "complete":
        return {"status": "fail", "message": "control resolution unexpectedly refused valid template requirements"}

    resolution = dict(accepted.get("resolution") or {})
    decision_log_ref = str(resolution.get("decision_log_ref", "")).strip()
    if not decision_log_ref:
        return {"status": "fail", "message": "decision_log_ref missing for accepted action"}
    decision_log = _read_decision_log(repo_root, decision_log_ref)
    action_family_id = str((dict(decision_log.get("extensions") or {})).get("action_family_id", "")).strip()
    if action_family_id != "action_family.transform":
        return {"status": "fail", "message": "decision log missing action_family_id from action_template mapping"}
    return {"status": "pass", "message": "control plane enforces action_template requirements"}

