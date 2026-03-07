"""Shared CTRL-4 planning/execution test fixtures."""

from __future__ import annotations

import copy
import json
import os
from typing import List

from tools.xstack.testx.tests.construction_testlib import base_state as construction_base_state
from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def base_state() -> dict:
    state = copy.deepcopy(construction_base_state())
    state.setdefault("plan_artifacts", [])
    return state


def law_profile(allowed_processes: List[str] | None = None) -> dict:
    rows = sorted(
        set(
            str(item).strip()
            for item in list(
                allowed_processes
                or [
                    "process.plan_create",
                    "process.plan_update_incremental",
                    "process.plan_execute",
                    "process.task_create",
                    "process.commitment_create",
                    "process.inspect_generate_snapshot",
                ]
            )
            if str(item).strip()
        )
    )
    entitlement_map = {}
    privilege_map = {}
    for process_id in rows:
        if process_id in ("process.plan_create", "process.plan_update_incremental", "process.inspect_generate_snapshot"):
            entitlement_map[process_id] = "entitlement.inspect"
            privilege_map[process_id] = "operator"
        elif process_id in ("process.plan_execute", "process.commitment_create"):
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
        elif process_id == "process.task_create":
            entitlement_map[process_id] = "entitlement.tool.use"
            privilege_map[process_id] = "operator"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.plan",
        "allowed_processes": rows,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1_000_000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def authority_context(
    entitlements: List[str] | None = None,
    privilege_level: str = "operator",
) -> dict:
    rows = sorted(
        set(
            str(item).strip()
            for item in list(
                entitlements
                or [
                    "entitlement.inspect",
                    "entitlement.control.admin",
                    "entitlement.tool.use",
                    "entitlement.agent.move",
                    "entitlement.tool.operating",
                ]
            )
            if str(item).strip()
        )
    )
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.plan",
        "subject_id": "agent.alpha",
        "experience_id": "profile.test.plan",
        "law_profile_id": "law.test.plan",
        "entitlements": rows,
        "epistemic_scope": {"scope_id": "scope.test.plan", "visibility_level": "nondiegetic"},
        "privilege_level": str(privilege_level),
    }


def policy_context(repo_root: str) -> dict:
    payload = construction_policy_context()
    payload["control_action_registry"] = _read_json(repo_root, "data/registries/control_action_registry.json")
    payload["control_policy_registry"] = _read_json(repo_root, "data/registries/control_policy_registry.json")
    payload["blueprint_registry"] = _read_json(repo_root, "data/registries/blueprint_registry.json")
    payload["part_class_registry"] = _read_json(repo_root, "data/registries/part_class_registry.json")
    payload["connection_type_registry"] = _read_json(repo_root, "data/registries/connection_type_registry.json")
    payload["material_class_registry"] = _read_json(repo_root, "data/registries/material_class_registry.json")
    payload["control_policy_id"] = "ctrl.policy.scheduler"
    payload["plan_compile_budget_units"] = 4096
    payload["control_ir_rs5_budget_units"] = 4096
    payload["max_control_cost_units"] = 4096
    payload["server_profile_id"] = "server.profile.local"
    payload["capability_bindings"] = [
        {
            "binding_id": "cap.bind.plan.site.alpha.blueprint",
            "entity_id": "site.plan.alpha",
            "capability_id": "capability.plan.blueprint",
            "parameters": {},
            "created_tick": 10,
            "extensions": {"source": "plan_testlib"},
        },
        {
            "binding_id": "cap.bind.plan.site.alpha.plannable",
            "entity_id": "site.plan.alpha",
            "capability_id": "capability.can_be_planned",
            "parameters": {},
            "created_tick": 10,
            "extensions": {"source": "plan_testlib"},
        },
        {
            "binding_id": "cap.bind.plan.site.manual.alpha.blueprint",
            "entity_id": "site.plan.manual.alpha",
            "capability_id": "capability.plan.blueprint",
            "parameters": {},
            "created_tick": 10,
            "extensions": {"source": "plan_testlib"},
        },
    ]
    return payload


def structure_plan_create_inputs() -> dict:
    return {
        "plan_intent": {
            "schema_version": "1.0.0",
            "plan_intent_id": "plan.intent.test.structure.alpha",
            "requester_subject_id": "agent.alpha",
            "target_context": {"site_ref": "site.plan.alpha"},
            "plan_type_id": "structure",
            "parameters": {
                "blueprint_id": "blueprint.house.basic",
                "blueprint_parameters": {},
            },
            "created_tick": 10,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        "control_policy_id": "ctrl.policy.planner",
    }


def custom_plan_create_inputs() -> dict:
    return {
        "plan_intent": {
            "schema_version": "1.0.0",
            "plan_intent_id": "plan.intent.test.manual.alpha",
            "requester_subject_id": "agent.alpha",
            "target_context": {"site_ref": "site.plan.manual.alpha"},
            "plan_type_id": "track",
            "parameters": {},
            "created_tick": 10,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        "control_policy_id": "ctrl.policy.planner",
    }
