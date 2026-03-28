"""Deterministic save manifest normalization, validation, and open-policy helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Mapping, Tuple

from appshell.paths import VROOT_SAVES, get_current_virtual_paths, vpath_candidate_roots
from compat.migration_lifecycle import (
    ARTIFACT_KIND_SAVE,
    DECISION_MIGRATE,
    DECISION_READ_ONLY,
    DECISION_REFUSE,
    REFUSAL_MIGRATION_NOT_ALLOWED,
    determine_migration_decision,
)
from meta.identity import UNIVERSAL_IDENTITY_FIELD
from meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256


SAVE_MANIFEST_NAME = "save.manifest.json"
CURRENT_SAVE_FORMAT_VERSION = "1.0.0"
DEFAULT_CONTRACT_BUNDLE_REF = "universe_contract_bundle.json"

REFUSAL_SAVE_HASH_MISMATCH = "refusal.save.hash_mismatch"
REFUSAL_SAVE_CONTRACT_MISMATCH = "refusal.save.contract_mismatch"
REFUSAL_SAVE_PACK_LOCK_MISMATCH = "refusal.save.pack_lock_mismatch"
REFUSAL_SAVE_MIGRATION_REQUIRED = "refusal.save.migration_required"
REFUSAL_SAVE_MANIFEST_REQUIRED = "refusal.save.manifest_required"
REFUSAL_SAVE_READ_ONLY_REQUIRED = "refusal.save.read_only_required"
REFUSAL_SAVE_BUILD_MISMATCH = "refusal.save.build_mismatch"

PATH_LIKE_KEYS = {
    "contract_bundle_ref",
    "patches_ref",
    "proofs_ref",
    "state_snapshots_ref",
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: object) -> str:
    token = str(path or "").replace("\\", "/")
    if token.startswith("./"):
        token = token[2:]
    return token


def _normalize_value(value: object, key: str = "") -> object:
    if isinstance(value, Mapping):
        return {
            str(name): _normalize_value(item, str(name))
            for name, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    if isinstance(value, str):
        if key in PATH_LIKE_KEYS or key.endswith(("_path", "_ref", "_root")):
            return _norm(value)
        return value
    return value


def write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.abspath(str(path or "").strip())
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            _normalize_value(normalize_extensions_tree(dict(payload or {}))),
            handle,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        handle.write("\n")
    return target


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["deterministic_fingerprint"] = ""
        body.pop(UNIVERSAL_IDENTITY_FIELD, None)
    return canonical_sha256(body)


def stable_save_id(seed_payload: Mapping[str, object]) -> str:
    return "save.{}".format(
        canonical_sha256(_normalize_value(normalize_extensions_tree(dict(seed_payload or {}))))[:24]
    )


def stable_migration_event_id(seed_payload: Mapping[str, object]) -> str:
    return "migration_event.{}".format(
        canonical_sha256(_normalize_value(normalize_extensions_tree(dict(seed_payload or {}))))[:24]
    )


def save_semantic_contract_registry_hash(manifest: Mapping[str, object] | None) -> str:
    payload = _as_map(manifest)
    token = str(payload.get("semantic_contract_registry_hash", "")).strip()
    if token:
        return token
    return str(_as_map(payload.get("extensions")).get("official.semantic_contract_registry_hash", "")).strip()


def normalize_migration_event(
    payload: Mapping[str, object] | None,
    *,
    fallback_version: str = CURRENT_SAVE_FORMAT_VERSION,
) -> dict:
    row = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    tick_applied = int(_as_map(row).get("tick_applied", 0) or 0)
    from_version = str(_as_map(row).get("from_version", "")).strip() or str(fallback_version or CURRENT_SAVE_FORMAT_VERSION)
    to_version = str(_as_map(row).get("to_version", "")).strip() or from_version
    migration_id = str(_as_map(row).get("migration_id", "")).strip()
    seed = {
        "event_id": str(_as_map(row).get("event_id", "")).strip(),
        "from_version": from_version,
        "to_version": to_version,
        "migration_id": migration_id,
        "tick_applied": tick_applied,
    }
    out = {
        "event_id": seed["event_id"] or stable_migration_event_id(seed),
        "from_version": from_version,
        "to_version": to_version,
        "migration_id": migration_id or str(seed["event_id"] or "").strip() or "migration.unknown",
        "tick_applied": tick_applied,
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(_as_map(_as_map(row).get("extensions"))),
    }
    out["deterministic_fingerprint"] = deterministic_fingerprint(out)
    return _normalize_value(out)


def _normalize_migration_chain(values: object, *, fallback_version: str) -> List[dict]:
    rows: List[dict] = []
    for item in _as_list(values):
        if isinstance(item, Mapping):
            rows.append(normalize_migration_event(item, fallback_version=fallback_version))
            continue
        token = str(item or "").strip()
        if not token:
            continue
        rows.append(
            normalize_migration_event(
                {
                    "event_id": "",
                    "from_version": fallback_version,
                    "to_version": fallback_version,
                    "migration_id": token,
                    "tick_applied": 0,
                    "extensions": {
                        "official.legacy_ref_hash": token,
                    },
                },
                fallback_version=fallback_version,
            )
        )
    return rows


def normalize_save_manifest(payload: Mapping[str, object]) -> dict:
    manifest = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    save_format_version = str(manifest.get("save_format_version", manifest.get("format_version", CURRENT_SAVE_FORMAT_VERSION))).strip() or CURRENT_SAVE_FORMAT_VERSION
    contract_bundle_hash = str(
        manifest.get("universe_contract_bundle_hash", manifest.get("contract_bundle_hash", ""))
    ).strip()
    migration_chain = _normalize_migration_chain(manifest.get("migration_chain"), fallback_version=save_format_version)
    normalized = dict(manifest)
    normalized["save_id"] = str(manifest.get("save_id", "")).strip()
    normalized["save_format_version"] = save_format_version
    normalized["universe_identity_hash"] = str(manifest.get("universe_identity_hash", "")).strip()
    normalized["universe_contract_bundle_hash"] = contract_bundle_hash
    semantic_contract_registry_hash = save_semantic_contract_registry_hash(manifest)
    if semantic_contract_registry_hash:
        normalized["semantic_contract_registry_hash"] = semantic_contract_registry_hash
    normalized["generator_version_id"] = str(manifest.get("generator_version_id", "")).strip()
    normalized["realism_profile_id"] = str(manifest.get("realism_profile_id", "")).strip()
    normalized["pack_lock_hash"] = str(manifest.get("pack_lock_hash", "")).strip()
    normalized["overlay_manifest_hash"] = str(manifest.get("overlay_manifest_hash", "")).strip()
    normalized["mod_policy_id"] = str(manifest.get("mod_policy_id", "mod.policy.default")).strip() or "mod.policy.default"
    normalized["created_by_build_id"] = str(manifest.get("created_by_build_id", "")).strip()
    normalized["migration_chain"] = migration_chain
    normalized["allow_read_only_open"] = bool(manifest.get("allow_read_only_open", False))
    for field in ("contract_bundle_ref", "state_snapshots_ref", "patches_ref", "proofs_ref"):
        token = str(manifest.get(field, "")).strip()
        if token:
            normalized[field] = _norm(token)
    normalized["contract_bundle_hash"] = contract_bundle_hash
    normalized["format_version"] = save_format_version
    normalized["extensions"] = normalize_extensions_map(_as_map(manifest.get("extensions")))
    normalized["deterministic_fingerprint"] = str(manifest.get("deterministic_fingerprint", "")).strip()
    return _normalize_value(normalized)


def _required_fields(manifest: Mapping[str, object]) -> List[str]:
    required = (
        "save_id",
        "save_format_version",
        "universe_identity_hash",
        "universe_contract_bundle_hash",
        "generator_version_id",
        "realism_profile_id",
        "pack_lock_hash",
        "overlay_manifest_hash",
        "mod_policy_id",
        "created_by_build_id",
        "migration_chain",
        "deterministic_fingerprint",
        "extensions",
    )
    missing: List[str] = []
    for field in required:
        value = manifest.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if isinstance(value, list):
            continue
        if isinstance(value, dict):
            if field == "extensions":
                continue
            if value:
                continue
        missing.append(field)
    if "allow_read_only_open" not in manifest:
        missing.append("allow_read_only_open")
    return missing


def _migration_chain_errors(save_format_version: str, migration_chain: List[dict]) -> List[dict]:
    errors: List[dict] = []
    previous_to_version = ""
    for index, row in enumerate(list(migration_chain or [])):
        event = normalize_migration_event(row, fallback_version=save_format_version)
        if not str(event.get("event_id", "")).strip():
            errors.append(
                {
                    "code": "save_manifest_migration_event_missing_id",
                    "path": "$.migration_chain[{}].event_id".format(index),
                    "message": "migration event is missing event_id",
                }
            )
        if not str(event.get("migration_id", "")).strip():
            errors.append(
                {
                    "code": "save_manifest_migration_event_missing_migration_id",
                    "path": "$.migration_chain[{}].migration_id".format(index),
                    "message": "migration event is missing migration_id",
                }
            )
        if previous_to_version and previous_to_version != str(event.get("from_version", "")).strip():
            errors.append(
                {
                    "code": "save_manifest_migration_chain_gap",
                    "path": "$.migration_chain[{}].from_version".format(index),
                    "message": "migration chain ordering is non-canonical",
                }
            )
        previous_to_version = str(event.get("to_version", "")).strip()
    if migration_chain and previous_to_version and previous_to_version != str(save_format_version or "").strip():
        errors.append(
            {
                "code": "save_manifest_migration_chain_terminal_version_mismatch",
                "path": "$.save_format_version",
                "message": "save_format_version must match the terminal migration to_version",
            }
        )
    return errors


def validate_save_manifest(
    *,
    repo_root: str,
    save_manifest_path: str = "",
    manifest_payload: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    if manifest_payload is None:
        try:
            payload = json.load(open(save_manifest_path, "r", encoding="utf-8"))
        except (OSError, ValueError):
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_MANIFEST_REQUIRED,
                "errors": [
                    {
                        "code": "save_manifest_invalid",
                        "path": "$",
                        "message": "unable to load save manifest",
                    }
                ],
                "warnings": [],
                "save_manifest": {},
            }
    else:
        payload = dict(manifest_payload or {})

    manifest = normalize_save_manifest(payload)
    migration_decision_record = determine_migration_decision(
        repo_root,
        artifact_kind_id=ARTIFACT_KIND_SAVE,
        payload=manifest,
        allow_read_only=bool(manifest.get("allow_read_only_open", False)),
        expected_contract_bundle_hash=str(manifest.get("universe_contract_bundle_hash", "")).strip(),
        artifact_path=save_manifest_path,
    )
    errors: List[dict] = []
    warnings: List[dict] = []

    for field in _required_fields(manifest):
        errors.append(
            {
                "code": "save_manifest_missing_field",
                "path": "$.{}".format(field),
                "message": "missing required field '{}'".format(field),
            }
        )

    save_id = str(manifest.get("save_id", "")).strip()
    if save_id and ("/" in save_id or "\\" in save_id):
        errors.append(
            {
                "code": "save_manifest_invalid_save_id",
                "path": "$.save_id",
                "message": "save_id must not contain path separators",
            }
        )

    errors.extend(_migration_chain_errors(str(manifest.get("save_format_version", "")).strip(), list(manifest.get("migration_chain") or [])))

    expected = deterministic_fingerprint(manifest)
    if str(manifest.get("deterministic_fingerprint", "")).strip() != expected:
        errors.append(
            {
                "code": REFUSAL_SAVE_HASH_MISMATCH,
                "path": "$.deterministic_fingerprint",
                "message": "deterministic_fingerprint mismatch",
            }
        )

    result = "complete" if not errors else "refused"
    refusal_code = str(errors[0].get("code", "")).strip() if errors else ""
    return {
        "result": result,
        "refusal_code": refusal_code,
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "warnings": sorted(warnings, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "save_manifest": manifest,
        "migration_decision_record": migration_decision_record,
    }


def resolve_save_root(
    *,
    repo_root: str,
    install_root: str,
    instance_root: str,
    instance_manifest: Mapping[str, object] | None,
    save_id: str,
) -> str:
    token = str(save_id or "").strip()
    if not token:
        return ""
    candidates: List[str] = []
    if instance_root:
        candidates.append(os.path.join(instance_root, "saves", token))
    store_root = ""
    locator = _as_map(_as_map(instance_manifest).get("store_root"))
    root_path = str(locator.get("root_path", "")).strip()
    manifest_ref = str(locator.get("manifest_ref", "")).strip()
    if manifest_ref:
        store_root = os.path.dirname(
            os.path.abspath(manifest_ref if os.path.isabs(manifest_ref) else os.path.join(instance_root, manifest_ref))
        )
    elif root_path:
        store_root = os.path.abspath(root_path if os.path.isabs(root_path) else os.path.join(instance_root, root_path))
    if store_root:
        candidates.append(os.path.join(store_root, "saves", token))
    if install_root:
        candidates.append(os.path.join(install_root, "saves", token))
    context = get_current_virtual_paths()
    if context is not None and str(context.get("result", "")).strip() == "complete":
        for root in vpath_candidate_roots(VROOT_SAVES, context):
            candidates.append(os.path.join(root, token))
    if repo_root:
        candidates.append(os.path.join(repo_root, "saves", token))
    seen = set()
    for candidate in candidates:
        abs_candidate = os.path.abspath(candidate)
        if abs_candidate in seen:
            continue
        seen.add(abs_candidate)
        if os.path.isfile(os.path.join(abs_candidate, SAVE_MANIFEST_NAME)):
            return abs_candidate
    return ""


def resolve_save_manifest_path(
    *,
    repo_root: str,
    install_root: str,
    instance_root: str,
    instance_manifest: Mapping[str, object] | None,
    save_id: str,
) -> str:
    save_root = resolve_save_root(
        repo_root=repo_root,
        install_root=install_root,
        instance_root=instance_root,
        instance_manifest=instance_manifest,
        save_id=save_id,
    )
    if not save_root:
        return ""
    return os.path.join(save_root, SAVE_MANIFEST_NAME)


def load_save_contract_bundle(save_root: str, manifest: Mapping[str, object] | None = None) -> Tuple[dict, str, str]:
    manifest_payload = _as_map(manifest)
    candidate_refs: List[str] = []
    explicit_ref = str(manifest_payload.get("contract_bundle_ref", "")).strip()
    if explicit_ref:
        candidate_refs.append(explicit_ref)
    candidate_refs.extend(
        [
            DEFAULT_CONTRACT_BUNDLE_REF,
            os.path.join("proofs", DEFAULT_CONTRACT_BUNDLE_REF),
            os.path.join("proofs", "anchors", DEFAULT_CONTRACT_BUNDLE_REF),
        ]
    )
    seen = set()
    for rel_path in candidate_refs:
        norm_ref = _norm(rel_path)
        if norm_ref in seen:
            continue
        seen.add(norm_ref)
        abs_path = os.path.join(save_root, norm_ref.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            payload = json.load(open(abs_path, "r", encoding="utf-8"))
        except (OSError, ValueError):
            return {}, _norm(abs_path), "invalid"
        if not isinstance(payload, dict):
            return {}, _norm(abs_path), "invalid"
        return _normalize_value(normalize_extensions_tree(payload)), _norm(abs_path), ""
    return {}, "", "missing"


def save_read_only_allowed(
    manifest: Mapping[str, object] | None,
    *,
    run_mode: str,
    instance_allow_read_only_fallback: bool,
) -> bool:
    payload = _as_map(manifest)
    if not bool(payload.get("allow_read_only_open", False)):
        return False
    mode = str(run_mode or "").strip().lower()
    return bool(instance_allow_read_only_fallback) or mode in ("inspect", "replay")


def migrate_save_manifest(
    *,
    repo_root: str,
    save_manifest_path: str = "",
    manifest_payload: Mapping[str, object] | None = None,
    to_version: str = CURRENT_SAVE_FORMAT_VERSION,
    migration_id: str = "",
    tick_applied: int = 0,
) -> Dict[str, object]:
    validation = validate_save_manifest(
        repo_root=repo_root,
        save_manifest_path=save_manifest_path,
        manifest_payload=manifest_payload,
    )
    if validation.get("result") != "complete":
        return validation
    manifest = dict(validation.get("save_manifest") or {})
    current_version = str(manifest.get("save_format_version", CURRENT_SAVE_FORMAT_VERSION)).strip() or CURRENT_SAVE_FORMAT_VERSION
    target_version = str(to_version or CURRENT_SAVE_FORMAT_VERSION).strip() or CURRENT_SAVE_FORMAT_VERSION
    if current_version == target_version:
        return {
            "result": "complete",
            "save_manifest": manifest,
            "migration_event": {},
            "wrote_manifest": False,
        }
    migration_token = str(migration_id or "").strip() or "migration.save_format.{}_to_{}".format(current_version, target_version)
    event = normalize_migration_event(
        {
            "from_version": current_version,
            "to_version": target_version,
            "migration_id": migration_token,
            "tick_applied": int(tick_applied or 0),
            "extensions": {},
        },
        fallback_version=current_version,
    )
    updated = dict(manifest)
    updated["save_format_version"] = target_version
    updated["format_version"] = target_version
    updated["migration_chain"] = list(manifest.get("migration_chain") or []) + [event]
    updated["deterministic_fingerprint"] = ""
    updated["deterministic_fingerprint"] = deterministic_fingerprint(updated)
    updated_validation = validate_save_manifest(
        repo_root=repo_root,
        save_manifest_path=save_manifest_path,
        manifest_payload=updated,
    )
    if updated_validation.get("result") != "complete":
        return updated_validation
    wrote_manifest = False
    if save_manifest_path:
        write_json(save_manifest_path, dict(updated_validation.get("save_manifest") or updated))
        wrote_manifest = True
    return {
        "result": "complete",
        "save_manifest": dict(updated_validation.get("save_manifest") or updated),
        "migration_event": event,
        "wrote_manifest": wrote_manifest,
    }


def evaluate_save_open(
    *,
    repo_root: str,
    save_manifest_path: str,
    instance_manifest: Mapping[str, object] | None,
    install_manifest: Mapping[str, object] | None,
    pack_lock_payload: Mapping[str, object] | None,
    run_mode: str,
    instance_allow_read_only_fallback: bool = False,
    allow_save_migration: bool = False,
    migration_tick: int = 0,
    migration_id: str = "",
) -> Dict[str, object]:
    validation = validate_save_manifest(
        repo_root=repo_root,
        save_manifest_path=save_manifest_path,
    )
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", REFUSAL_SAVE_MANIFEST_REQUIRED)).strip() or REFUSAL_SAVE_MANIFEST_REQUIRED,
            "save_manifest": dict(validation.get("save_manifest") or {}),
            "save_validation": validation,
            "degrade_reasons": [],
            "migration_applied": False,
            "migration_required": False,
            "read_only_required": False,
        }

    save_manifest = dict(validation.get("save_manifest") or {})
    migration_decision_record = dict(validation.get("migration_decision_record") or {})
    save_root = os.path.dirname(os.path.abspath(save_manifest_path))
    read_only_allowed = save_read_only_allowed(
        save_manifest,
        run_mode=run_mode,
        instance_allow_read_only_fallback=instance_allow_read_only_fallback,
    )
    degrade_reasons: List[str] = []
    migration_applied = False
    decision_action_id = str(migration_decision_record.get("decision_action_id", "")).strip()

    contract_bundle_payload, contract_bundle_path, contract_bundle_error = load_save_contract_bundle(save_root, save_manifest)
    contract_bundle_hash = canonical_sha256(contract_bundle_payload) if contract_bundle_payload else ""
    if contract_bundle_error:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_SAVE_CONTRACT_MISMATCH,
            "save_manifest": save_manifest,
            "save_validation": validation,
            "contract_bundle_path": contract_bundle_path,
            "contract_bundle_error": contract_bundle_error,
            "degrade_reasons": [],
            "migration_applied": False,
            "migration_required": False,
            "read_only_required": False,
        }

    if contract_bundle_hash != str(save_manifest.get("universe_contract_bundle_hash", "")).strip():
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_CONTRACT_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "contract_bundle_path": contract_bundle_path,
                "contract_bundle_hash": contract_bundle_hash,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_contract_bundle_mismatch")

    expected_registry_hash = save_semantic_contract_registry_hash(save_manifest)
    install_registry_hash = str(_as_map(install_manifest).get("semantic_contract_registry_hash", "")).strip()
    lock_registry_hash = str(_as_map(pack_lock_payload).get("semantic_contract_registry_hash", "")).strip()
    if expected_registry_hash and install_registry_hash and expected_registry_hash != install_registry_hash:
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_CONTRACT_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_registry_hash_mismatch")
    if expected_registry_hash and lock_registry_hash and expected_registry_hash != lock_registry_hash:
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_CONTRACT_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_pack_registry_hash_mismatch")

    expected_pack_lock_hash = str(save_manifest.get("pack_lock_hash", "")).strip()
    actual_pack_lock_hash = str(_as_map(pack_lock_payload).get("pack_lock_hash", "")).strip()
    if expected_pack_lock_hash and actual_pack_lock_hash and expected_pack_lock_hash != actual_pack_lock_hash:
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_PACK_LOCK_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_pack_lock_mismatch")

    lock_contract_bundle_hash = str(_as_map(pack_lock_payload).get("engine_contract_bundle_hash", "")).strip()
    if lock_contract_bundle_hash and lock_contract_bundle_hash != str(save_manifest.get("universe_contract_bundle_hash", "")).strip():
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_CONTRACT_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_engine_contract_mismatch")

    install_product_builds = {
        str(key): str(value).strip()
        for key, value in sorted(_as_map(_as_map(install_manifest).get("product_builds")).items(), key=lambda row: str(row[0]))
    }
    created_by_build_id = str(save_manifest.get("created_by_build_id", "")).strip()
    if created_by_build_id and created_by_build_id not in set(install_product_builds.values()):
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_BUILD_MISMATCH,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": False,
            }
        degrade_reasons.append("save_created_by_build_mismatch")

    if decision_action_id == DECISION_REFUSE:
        refusal_code = str(migration_decision_record.get("refusal_code", "")).strip() or REFUSAL_MIGRATION_NOT_ALLOWED
        return {
            "result": "refused",
            "refusal_code": refusal_code,
            "save_manifest": save_manifest,
            "save_validation": validation,
            "migration_decision_record": migration_decision_record,
            "degrade_reasons": [],
            "migration_applied": False,
            "migration_required": False,
            "read_only_required": False,
        }

    migration_required = decision_action_id == DECISION_MIGRATE
    if migration_required:
        if allow_save_migration:
            migration = migrate_save_manifest(
                repo_root=repo_root,
                save_manifest_path=save_manifest_path,
                manifest_payload=save_manifest,
                to_version=str(migration_decision_record.get("target_version", CURRENT_SAVE_FORMAT_VERSION)).strip() or CURRENT_SAVE_FORMAT_VERSION,
                migration_id=migration_id,
                tick_applied=migration_tick,
            )
            if migration.get("result") != "complete":
                return {
                    "result": "refused",
                    "refusal_code": REFUSAL_SAVE_MIGRATION_REQUIRED,
                    "save_manifest": save_manifest,
                    "save_validation": validation,
                    "migration_result": migration,
                    "degrade_reasons": [],
                    "migration_applied": False,
                    "migration_required": True,
                    "read_only_required": False,
                }
            save_manifest = dict(migration.get("save_manifest") or save_manifest)
            migration_applied = True
            migration_required = False
        elif not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_MIGRATION_REQUIRED,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": True,
                "read_only_required": False,
            }
        else:
            degrade_reasons.append("save_migration_required")
    elif decision_action_id == DECISION_READ_ONLY:
        if not read_only_allowed:
            return {
                "result": "refused",
                "refusal_code": REFUSAL_SAVE_READ_ONLY_REQUIRED,
                "save_manifest": save_manifest,
                "save_validation": validation,
                "migration_decision_record": migration_decision_record,
                "degrade_reasons": [],
                "migration_applied": False,
                "migration_required": False,
                "read_only_required": True,
            }
        degrade_reasons.append("save_read_only_forward_version")

    read_only_required = bool(degrade_reasons)
    return {
        "result": "complete",
        "refusal_code": "",
        "save_manifest": save_manifest,
        "save_validation": validation,
        "save_manifest_path": _norm(save_manifest_path),
        "save_root": _norm(save_root),
        "contract_bundle_path": contract_bundle_path,
        "contract_bundle_hash": contract_bundle_hash,
        "expected_contract_bundle_hash": str(save_manifest.get("universe_contract_bundle_hash", "")).strip(),
        "migration_decision_record": migration_decision_record,
        "degrade_reasons": degrade_reasons,
        "migration_applied": migration_applied,
        "migration_required": migration_required,
        "read_only_required": read_only_required,
        "read_only_allowed": read_only_allowed,
    }


__all__ = [
    "CURRENT_SAVE_FORMAT_VERSION",
    "DEFAULT_CONTRACT_BUNDLE_REF",
    "REFUSAL_SAVE_BUILD_MISMATCH",
    "REFUSAL_SAVE_CONTRACT_MISMATCH",
    "REFUSAL_SAVE_HASH_MISMATCH",
    "REFUSAL_SAVE_MANIFEST_REQUIRED",
    "REFUSAL_SAVE_MIGRATION_REQUIRED",
    "REFUSAL_SAVE_PACK_LOCK_MISMATCH",
    "REFUSAL_SAVE_READ_ONLY_REQUIRED",
    "SAVE_MANIFEST_NAME",
    "deterministic_fingerprint",
    "evaluate_save_open",
    "load_save_contract_bundle",
    "migrate_save_manifest",
    "normalize_migration_event",
    "normalize_save_manifest",
    "resolve_save_manifest_path",
    "resolve_save_root",
    "save_read_only_allowed",
    "save_semantic_contract_registry_hash",
    "stable_migration_event_id",
    "stable_save_id",
    "validate_save_manifest",
    "write_json",
]
