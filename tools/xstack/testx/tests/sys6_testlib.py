"""Shared SYS-6 reliability TestX fixtures/helpers."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests.sys0_testlib import cloned_state as sys0_cloned_state


def _read_registry_payload(*, repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(str(repo_root), str(rel_path).replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if isinstance(payload.get("record"), dict):
        return dict(payload.get("record") or {})
    return dict(payload)


def base_state(
    *,
    system_id: str = "system.reactor.alpha",
    reliability_profile_id: str = "reliability.reactor_stub",
    hazard_levels: Mapping[str, int] | None = None,
) -> dict:
    state = copy.deepcopy(sys0_cloned_state())
    hazard_map = dict(hazard_levels or {"hazard.thermal.overheat": 780, "hazard.control.loss": 820})
    capsule_id = "capsule.{}".format(str(system_id).replace(".", "_"))

    system_row = dict((state.get("system_rows") or [])[0])
    system_row["system_id"] = str(system_id)
    system_row["current_tier"] = "macro"
    system_row["active_capsule_id"] = capsule_id
    ext = dict(system_row.get("extensions") or {})
    ext["reliability_profile_id"] = str(reliability_profile_id)
    ext["hazard_levels"] = dict((str(key), int(value)) for key, value in sorted(hazard_map.items()))
    ext["unresolved_hazard_count"] = 0
    ext["pending_internal_event_count"] = 0
    ext["open_branch_dependency_count"] = 0
    system_row["extensions"] = ext
    state["system_rows"] = [system_row]

    interface_row = dict((state.get("system_interface_signature_rows") or [])[0])
    interface_row["system_id"] = str(system_id)
    state["system_interface_signature_rows"] = [interface_row]

    state["system_macro_capsule_rows"] = [
        {
            "schema_version": "1.1.0",
            "capsule_id": capsule_id,
            "system_id": str(system_id),
            "interface_signature_id": str(interface_row.get("interface_signature_id", "")),
            "macro_model_set_id": "macro.engine_stub",
            "model_error_bounds_ref": "tol.strict",
            "macro_model_bindings": [],
            "internal_state_vector": {"state_vector_id": "statevec.{}".format(str(system_id).replace(".", "_"))},
            "provenance_anchor_hash": "hash.anchor.sys6.{}".format(canonical_sha256({"system_id": system_id})[:12]),
            "tier_mode": "macro",
            "deterministic_fingerprint": "",
            "extensions": {
                "hazard_level": 0,
                "max_error_estimate": 8,
                "fail_safe_on_forced_expand": True,
                "region_id": "region.default",
            },
        }
    ]
    state["system_macro_runtime_state_rows"] = []
    state["system_forced_expand_event_rows"] = []
    state["system_health_state_rows"] = []
    state["system_failure_event_rows"] = []
    state["system_reliability_warning_rows"] = []
    state["system_reliability_safe_fallback_rows"] = []
    state["system_reliability_output_adjustment_rows"] = []
    state["system_reliability_rng_outcome_rows"] = []
    state["control_decision_log"] = []
    state["model_hazard_rows"] = []
    state["safety_events"] = []
    state["chem_degradation_event_rows"] = []
    state["entropy_states"] = []
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    state.setdefault("explain_artifact_rows", [])
    return state


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys6.test",
        "allowed_processes": [
            "process.system_health_tick",
            "process.system_reliability_tick",
            "process.system_macro_tick",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_health_tick": "session.boot",
            "process.system_reliability_tick": "session.boot",
            "process.system_macro_tick": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_health_tick": "observer",
            "process.system_reliability_tick": "observer",
            "process.system_macro_tick": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys6.test",
        "entitlements": ["session.boot"],
        "privilege_level": "observer",
    }


def policy_context(*, repo_root: str) -> dict:
    return {
        "reliability_profile_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/reliability_profile_registry.json",
        ),
        "explain_contract_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/explain_contract_registry.json",
        ),
        "system_health_max_updates_per_tick": 128,
        "system_health_low_priority_update_stride": 1,
        "system_reliability_max_evaluations_per_tick": 128,
        "system_reliability_tick_bucket_stride": 1,
    }


def execute_process(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
    inputs: Mapping[str, object] | None = None,
    policy_ctx: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys6.{}.{}".format(
                str(process_id).replace(".", "_"),
                canonical_sha256(dict(inputs or {}))[:12],
            ),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_ctx or {}),
    )


def execute_health_tick(*, repo_root: str, state: dict, inputs: Mapping[str, object] | None = None) -> dict:
    return execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_health_tick",
        inputs=inputs,
        policy_ctx=policy_context(repo_root=repo_root),
    )


def execute_reliability_tick(*, repo_root: str, state: dict, inputs: Mapping[str, object] | None = None) -> dict:
    return execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_reliability_tick",
        inputs=inputs,
        policy_ctx=policy_context(repo_root=repo_root),
    )

