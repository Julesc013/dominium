"""STRICT test: structure blueprint planning requires capability.can_be_planned."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_planning_requires_capability"
TEST_TAGS = ["strict", "control", "planning", "capability"]


def _control_policy_row(control_policy_registry: dict, policy_id: str) -> dict:
    payload = dict(control_policy_registry or {})
    rows = payload.get("policies")
    if not isinstance(rows, list):
        rows = dict(payload.get("record") or {}).get("policies")
    if not isinstance(rows, list):
        rows = []
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("control_policy_id", ""))):
        if str(row.get("control_policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {}


def _plan_intent():
    return {
        "schema_version": "1.0.0",
        "plan_intent_id": "plan.intent.capability.required.001",
        "requester_subject_id": "agent.alpha",
        "target_context": {
            "site_ref": "site.plan.capability.alpha",
            "spatial_node_id": "spatial.node.plan.alpha",
        },
        "plan_type_id": "structure",
        "parameters": {
            "blueprint_id": "blueprint.house.basic",
            "blueprint_parameters": {},
            "target_entity_id": "assembly.site.plan.alpha",
        },
        "created_tick": 22,
        "deterministic_fingerprint": "",
        "extensions": {},
    }


def _invoke_plan_create(repo_root: str, policy: dict):
    from src.control.planning.plan_engine import create_plan_artifact
    from tools.xstack.testx.tests.plan_testlib import authority_context, law_profile

    return create_plan_artifact(
        plan_intent=_plan_intent(),
        law_profile=law_profile(),
        authority_context=authority_context(),
        control_policy=_control_policy_row(policy.get("control_policy_registry", {}), "ctrl.policy.planner"),
        control_action_registry=dict(policy.get("control_action_registry") or {}),
        control_policy_registry=dict(policy.get("control_policy_registry") or {}),
        policy_context=policy,
        repo_root=repo_root,
        pack_lock_hash=str(policy.get("pack_lock_hash", "a" * 64)),
        blueprint_registry=dict(policy.get("blueprint_registry") or {}),
        part_class_registry=dict(policy.get("part_class_registry") or {}),
        connection_type_registry=dict(policy.get("connection_type_registry") or {}),
        material_class_registry=dict(policy.get("material_class_registry") or {}),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.plan_testlib import policy_context

    policy = policy_context(repo_root)
    policy["control_policy_id"] = "ctrl.policy.planner"

    missing_capability_policy = copy.deepcopy(policy)
    missing_capability_policy["capability_bindings"] = [
        {
            "entity_id": "site.plan.capability.alpha",
            "capability_id": "capability.plan.blueprint",
            "parameters": {},
            "created_tick": 22,
        },
        {
            "entity_id": "assembly.site.plan.alpha",
            "capability_id": "capability.has_ports",
            "parameters": {},
            "created_tick": 22,
        },
    ]
    missing_result = _invoke_plan_create(repo_root, missing_capability_policy)
    if str(missing_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "plan creation should remain valid when target is not plannable (blueprint compile skipped)"}
    missing_artifact = dict(missing_result.get("plan_artifact") or {})
    missing_ext = dict(missing_artifact.get("extensions") or {})
    if bool(missing_ext.get("target_can_be_planned", True)):
        return {"status": "fail", "message": "plan artifact should mark target_can_be_planned=false when capability is missing"}
    if missing_artifact.get("compiled_blueprint_ref") is not None:
        return {"status": "fail", "message": "blueprint compile should not run when target lacks capability.can_be_planned"}

    with_capability_policy = copy.deepcopy(policy)
    with_capability_policy["capability_bindings"] = [
        {
            "entity_id": "site.plan.capability.alpha",
            "capability_id": "capability.plan.blueprint",
            "parameters": {},
            "created_tick": 22,
        },
        {
            "entity_id": "assembly.site.plan.alpha",
            "capability_id": "capability.can_be_planned",
            "parameters": {},
            "created_tick": 22,
        },
    ]
    enabled_result = _invoke_plan_create(repo_root, with_capability_policy)
    if str(enabled_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "plan creation unexpectedly refused with capability.can_be_planned bound"}
    enabled_artifact = dict(enabled_result.get("plan_artifact") or {})
    enabled_ext = dict(enabled_artifact.get("extensions") or {})
    if not bool(enabled_ext.get("target_can_be_planned", False)):
        return {"status": "fail", "message": "plan artifact should mark target_can_be_planned=true when capability is present"}
    if str(enabled_artifact.get("compiled_blueprint_ref", "")) != "blueprint.house.basic":
        return {"status": "fail", "message": "blueprint compile did not execute for capability-eligible plan target"}

    return {"status": "pass", "message": "planning capability requirement checks passed"}
