"""Deterministic pack compatibility manifest validation helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.compatx.core.semantic_contract_validator import load_semantic_contract_registry, semantic_contract_ids
from src.meta_extensions_engine import normalize_extensions_tree


PACK_COMPAT_MANIFEST_NAME = "pack.compat.json"
PACK_COMPAT_SCHEMA_NAME = "pack_compat_manifest"
PACK_DEGRADE_MODE_REGISTRY_REL = os.path.join("data", "registries", "pack_degrade_mode_registry.json")
CAPABILITY_REGISTRY_REL = os.path.join("data", "registries", "capability_registry.json")

REFUSAL_PACK_CONTRACT_MISMATCH = "refusal.pack.contract_mismatch"
REFUSAL_PACK_MISSING_CAPABILITY = "refusal.pack.missing_capability"
REFUSAL_PACK_MISSING_REGISTRY = "refusal.pack.missing_registry"
REFUSAL_PACK_COMPAT_MANIFEST_MISSING = "refusal.pack.compat_manifest_missing"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: object) -> List[str]:
    return sorted(set(str(item).strip() for item in _as_list(values) if str(item).strip()))


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = normalize_extensions_tree(json.load(open(path, "r", encoding="utf-8")))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _error(code: str, path: str, message: str) -> dict:
    return {
        "code": str(code),
        "path": str(path),
        "message": str(message),
    }


def _load_pack_degrade_modes(repo_root: str) -> Tuple[set[str], List[dict]]:
    payload, err = _read_json(os.path.join(repo_root, PACK_DEGRADE_MODE_REGISTRY_REL))
    if err:
        return set(), [_error("pack_compat_registry_invalid", "$.pack_degrade_mode_registry", "unable to load pack degrade mode registry")]
    rows = list(_as_map(payload.get("record")).get("pack_degrade_modes") or [])
    modes = set()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("degrade_mode_id", "")).strip()
        if token:
            modes.add(token)
    if not modes:
        return set(), [_error("pack_compat_registry_invalid", "$.pack_degrade_mode_registry", "pack degrade mode registry is empty")]
    return set(sorted(modes)), []


def _load_capability_ids(repo_root: str) -> Tuple[set[str], List[dict]]:
    payload, err = _read_json(os.path.join(repo_root, CAPABILITY_REGISTRY_REL))
    if err:
        return set(), [_error(REFUSAL_PACK_MISSING_CAPABILITY, "$.capability_registry", "unable to load capability registry")]
    rows = list(_as_map(payload.get("record")).get("capabilities") or [])
    ids = set()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("capability_id", "")).strip()
        if token:
            ids.add(token)
    if not ids:
        return set(), [_error(REFUSAL_PACK_MISSING_CAPABILITY, "$.capability_registry", "capability registry is empty")]
    return set(sorted(ids)), []


def _normalize_manifest(payload: Mapping[str, object]) -> dict:
    body = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "pack_id": str(payload.get("pack_id", "")).strip(),
        "pack_version": str(payload.get("pack_version", "")).strip(),
        "trust_level_id": str(payload.get("trust_level_id", "")).strip(),
        "capability_ids": _sorted_tokens(payload.get("capability_ids")),
        "required_contract_ranges": {
            str(key): dict(value)
            for key, value in sorted(_as_map(payload.get("required_contract_ranges")).items(), key=lambda item: str(item[0]))
            if isinstance(value, Mapping)
        },
        "required_protocol_ranges": {
            str(key): dict(value)
            for key, value in sorted(_as_map(payload.get("required_protocol_ranges")).items(), key=lambda item: str(item[0]))
            if isinstance(value, Mapping)
        },
        "supported_engine_version_range": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("supported_engine_version_range")).items(), key=lambda item: str(item[0]))
        },
        "required_registry_ids": _sorted_tokens(payload.get("required_registry_ids")),
        "provides": _sorted_tokens(payload.get("provides")),
        "degrade_mode_id": str(payload.get("degrade_mode_id", "")).strip(),
        "migration_refs": _sorted_tokens(payload.get("migration_refs")),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    return body


def validate_pack_compat_manifest(
    *,
    repo_root: str,
    pack_row: Mapping[str, object],
    manifest_payload: Mapping[str, object],
    schema_repo_root: str = "",
) -> Dict[str, object]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    payload = _normalize_manifest(manifest_payload)
    errors: List[dict] = []
    warnings: List[dict] = []

    schema_check = validate_instance(
        repo_root=schema_root,
        schema_name=PACK_COMPAT_SCHEMA_NAME,
        payload=payload,
        strict_top_level=True,
    )
    if not bool(schema_check.get("valid", False)):
        for row in schema_check.get("errors") or []:
            if not isinstance(row, Mapping):
                continue
            errors.append(
                _error(
                    "pack_compat_manifest_invalid",
                    str(row.get("path", "$")),
                    str(row.get("message", "")),
                )
            )
        return {"result": "refused", "errors": sorted(errors, key=lambda row: (row["code"], row["path"], row["message"])), "warnings": []}

    if payload["deterministic_fingerprint"] != _fingerprint(payload):
        errors.append(
            _error(
                "pack_compat_manifest_fingerprint_mismatch",
                "$.deterministic_fingerprint",
                "pack compatibility manifest deterministic_fingerprint mismatch",
            )
        )

    pack_id = str(pack_row.get("pack_id", "")).strip()
    version = str(pack_row.get("version", "")).strip()
    if payload["pack_id"] != pack_id:
        errors.append(_error("pack_compat_pack_id_mismatch", "$.pack_id", "pack.compat.json pack_id does not match adjacent pack.json"))
    if payload["pack_version"] != version:
        errors.append(_error("pack_compat_pack_version_mismatch", "$.pack_version", "pack.compat.json pack_version does not match adjacent pack.json"))
    if payload["trust_level_id"] and str(pack_row.get("trust_level_id", "")).strip() and payload["trust_level_id"] != str(pack_row.get("trust_level_id", "")).strip():
        errors.append(_error("pack_compat_trust_level_mismatch", "$.trust_level_id", "pack.compat.json trust_level_id does not match pack.trust.json"))
    if payload["capability_ids"] and _sorted_tokens(pack_row.get("capability_ids")) and payload["capability_ids"] != _sorted_tokens(pack_row.get("capability_ids")):
        errors.append(_error("pack_compat_capability_mismatch", "$.capability_ids", "pack.compat.json capability_ids do not match pack.capabilities.json"))
    capability_ids, capability_errors = _load_capability_ids(repo_root)
    errors.extend(capability_errors)
    for capability_id in payload["capability_ids"]:
        if capability_id not in capability_ids:
            errors.append(_error(REFUSAL_PACK_MISSING_CAPABILITY, "$.capability_ids", "capability '{}' is not present in the capability registry".format(capability_id)))

    known_contract_ids = set()
    contract_registry, contract_registry_error = load_semantic_contract_registry(repo_root)
    if contract_registry_error:
        errors.append(_error(REFUSAL_PACK_CONTRACT_MISMATCH, "$.required_contract_ranges", "semantic contract registry is unavailable"))
    else:
        known_contract_ids = set(semantic_contract_ids(contract_registry))
    for contract_id, contract_range in sorted(payload["required_contract_ranges"].items(), key=lambda item: str(item[0])):
        if contract_id not in known_contract_ids:
            errors.append(_error(REFUSAL_PACK_CONTRACT_MISMATCH, "$.required_contract_ranges.{}".format(contract_id), "required contract id is not present in the current semantic contract registry"))
            continue
        row = _as_map(contract_range)
        min_version = str(row.get("min_version", "")).strip()
        max_version = str(row.get("max_version", "")).strip()
        exact_version = str(row.get("exact_version", "")).strip()
        if exact_version and exact_version != contract_id:
            errors.append(_error(REFUSAL_PACK_CONTRACT_MISMATCH, "$.required_contract_ranges.{}".format(contract_id), "exact_version must match the pinned contract id for MVP v1 contracts"))
        if min_version and min_version != contract_id:
            errors.append(_error(REFUSAL_PACK_CONTRACT_MISMATCH, "$.required_contract_ranges.{}.min_version".format(contract_id), "min_version is not supported by the current contract registry"))
        if max_version and max_version != contract_id:
            errors.append(_error(REFUSAL_PACK_CONTRACT_MISMATCH, "$.required_contract_ranges.{}.max_version".format(contract_id), "max_version is not supported by the current contract registry"))

    degrade_modes, degrade_errors = _load_pack_degrade_modes(repo_root)
    errors.extend(degrade_errors)
    if payload["degrade_mode_id"] and payload["degrade_mode_id"] not in degrade_modes:
        errors.append(_error("pack_compat_degrade_mode_unknown", "$.degrade_mode_id", "degrade_mode_id is not declared in the pack degrade mode registry"))

    registry_dir = os.path.join(repo_root, "data", "registries")
    registry_ids = set()
    if os.path.isdir(registry_dir):
        for name in sorted(os.listdir(registry_dir)):
            if not name.endswith(".json"):
                continue
            registry_payload, err = _read_json(os.path.join(registry_dir, name))
            if err:
                continue
            record = _as_map(registry_payload.get("record"))
            registry_id = str(record.get("registry_id", "")).strip()
            if registry_id:
                registry_ids.add(registry_id)
    for registry_id in payload["required_registry_ids"]:
        if registry_id not in registry_ids:
            errors.append(_error(REFUSAL_PACK_MISSING_REGISTRY, "$.required_registry_ids", "required registry '{}' is not present".format(registry_id)))

    if errors:
        return {"result": "refused", "errors": sorted(errors, key=lambda row: (row["code"], row["path"], row["message"])), "warnings": []}
    return {
        "result": "complete",
        "errors": [],
        "warnings": sorted(warnings, key=lambda row: (row["code"], row["path"], row["message"])),
        "compat_manifest": payload,
        "compat_manifest_hash": canonical_sha256(payload),
        "degrade_mode_id": payload["degrade_mode_id"],
    }


def attach_pack_compat_manifest(
    *,
    repo_root: str,
    pack_row: Mapping[str, object],
    schema_repo_root: str = "",
    mod_policy_id: str = "",
) -> Tuple[dict, List[dict], List[dict]]:
    attached = dict(pack_row)
    pack_dir = str(attached.get("pack_dir", "")).strip()
    compat_path = os.path.join(pack_dir, PACK_COMPAT_MANIFEST_NAME)
    attached["compat_manifest_path"] = ""
    attached["compat_manifest_hash"] = ""
    attached["compat_manifest"] = {}
    attached["pack_degrade_mode_id"] = ""
    if not os.path.isfile(compat_path):
        code = REFUSAL_PACK_COMPAT_MANIFEST_MISSING if str(mod_policy_id).strip() == "mod_policy.strict" else "warn.pack.compat_manifest_missing"
        row = _error(code, "$.pack.compat", "missing pack.compat.json for '{}'".format(str(attached.get("pack_id", "")).strip()))
        if str(mod_policy_id).strip() == "mod_policy.strict":
            return attached, [row], []
        return attached, [], [row]

    payload, err = _read_json(compat_path)
    if err:
        return attached, [_error("pack_compat_manifest_invalid", "$.pack.compat", "unable to parse pack.compat.json")], []
    report = validate_pack_compat_manifest(
        repo_root=repo_root,
        pack_row=attached,
        manifest_payload=payload,
        schema_repo_root=schema_repo_root,
    )
    if report.get("result") != "complete":
        return attached, list(report.get("errors") or []), list(report.get("warnings") or [])
    attached["compat_manifest_path"] = os.path.relpath(compat_path, repo_root).replace("\\", "/")
    attached["compat_manifest_hash"] = str(report.get("compat_manifest_hash", "")).strip()
    attached["compat_manifest"] = dict(report.get("compat_manifest") or {})
    attached["pack_degrade_mode_id"] = str(report.get("degrade_mode_id", "")).strip()
    return attached, [], list(report.get("warnings") or [])
