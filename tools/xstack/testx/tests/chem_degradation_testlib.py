"""Shared CHEM-3 degradation TestX fixtures."""

from __future__ import annotations

import copy
import json
import os
import sys


def seed_degradation_state() -> dict:
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state.setdefault("chem_degradation_state_rows", [])
    state.setdefault("degradation_state_rows", [])
    state.setdefault("chem_degradation_event_rows", [])
    state.setdefault("degradation_event_rows", [])
    state.setdefault("chem_maintenance_action_rows", [])
    state.setdefault("maintenance_action_rows", [])
    state.setdefault("effect_rows", [])
    state.setdefault("model_hazard_rows", [])
    state.setdefault("model_cache_rows", [])
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    return state


def _law_profile_for(process_ids: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(process_ids or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    for process_id in list(process_ids or []):
        token = str(process_id or "").strip()
        if not token:
            continue
        if token == "process.degradation_tick":
            entitlements[token] = "session.boot"
            privileges[token] = "observer"
        elif token in {
            "process.clean_heat_exchanger",
            "process.flush_pipe",
            "process.apply_coating",
            "process.replace_section",
        }:
            entitlements[token] = "entitlement.control.admin"
            privileges[token] = "operator"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def _authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect", "entitlement.tool.operating"],
        privilege_level="operator",
    )


def _policy_context(max_compute_units_per_tick: int = 4096) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    policy = copy.deepcopy(
        construction_policy_context(max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick))))
    )
    policy["physics_profile_id"] = "phys.realistic.default"
    policy["chem_max_degradation_targets_per_tick"] = 256
    policy["chem_max_degradation_model_cost_units"] = 1024
    return policy


def execute_process(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
    inputs: dict | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    process_token = str(process_id or "").strip()
    law = _law_profile_for([process_token])
    authority = _authority_context()
    policy = _policy_context()
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.chem3.{}".format(process_token.replace(".", "_")),
            "process_id": process_token,
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def load_registry_payload(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = json.load(open(abs_path, "r", encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    return dict(payload.get("record") or payload)
