#!/usr/bin/env python3
"""SYS-4 developer template browser/instantiation CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from system import compile_system_template  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _registry_rows(payload: Mapping[str, object], entry_key: str) -> list[dict]:
    body = _as_map(payload)
    rows = body.get(entry_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record_rows = _as_map(body.get("record")).get(entry_key)
    if isinstance(record_rows, list):
        return [dict(item) for item in record_rows if isinstance(item, Mapping)]
    return []


def _registry_payload(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return _read_json(abs_path)


def _combined_template_registry(repo_root: str) -> dict:
    core = _registry_payload(repo_root, "data/registries/system_template_registry.json")
    out_rows = _registry_rows(core, "system_templates")
    optional_paths = _sorted_tokens(list(_as_map(_as_map(core.get("record")).get("extensions")).get("optional_pack_paths") or []))
    for rel in optional_paths:
        pack_rel = "{}/data/system_template_registry.json".format(str(rel).strip("/"))
        out_rows.extend(_registry_rows(_registry_payload(repo_root, pack_rel), "system_templates"))
    return {"system_templates": out_rows}


def _summary_row(row: Mapping[str, object]) -> dict:
    payload = _as_map(row)
    ext = _as_map(payload.get("extensions"))
    iface_summary = _as_map(ext.get("interface_summary"))
    return {
        "template_id": str(payload.get("template_id", "")).strip(),
        "version": str(payload.get("version", "")).strip(),
        "description": str(payload.get("description", "")).strip(),
        "interface_signature_template_id": str(payload.get("interface_signature_template_id", "")).strip(),
        "boundary_invariant_template_ids": _sorted_tokens(list(payload.get("boundary_invariant_template_ids") or [])),
        "macro_model_set_id": str(payload.get("macro_model_set_id", "")).strip(),
        "tier_contract_id": str(payload.get("tier_contract_id", "")).strip(),
        "safety_pattern_ids": _sorted_tokens(
            [str(item.get("pattern_id", "")).strip() for item in list(payload.get("safety_pattern_instance_templates") or []) if isinstance(item, Mapping)]
        ),
        "spec_bindings": [
            {
                "spec_type_id": str(item.get("spec_type_id", "")).strip(),
                "target": str(item.get("target", "")).strip() or "system",
            }
            for item in list(payload.get("spec_bindings") or [])
            if isinstance(item, Mapping)
        ],
        "expected_ports": _sorted_tokens(list(iface_summary.get("ports") or [])),
    }


def _compile_preview(*, repo_root: str, template_id: str, instantiation_mode: str) -> dict:
    template_registry = _combined_template_registry(repo_root)
    compiled = compile_system_template(
        template_id=template_id,
        instantiation_mode=instantiation_mode,
        system_template_registry_payload=template_registry,
        interface_signature_template_registry_payload=_registry_payload(repo_root, "data/registries/interface_signature_template_registry.json"),
        boundary_invariant_template_registry_payload=_registry_payload(repo_root, "data/registries/boundary_invariant_template_registry.json"),
        macro_model_set_registry_payload=_registry_payload(repo_root, "data/registries/macro_model_set_registry.json"),
        tier_contract_registry_payload=_registry_payload(repo_root, "data/registries/tier_contract_registry.json"),
        domain_registry_payload=_registry_payload(repo_root, "data/registries/domain_registry.json"),
    )
    macro = _as_map(compiled.get("compiled_macro_capsule"))
    return {
        "template_id": template_id,
        "instantiation_mode": instantiation_mode,
        "resolved_template_order": [str(token).strip() for token in list(compiled.get("resolved_template_order") or []) if str(token).strip()],
        "interface_signature_template_id": str(macro.get("interface_signature_template_id", "")).strip(),
        "boundary_invariant_template_ids": _sorted_tokens(list(macro.get("boundary_invariant_template_ids") or [])),
        "safety_pattern_ids": _sorted_tokens(
            [str(item.get("pattern_id", "")).strip() for item in list(macro.get("safety_pattern_instance_templates") or []) if isinstance(item, Mapping)]
        ),
        "expected_outputs": _sorted_tokens(
            [
                str(port).strip()
                for item in list(macro.get("model_bindings") or [])
                if isinstance(item, Mapping)
                for port in list(item.get("output_port_ids") or [])
            ]
        ),
        "compiled_template_fingerprint": str(compiled.get("compiled_template_fingerprint", "")).strip(),
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.sys4.template_browser",
        "allowed_processes": ["process.template_instantiate"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.template_instantiate": "entitlement.control.admin"},
        "process_privilege_requirements": {"process.template_instantiate": "operator"},
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys4.template_browser",
        "entitlements": ["entitlement.control.admin"],
        "privilege_level": "operator",
    }


def _execute_template_instantiation(
    *,
    template_id: str,
    instantiation_mode: str,
    target_spatial_id: str,
    allow_macro: bool,
) -> dict:
    state = {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "process_log": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
    }
    policy_context = {
        "template_instantiation_policy": {
            "allow_macro": bool(allow_macro),
            "allow_hybrid": True,
        }
    }
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys4.template_browser.{}".format(
                canonical_sha256({"template_id": template_id, "mode": instantiation_mode, "target": target_spatial_id})[:16]
            ),
            "process_id": "process.template_instantiate",
            "inputs": {
                "template_id": template_id,
                "instantiation_mode": instantiation_mode,
                "target_spatial_id": target_spatial_id,
                "allow_macro": bool(allow_macro),
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=policy_context,
    )
    return {
        "result": str(result.get("result", "")).strip(),
        "reason_code": str(result.get("reason_code", "")).strip(),
        "metadata": dict(result.get("metadata") or {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Browse SYS-4 templates and optionally execute instantiation.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--template-id", default="")
    parser.add_argument("--instantiation-mode", default="micro", choices=("micro", "macro", "hybrid"))
    parser.add_argument("--target-spatial-id", default="cell.template.browser.0001")
    parser.add_argument("--execute", action="store_true", help="Execute process.template_instantiate using tool authority.")
    parser.add_argument("--allow-execute", action="store_true", help="Policy gate for execute mode.")
    parser.add_argument("--allow-macro", action="store_true", help="Enable macro mode policy gate in execute mode.")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    template_registry = _combined_template_registry(repo_root)
    summaries = sorted(
        (_summary_row(row) for row in _registry_rows(template_registry, "system_templates")),
        key=lambda row: str(row.get("template_id", "")),
    )
    report = {
        "result": "complete",
        "template_count": len(summaries),
        "templates": summaries,
        "preview": {},
        "execution": {},
    }
    template_id = str(args.template_id or "").strip()
    if template_id:
        try:
            report["preview"] = _compile_preview(
                repo_root=repo_root,
                template_id=template_id,
                instantiation_mode=str(args.instantiation_mode),
            )
        except Exception as exc:
            report["result"] = "refusal"
            report["reason_code"] = "refusal.template.preview_failed"
            report["message"] = str(exc)
    if bool(args.execute):
        if not bool(args.allow_execute):
            report["result"] = "refusal"
            report["reason_code"] = "refusal.template.browser.execute_not_allowed"
            report["message"] = "Pass --allow-execute to run process.template_instantiate from browser CLI."
        elif not template_id:
            report["result"] = "refusal"
            report["reason_code"] = "refusal.template.browser.template_required"
            report["message"] = "--template-id is required when --execute is set."
        else:
            report["execution"] = _execute_template_instantiation(
                template_id=template_id,
                instantiation_mode=str(args.instantiation_mode),
                target_spatial_id=str(args.target_spatial_id),
                allow_macro=bool(args.allow_macro),
            )
            if str(report["execution"].get("result", "")).strip() != "complete":
                report["result"] = "refusal"
                report["reason_code"] = str(report["execution"].get("reason_code", "")).strip() or "refusal.template.execution_failed"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

