"""Shared SYS-4 template library TestX fixtures/helpers."""

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
    return dict(payload)


def _rows(payload: Mapping[str, object], key: str) -> list[dict]:
    rows = dict(payload or {}).get(key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record_rows = dict(dict(payload or {}).get("record") or {}).get(key)
    if isinstance(record_rows, list):
        return [dict(item) for item in record_rows if isinstance(item, Mapping)]
    return []


def _sorted_tokens(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def combined_template_registry(*, repo_root: str) -> dict:
    core = _read_registry_payload(repo_root=repo_root, rel_path="data/registries/system_template_registry.json")
    out_rows = _rows(core, "system_templates")
    optional_paths = _sorted_tokens(list(dict(dict(core.get("record") or {}).get("extensions") or {}).get("optional_pack_paths") or []))
    for rel in optional_paths:
        pack_rel = "{}/data/system_template_registry.json".format(str(rel).strip("/"))
        out_rows.extend(_rows(_read_registry_payload(repo_root=repo_root, rel_path=pack_rel), "system_templates"))
    return {"system_templates": out_rows}


def compile_template(*, repo_root: str, template_id: str, instantiation_mode: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.system import compile_system_template

    return compile_system_template(
        template_id=str(template_id),
        instantiation_mode=str(instantiation_mode),
        system_template_registry_payload=combined_template_registry(repo_root=repo_root),
        interface_signature_template_registry_payload=_read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/interface_signature_template_registry.json",
        ),
        boundary_invariant_template_registry_payload=_read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/boundary_invariant_template_registry.json",
        ),
        macro_model_set_registry_payload=_read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/macro_model_set_registry.json",
        ),
        tier_contract_registry_payload=_read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/tier_contract_registry.json",
        ),
        domain_registry_payload=_read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/domain_registry.json",
        ),
    )


def base_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "process_log": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
    }


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys4.test",
        "allowed_processes": ["process.template_instantiate"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.template_instantiate": "entitlement.control.admin",
        },
        "process_privilege_requirements": {
            "process.template_instantiate": "operator",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys4.test",
        "entitlements": ["entitlement.control.admin"],
        "privilege_level": "operator",
    }


def execute_template_instantiate(
    *,
    repo_root: str,
    state: dict,
    template_id: str,
    instantiation_mode: str,
    target_spatial_id: str = "cell.sys4.test.0001",
    allow_macro: bool = False,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    policy_context = {
        "template_instantiation_policy": {
            "allow_macro": bool(allow_macro),
            "allow_hybrid": True,
        }
    }
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys4.template.{}".format(
                canonical_sha256(
                    {
                        "template_id": template_id,
                        "instantiation_mode": instantiation_mode,
                        "target_spatial_id": target_spatial_id,
                    }
                )[:16]
            ),
            "process_id": "process.template_instantiate",
            "inputs": {
                "template_id": str(template_id),
                "instantiation_mode": str(instantiation_mode),
                "target_spatial_id": str(target_spatial_id),
                "allow_macro": bool(allow_macro),
            },
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy_context,
    )


def cloned_state() -> dict:
    return copy.deepcopy(base_state())

