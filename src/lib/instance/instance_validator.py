"""Deterministic instance manifest normalization and validation helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Mapping, Tuple

from src.meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256


INSTANCE_KIND_CLIENT = "instance.client"
INSTANCE_KIND_SERVER = "instance.server"
INSTANCE_KIND_TOOLING = "instance.tooling"
INSTANCE_KIND_VALUES = (
    INSTANCE_KIND_CLIENT,
    INSTANCE_KIND_SERVER,
    INSTANCE_KIND_TOOLING,
)
SEED_POLICY_VALUES = (
    "fixed",
    "prompt",
    "deterministic_counter",
)
UI_MODE_VALUES = (
    "cli",
    "tui",
    "rendered",
)
RENDERER_MODE_VALUES = (
    "",
    "software",
    "hardware_stub",
)
LAST_OPENED_SAVE_ID_KEY = "instance.last_opened_save_id"

REFUSAL_INSTANCE_HASH_MISMATCH = "refusal.instance.hash_mismatch"
REFUSAL_INSTANCE_INVALID_SAVE_REF = "refusal.instance.invalid_save_ref"
REFUSAL_INSTANCE_MISSING_LOCK = "refusal.instance.missing_lock"
REFUSAL_INSTANCE_MISSING_PROFILE_BUNDLE = "refusal.instance.missing_profile_bundle"

PATH_LIKE_KEYS = {
    "artifact_path",
    "binary_ref",
    "capability_lockfile",
    "descriptor_ref",
    "manifest_ref",
    "path",
    "root_path",
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
    return canonical_sha256(body)


def stable_instance_id(seed_payload: Mapping[str, object]) -> str:
    return "instance.{}".format(
        canonical_sha256(_normalize_value(normalize_extensions_tree(dict(seed_payload or {}))))[:24]
    )


def _sorted_unique_strings(values: object) -> List[str]:
    ordered = {
        str(value).strip()
        for value in _as_list(values)
        if str(value).strip()
    }
    return sorted(ordered)


def _normalize_install_ref(payload: Mapping[str, object] | None, fallback_install_id: str) -> dict:
    row = _as_map(payload)
    return {
        "install_id": str(row.get("install_id", "")).strip() or str(fallback_install_id or "").strip(),
        "manifest_ref": _norm(row.get("manifest_ref", "")),
        "root_path": _norm(row.get("root_path", "")),
    }


def _normalize_store_ref(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    return {
        "store_id": str(row.get("store_id", "")).strip(),
        "root_path": _norm(row.get("root_path", "")),
        "manifest_ref": _norm(row.get("manifest_ref", "")),
    }


def _normalize_embedded_artifacts(values: object) -> List[dict]:
    rows: List[dict] = []
    for row in _as_list(values):
        payload = _as_map(row)
        if not payload:
            continue
        rows.append(
            {
                "artifact_hash": str(payload.get("artifact_hash", "")).strip(),
                "artifact_id": str(payload.get("artifact_id", "")).strip(),
                "artifact_path": _norm(payload.get("artifact_path", "")),
                "artifact_type": str(payload.get("artifact_type", "")).strip(),
                "category": str(payload.get("category", "")).strip(),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("category", "")),
            str(row.get("artifact_hash", "")),
            str(row.get("artifact_id", "")),
        ),
    )


def _normalize_required_product_builds(values: object) -> Dict[str, str]:
    payload = _as_map(values)
    return {
        str(key): str(value).strip()
        for key, value in sorted(payload.items(), key=lambda row: str(row[0]))
        if str(key).strip() and str(value).strip()
    }


def _normalize_required_contract_ranges(values: object) -> Dict[str, dict]:
    payload = _as_map(values)
    rows: Dict[str, dict] = {}
    for contract_id, row in sorted(payload.items(), key=lambda item: str(item[0])):
        token = str(contract_id or "").strip()
        if not token:
            continue
        item = _as_map(row)
        min_version = int(item.get("min_version", 1) or 1)
        max_version = int(item.get("max_version", min_version) or min_version)
        if max_version < min_version:
            max_version = min_version
        normalized = {
            "contract_category_id": str(item.get("contract_category_id", token)).strip() or token,
            "min_version": min_version,
            "max_version": max_version,
            "deterministic_fingerprint": "",
            "extensions": normalize_extensions_map(_as_map(item.get("extensions"))),
        }
        normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
        rows[token] = normalized
    return dict((key, rows[key]) for key in sorted(rows.keys()))


def normalize_instance_settings(payload: Mapping[str, object] | None) -> dict:
    settings = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    out = dict(settings if isinstance(settings, dict) else {})
    renderer_mode = str(out.get("renderer_mode", "") or "").strip()
    ui_mode_default = str(out.get("ui_mode_default", "") or "").strip()
    out["renderer_mode"] = renderer_mode if renderer_mode in RENDERER_MODE_VALUES else None
    out["ui_mode_default"] = ui_mode_default if ui_mode_default in UI_MODE_VALUES else "cli"
    out["allow_read_only_fallback"] = bool(out.get("allow_read_only_fallback", False))
    out["tick_budget_policy_id"] = str(out.get("tick_budget_policy_id", "tick.budget.default")).strip() or "tick.budget.default"
    out["compute_profile_id"] = str(out.get("compute_profile_id", "compute.profile.default")).strip() or "compute.profile.default"
    out["data_root"] = _norm(out.get("data_root", ".") or ".") or "."
    out["active_profiles"] = _sorted_unique_strings(out.get("active_profiles"))
    out["active_modpacks"] = _sorted_unique_strings(out.get("active_modpacks"))
    out["sandbox_policy_ref"] = str(out.get("sandbox_policy_ref", "sandbox.default")).strip() or "sandbox.default"
    out["update_channel"] = str(out.get("update_channel", "stable")).strip() or "stable"
    out["extensions"] = normalize_extensions_map(_as_map(out.get("extensions")))
    out["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = deterministic_fingerprint(out)
    return _normalize_value(out)


def instance_install_id(manifest: Mapping[str, object] | None) -> str:
    payload = _as_map(manifest)
    install_ref = _as_map(payload.get("install_ref"))
    return str(install_ref.get("install_id", "")).strip() or str(payload.get("install_id", "")).strip()


def instance_settings_payload(manifest: Mapping[str, object] | None) -> dict:
    payload = _as_map(manifest)
    settings = _as_map(payload.get("instance_settings"))
    if settings:
        return normalize_instance_settings(settings)
    return normalize_instance_settings(
        {
            "data_root": payload.get("data_root", "."),
            "active_profiles": payload.get("active_profiles") or [],
            "active_modpacks": payload.get("active_modpacks") or [],
            "sandbox_policy_ref": payload.get("sandbox_policy_ref", "sandbox.default"),
            "update_channel": payload.get("update_channel", "stable"),
            "renderer_mode": payload.get("renderer_mode"),
            "ui_mode_default": payload.get("ui_mode_default", "cli"),
            "allow_read_only_fallback": payload.get("allow_read_only_fallback", False),
            "tick_budget_policy_id": payload.get("tick_budget_policy_id", "tick.budget.default"),
            "compute_profile_id": payload.get("compute_profile_id", "compute.profile.default"),
            "extensions": {},
        }
    )


def instance_data_root(manifest: Mapping[str, object] | None) -> str:
    settings = instance_settings_payload(manifest)
    return str(settings.get("data_root", ".")).strip() or "."


def instance_active_profiles(manifest: Mapping[str, object] | None) -> List[str]:
    settings = instance_settings_payload(manifest)
    return list(settings.get("active_profiles") or [])


def instance_active_modpacks(manifest: Mapping[str, object] | None) -> List[str]:
    settings = instance_settings_payload(manifest)
    return list(settings.get("active_modpacks") or [])


def instance_allow_read_only_fallback(manifest: Mapping[str, object] | None) -> bool:
    settings = instance_settings_payload(manifest)
    return bool(settings.get("allow_read_only_fallback", False))


def instance_ui_mode_default(manifest: Mapping[str, object] | None) -> str:
    settings = instance_settings_payload(manifest)
    return str(settings.get("ui_mode_default", "cli")).strip() or "cli"


def instance_last_opened_save_id(manifest: Mapping[str, object] | None) -> str:
    payload = _as_map(manifest)
    extensions = _as_map(payload.get("extensions"))
    token = str(extensions.get(LAST_OPENED_SAVE_ID_KEY, "")).strip()
    if token:
        return token
    settings = instance_settings_payload(payload)
    return str(_as_map(settings.get("extensions")).get(LAST_OPENED_SAVE_ID_KEY, "")).strip()


def _normalize_embedded_builds(values: object) -> Dict[str, dict]:
    payload = _as_map(values)
    out: Dict[str, dict] = {}
    for product_id, row in sorted(payload.items(), key=lambda item: str(item[0])):
        token = str(product_id or "").strip()
        if not token:
            continue
        item = _as_map(row)
        normalized = {
            "product_id": str(item.get("product_id", token)).strip() or token,
            "build_id": str(item.get("build_id", "")).strip(),
            "binary_hash": str(item.get("binary_hash", "")).strip(),
            "endpoint_descriptor_hash": str(item.get("endpoint_descriptor_hash", "")).strip(),
            "binary_ref": _norm(item.get("binary_ref", "")),
            "descriptor_ref": _norm(item.get("descriptor_ref", "")),
            "deterministic_fingerprint": "",
            "extensions": normalize_extensions_map(_as_map(item.get("extensions"))),
        }
        normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
        out[token] = normalized
    return dict((key, out[key]) for key in sorted(out.keys()))


def normalize_instance_manifest(payload: Mapping[str, object]) -> dict:
    manifest = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    install_id = str(_as_map(manifest.get("install_ref")).get("install_id", "")).strip() or str(manifest.get("install_id", "")).strip()
    install_ref = _normalize_install_ref(manifest.get("install_ref"), install_id)
    settings = instance_settings_payload(manifest)
    save_refs = _sorted_unique_strings(manifest.get("save_refs") or manifest.get("save_ids") or [])
    last_opened_save_id = instance_last_opened_save_id(manifest)
    if last_opened_save_id and last_opened_save_id not in save_refs:
        save_refs = sorted(set(save_refs + [last_opened_save_id]))
    extensions = normalize_extensions_map(_as_map(manifest.get("extensions")))
    if last_opened_save_id:
        extensions[LAST_OPENED_SAVE_ID_KEY] = last_opened_save_id
    else:
        extensions.pop(LAST_OPENED_SAVE_ID_KEY, None)
    mode = str(manifest.get("mode", "portable")).strip().lower() or "portable"
    if mode not in ("linked", "portable"):
        mode = "portable"
    instance_kind = str(manifest.get("instance_kind", INSTANCE_KIND_CLIENT)).strip() or INSTANCE_KIND_CLIENT
    if instance_kind not in INSTANCE_KIND_VALUES:
        instance_kind = INSTANCE_KIND_CLIENT
    seed_policy = str(manifest.get("seed_policy", "prompt")).strip() or "prompt"
    if seed_policy not in SEED_POLICY_VALUES:
        seed_policy = "prompt"

    normalized = dict(manifest)
    normalized["instance_id"] = str(manifest.get("instance_id", "")).strip()
    normalized["instance_kind"] = instance_kind
    normalized["mode"] = mode
    normalized["install_ref"] = install_ref
    normalized["embedded_builds"] = _normalize_embedded_builds(manifest.get("embedded_builds"))
    normalized["pack_lock_hash"] = str(manifest.get("pack_lock_hash", "")).strip()
    normalized["profile_bundle_hash"] = str(manifest.get("profile_bundle_hash", "")).strip()
    normalized["mod_policy_id"] = str(manifest.get("mod_policy_id", "mod.policy.default")).strip() or "mod.policy.default"
    normalized["overlay_conflict_policy_id"] = str(
        manifest.get("overlay_conflict_policy_id", "overlay.conflict.default")
    ).strip() or "overlay.conflict.default"
    normalized["default_session_template_id"] = str(
        manifest.get("default_session_template_id", "session.template.default")
    ).strip() or "session.template.default"
    normalized["seed_policy"] = seed_policy
    normalized["instance_settings"] = settings
    normalized["save_refs"] = save_refs
    normalized["required_product_builds"] = _normalize_required_product_builds(manifest.get("required_product_builds"))
    normalized["required_contract_ranges"] = _normalize_required_contract_ranges(manifest.get("required_contract_ranges"))
    normalized["store_root"] = _normalize_store_ref(manifest.get("store_root"))
    normalized["embedded_artifacts"] = _normalize_embedded_artifacts(manifest.get("embedded_artifacts"))
    normalized["extensions"] = extensions

    # Legacy compatibility fields remain populated for older launcher/setup flows.
    normalized["install_id"] = install_ref.get("install_id", "")
    normalized["data_root"] = str(settings.get("data_root", ".")).strip() or "."
    normalized["active_profiles"] = list(settings.get("active_profiles") or [])
    normalized["active_modpacks"] = list(settings.get("active_modpacks") or [])
    normalized["capability_lockfile"] = _norm(
        manifest.get("capability_lockfile", "lockfiles/capabilities.lock" if mode == "portable" else "")
    )
    normalized["sandbox_policy_ref"] = str(settings.get("sandbox_policy_ref", "sandbox.default")).strip() or "sandbox.default"
    normalized["update_channel"] = str(settings.get("update_channel", "stable")).strip() or "stable"
    normalized["created_at"] = str(manifest.get("created_at", "")).strip()
    normalized["last_used_at"] = str(manifest.get("last_used_at", "")).strip()
    normalized["deterministic_fingerprint"] = str(manifest.get("deterministic_fingerprint", "")).strip()
    return _normalize_value(normalized)


def _required_fields(manifest: Mapping[str, object]) -> List[str]:
    required = (
        "instance_id",
        "instance_kind",
        "mode",
        "pack_lock_hash",
        "profile_bundle_hash",
        "mod_policy_id",
        "overlay_conflict_policy_id",
        "default_session_template_id",
        "seed_policy",
        "instance_settings",
        "deterministic_fingerprint",
        "extensions",
    )
    missing: List[str] = []
    for field in required:
        value = manifest.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if isinstance(value, dict):
            if field in ("instance_settings", "extensions"):
                continue
            if value:
                continue
        missing.append(field)
    if "save_refs" not in manifest:
        missing.append("save_refs")
    return missing


def _invalid_save_refs(save_refs: List[str]) -> List[str]:
    invalid = []
    for token in list(save_refs or []):
        save_id = str(token or "").strip()
        if not save_id:
            invalid.append(save_id)
            continue
        if "/" in save_id or "\\" in save_id:
            invalid.append(save_id)
    return invalid


def validate_instance_manifest(
    *,
    repo_root: str,
    instance_manifest_path: str = "",
    manifest_payload: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    del repo_root
    manifest = normalize_instance_manifest(
        manifest_payload if manifest_payload is not None else json.load(open(instance_manifest_path, "r", encoding="utf-8"))
    )
    missing = _required_fields(manifest)
    if missing:
        refusal_code = REFUSAL_INSTANCE_MISSING_LOCK if "pack_lock_hash" in missing else REFUSAL_INSTANCE_MISSING_PROFILE_BUNDLE
        return {
            "result": "refused",
            "refusal_code": refusal_code,
            "missing_fields": missing,
            "instance_manifest": manifest,
        }
    if str(manifest.get("mode", "")).strip() == "linked" and not str(_as_map(manifest.get("install_ref")).get("install_id", "")).strip():
        return {
            "result": "refused",
            "refusal_code": REFUSAL_INSTANCE_MISSING_PROFILE_BUNDLE,
            "message": "linked instances require install_ref.install_id",
            "instance_manifest": manifest,
        }
    if str(manifest.get("mode", "")).strip() == "portable":
        embedded_builds = _as_map(manifest.get("embedded_builds"))
        install_ref = _as_map(manifest.get("install_ref"))
        if not embedded_builds and not str(install_ref.get("install_id", "")).strip():
            return {
                "result": "refused",
                "refusal_code": REFUSAL_INSTANCE_MISSING_PROFILE_BUNDLE,
                "message": "portable instances require install_ref or embedded_builds",
                "instance_manifest": manifest,
            }
    invalid_save_refs = _invalid_save_refs(list(manifest.get("save_refs") or []))
    if invalid_save_refs:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_INSTANCE_INVALID_SAVE_REF,
            "invalid_save_refs": invalid_save_refs,
            "instance_manifest": manifest,
        }
    expected = deterministic_fingerprint(manifest)
    if str(manifest.get("deterministic_fingerprint", "")).strip() != expected:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_INSTANCE_HASH_MISMATCH,
            "expected_deterministic_fingerprint": expected,
            "actual_deterministic_fingerprint": str(manifest.get("deterministic_fingerprint", "")).strip(),
            "instance_manifest": manifest,
        }
    return {
        "result": "complete",
        "instance_manifest": manifest,
    }
