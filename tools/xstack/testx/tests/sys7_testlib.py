"""Shared SYS-7 forensics TestX fixtures/helpers."""

from __future__ import annotations

import copy
import json
import os
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


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


def base_state() -> dict:
    if "." not in sys.path:
        sys.path.insert(0, ".")
    from tools.xstack.testx.tests.sys6_testlib import base_state as sys6_base_state

    state = copy.deepcopy(
        sys6_base_state(
            hazard_levels={
                "hazard.thermal.overheat": 980,
                "hazard.control.loss": 980,
            }
        )
    )
    state.setdefault("system_explain_request_rows", [])
    state.setdefault("system_explain_artifact_rows", [])
    state.setdefault("system_explain_cache_rows", [])
    state.setdefault("info_artifact_rows", [])
    state.setdefault("knowledge_artifacts", [])
    return state


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys7.test",
        "allowed_processes": [
            "process.system_health_tick",
            "process.system_reliability_tick",
            "process.system_generate_explain",
            "process.system_evaluate_certification",
            "process.system_collapse",
            "process.system_expand",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_health_tick": "session.boot",
            "process.system_reliability_tick": "session.boot",
            "process.system_generate_explain": "entitlement.inspect",
            "process.system_evaluate_certification": "entitlement.inspect",
            "process.system_collapse": "session.boot",
            "process.system_expand": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_health_tick": "observer",
            "process.system_reliability_tick": "observer",
            "process.system_generate_explain": "observer",
            "process.system_evaluate_certification": "observer",
            "process.system_collapse": "observer",
            "process.system_expand": "observer",
        },
    }


def authority_context(*, requester_subject_id: str = "inspector.sys7") -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys7.test",
        "entitlements": ["session.boot", "entitlement.inspect"],
        "privilege_level": "observer",
        "subject_id": str(requester_subject_id),
        "requester_subject_id": str(requester_subject_id),
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
    requester_subject_id: str = "inspector.sys7",
    policy_ctx: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys7.{}.{}".format(
                str(process_id).replace(".", "_"),
                canonical_sha256(dict(inputs or {}))[:12],
            ),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(requester_subject_id=requester_subject_id),
        navigation_indices={},
        policy_context=dict(policy_ctx or policy_context(repo_root=repo_root)),
    )


def seed_reliability_events(*, repo_root: str, state: dict) -> tuple[dict, dict]:
    health_result = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_health_tick",
        inputs={},
    )
    reliability_result = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_reliability_tick",
        inputs={"denied_expand_system_ids": []},
    )
    return health_result, reliability_result


def execute_system_explain(
    *,
    repo_root: str,
    state: dict,
    system_id: str,
    explain_level: str = "L1",
    event_id: str | None = None,
    requester_policy_id: str = "",
    requester_subject_id: str = "inspector.sys7",
    max_cause_entries: int = 16,
) -> dict:
    before_request_ids = set(
        str(dict(row).get("request_id", "")).strip()
        for row in list(state.get("system_explain_request_rows") or [])
        if isinstance(row, Mapping) and str(dict(row).get("request_id", "")).strip()
    )
    result = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.system_generate_explain",
        requester_subject_id=requester_subject_id,
        inputs={
            "system_explain_request": {
                "request_id": "",
                "system_id": str(system_id),
                "event_id": event_id,
                "explain_level": str(explain_level).strip().upper() or "L1",
                "requester_subject_id": str(requester_subject_id),
                "extensions": {},
            },
            "requester_policy_id": str(requester_policy_id),
            "max_cause_entries": int(max(1, int(max_cause_entries))),
        },
    )
    after_requests = [
        dict(row)
        for row in list(state.get("system_explain_request_rows") or [])
        if isinstance(row, Mapping)
    ]
    selected_request_id = ""
    new_request_ids = sorted(
        token
        for token in (
            str(dict(row).get("request_id", "")).strip()
            for row in after_requests
        )
        if token and token not in before_request_ids
    )
    if new_request_ids:
        selected_request_id = str(new_request_ids[-1]).strip()
    if not selected_request_id:
        for row in reversed(after_requests):
            request_id = str(row.get("request_id", "")).strip()
            if not request_id:
                continue
            if str(row.get("system_id", "")).strip() != str(system_id).strip():
                continue
            if str(row.get("explain_level", "")).strip().upper() != str(explain_level).strip().upper():
                continue
            selected_request_id = request_id
            break

    selected_artifact = {}
    for row in list(state.get("system_explain_artifact_rows") or []):
        if not isinstance(row, Mapping):
            continue
        ext = dict(dict(row).get("extensions") or {})
        if str(ext.get("request_id", "")).strip() != selected_request_id:
            continue
        selected_artifact = dict(row)
    result = dict(result or {})
    result["sys7_request_id"] = selected_request_id
    result["sys7_explain_artifact"] = dict(selected_artifact or {})
    result["sys7_explain_id"] = str(dict(selected_artifact or {}).get("explain_id", "")).strip()
    return result
