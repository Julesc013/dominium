"""Deterministic release-index and update-plan resolution helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from src.lib.install import merge_protocol_ranges, normalize_install_manifest
from src.governance import governance_profile_hash
from src.meta.identity import (
    UNIVERSAL_IDENTITY_FIELD,
    canonicalize_universal_identity_block,
)
from src.release.component_graph_resolver import (
    COMPONENT_KIND_BINARY,
    COMPONENT_KIND_DOCS,
    COMPONENT_KIND_LOCK,
    COMPONENT_KIND_MANIFEST,
    COMPONENT_KIND_PACK,
    COMPONENT_KIND_PROFILE,
    YANK_POLICY_REFUSE,
    YANK_POLICY_WARN,
    canonicalize_component_descriptor,
    canonicalize_component_graph,
    canonicalize_install_plan,
    deterministic_fingerprint,
    resolve_component_graph,
)
from src.security.trust import ARTIFACT_KIND_RELEASE_INDEX, verify_artifact_trust
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_RELEASE_INDEX_REL = os.path.join("manifests", "release_index.json")
DEFAULT_INSTALL_TRANSACTION_LOG_REL = os.path.join(".dsu", "install_transaction_log.json")
DEFAULT_RELEASE_RESOLUTION_POLICY_REGISTRY_REL = os.path.join("data", "registries", "release_resolution_policy_registry.json")
DEFAULT_RELEASE_SERIES = "0.x"
RESOLUTION_POLICY_EXACT_SUITE = "policy.exact_suite"
RESOLUTION_POLICY_LATEST_COMPATIBLE = "policy.latest_compatible"
RESOLUTION_POLICY_LAB = "policy.lab"
DEFAULT_RELEASE_RESOLUTION_POLICY_ID = RESOLUTION_POLICY_EXACT_SUITE
LEGACY_RELEASE_RESOLUTION_POLICY_ALIASES = {
    "exact_suite": RESOLUTION_POLICY_EXACT_SUITE,
    "install.policy.exact_suite": RESOLUTION_POLICY_EXACT_SUITE,
    "latest_compatible": RESOLUTION_POLICY_LATEST_COMPATIBLE,
    "install.policy.latest_compatible": RESOLUTION_POLICY_LATEST_COMPATIBLE,
    "lab": RESOLUTION_POLICY_LAB,
    "install.policy.lab": RESOLUTION_POLICY_LAB,
}

REFUSAL_RELEASE_INDEX_MISSING = "refusal.update.index_missing"
REFUSAL_UPDATE_CONTRACT_INCOMPATIBLE = "refusal.update.contract_incompatible"
REFUSAL_UPDATE_PROTOCOL_INCOMPATIBLE = "refusal.update.protocol_incompatible"
REFUSAL_UPDATE_TRUST_UNMET = "refusal.update.trust_unmet"
REFUSAL_UPDATE_PLATFORM_UNAVAILABLE = "refusal.update.platform_unavailable"
REFUSAL_UPDATE_COMPONENT_GRAPH_MISSING = "refusal.update.component_graph_missing"
REFUSAL_UPDATE_INSTALL_PROFILE_MISSING = "refusal.update.install_profile_missing"
REFUSAL_UPDATE_RELEASE_UNAVAILABLE = "refusal.update.release_unavailable"
REFUSAL_UPDATE_YANKED_COMPONENT = "refusal.update.yanked_component"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_unique_strings(values: object) -> list[str]:
    return sorted({str(value).strip() for value in _as_list(values) if str(value).strip()})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _canonical_release_resolution_policy_id(value: object) -> str:
    token = _token(value)
    return _token(LEGACY_RELEASE_RESOLUTION_POLICY_ALIASES.get(token, token))


def _stable_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    token = _token(value).lower()
    return token in {"1", "true", "yes", "on"}


def canonicalize_release_resolution_policy(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "policy_id": _canonical_release_resolution_policy_id(item.get("policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
        "selection_rule_id": _token(item.get("selection_rule_id")) or "selection.exact_suite_component_graph_pin",
        "allow_yanked": _stable_bool(item.get("allow_yanked")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _builtin_release_resolution_policy_rows() -> list[dict]:
    return [
        canonicalize_release_resolution_policy(
            {
                "policy_id": RESOLUTION_POLICY_EXACT_SUITE,
                "selection_rule_id": "selection.exact_suite_component_graph_pin",
                "allow_yanked": True,
                "extensions": {
                    "cli_alias": "exact_suite",
                    "description": "Select the suite-pinned component descriptor for each selected component id.",
                },
            }
        ),
        canonicalize_release_resolution_policy(
            {
                "policy_id": RESOLUTION_POLICY_LATEST_COMPATIBLE,
                "selection_rule_id": "selection.highest_semver_build_artifact",
                "allow_yanked": False,
                "extensions": {
                    "cli_alias": "latest_compatible",
                    "description": "Select the highest compatible non-yanked candidate for each selected component id.",
                },
            }
        ),
        canonicalize_release_resolution_policy(
            {
                "policy_id": RESOLUTION_POLICY_LAB,
                "selection_rule_id": "selection.latest_compatible_explicit_opt_in",
                "allow_yanked": True,
                "extensions": {
                    "cli_alias": "lab",
                    "description": "Select the highest compatible candidate for each selected component id, including yanked candidates when explicitly requested.",
                    "requires_explicit_confirmation": True,
                },
            }
        ),
    ]


def load_release_resolution_policy_registry(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), DEFAULT_RELEASE_RESOLUTION_POLICY_REGISTRY_REL))


def select_release_resolution_policy(
    registry_payload: Mapping[str, object] | None,
    *,
    policy_id: str = "",
) -> dict:
    record = _as_map(_as_map(registry_payload).get("record"))
    rows = [
        canonicalize_release_resolution_policy(row)
        for row in _as_list(record.get("release_resolution_policies"))
        if _token(_as_map(row).get("policy_id"))
    ]
    if not rows:
        rows = _builtin_release_resolution_policy_rows()
    rows = sorted(rows, key=lambda row: _token(row.get("policy_id")))
    selected_id = _canonical_release_resolution_policy_id(policy_id)
    if selected_id:
        for row in rows:
            if _token(row.get("policy_id")) == selected_id:
                return dict(row)
        return {}
    for row in rows:
        if _token(row.get("policy_id")) == DEFAULT_RELEASE_RESOLUTION_POLICY_ID:
            return dict(row)
    return dict(rows[0]) if rows else {}


def _descriptor_artifact_id(payload: Mapping[str, object] | None) -> str:
    item = canonicalize_component_descriptor(payload)
    extensions = _as_map(item.get("extensions"))
    artifact_id = _token(extensions.get("artifact_id"))
    if artifact_id:
        return artifact_id
    managed_paths = _sorted_unique_strings(extensions.get("managed_paths"))
    if managed_paths:
        return managed_paths[0]
    return _token(extensions.get("product_id")) or _token(extensions.get("pack_id")) or _token(item.get("component_id"))


def _semver_key(version: object) -> tuple:
    token = _token(version)
    if token.lower().startswith("v"):
        token = token[1:]
    build_split = token.split("+", 1)[0]
    if "-" in build_split:
        core, prerelease = build_split.split("-", 1)
    else:
        core, prerelease = build_split, ""
    core_parts = []
    for part in core.split("."):
        try:
            core_parts.append(int(part))
        except ValueError:
            core_parts.append(0)
    while len(core_parts) < 3:
        core_parts.append(0)
    prerelease_parts = []
    if prerelease:
        for part in prerelease.split("."):
            if part.isdigit():
                prerelease_parts.append((0, int(part)))
            else:
                prerelease_parts.append((1, part))
    release_weight = 1 if not prerelease_parts else 0
    return (tuple(core_parts[:3]), release_weight, tuple(prerelease_parts))


def _component_descriptor_sort_key(payload: Mapping[str, object] | None) -> tuple:
    item = canonicalize_component_descriptor(payload)
    extensions = _as_map(item.get("extensions"))
    return (
        _token(item.get("component_id")),
        _semver_key(item.get("version")),
        _token(extensions.get("build_id")),
        _descriptor_artifact_id(item),
        _token(item.get("content_hash")).lower(),
    )


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _platform_matrix_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "os": _token(item.get("os")),
        "arch": _token(item.get("arch")),
        "abi": _token(item.get("abi")),
        "artifact_url_or_path": _norm_rel(item.get("artifact_url_or_path")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _signature_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "signature_id": _token(item.get("signature_id")),
        "signer_id": _token(item.get("signer_id")),
        "signed_hash": _token(item.get("signed_hash")).lower(),
        "signature_bytes": _token(item.get("signature_bytes")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _update_component_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "component_id": _token(item.get("component_id")),
        "component_kind": _token(item.get("component_kind")),
        "from_content_hash": _token(item.get("from_content_hash")).lower(),
        "to_content_hash": _token(item.get("to_content_hash")).lower(),
        "from_version": _token(item.get("from_version")),
        "to_version": _token(item.get("to_version")),
        "build_id": _token(item.get("build_id")),
        "reason": _token(item.get("reason")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _verification_step_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "step_id": _token(item.get("step_id")),
        "action": _token(item.get("action")),
        "component_id": _token(item.get("component_id")),
        "artifact_ref": _norm_rel(item.get("artifact_ref")),
        "reason": _token(item.get("reason")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_release_index(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    protocol_ranges = merge_protocol_ranges(_as_map(item.get("supported_protocol_ranges")).values())
    components = sorted(
        (
            canonicalize_component_descriptor(row)
            for row in _as_list(item.get("components"))
            if _token(_as_map(row).get("component_id"))
        ),
        key=_component_descriptor_sort_key,
    )
    platform_matrix = sorted(
        (
            _platform_matrix_row(row)
            for row in _as_list(item.get("platform_matrix"))
            if _token(_as_map(row).get("os")) and _token(_as_map(row).get("arch")) and _token(_as_map(row).get("abi"))
        ),
        key=lambda row: (
            _token(row.get("os")),
            _token(row.get("arch")),
            _token(row.get("abi")),
            _norm_rel(row.get("artifact_url_or_path")),
        ),
    )
    signatures = sorted(
        (
            _signature_row(row)
            for row in _as_list(item.get("signatures"))
            if _token(_as_map(row).get("signer_id")) and _token(_as_map(row).get("signed_hash"))
        ),
        key=lambda row: (
            _token(row.get("signed_hash")),
            _token(row.get("signer_id")),
            _token(row.get("signature_id")),
        ),
    )
    normalized = {
        "channel": _token(item.get("channel")),
        "release_series": _token(item.get("release_series")) or DEFAULT_RELEASE_SERIES,
        "semantic_contract_registry_hash": _token(item.get("semantic_contract_registry_hash")).lower(),
        "governance_profile_hash": _token(item.get("governance_profile_hash")).lower(),
        "supported_protocol_ranges": dict((key, protocol_ranges[key]) for key in sorted(protocol_ranges.keys())),
        "platform_matrix": platform_matrix,
        "component_graph_hash": _token(item.get("component_graph_hash")).lower(),
        "components": components,
        "signatures": signatures,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    if _as_map(item.get(UNIVERSAL_IDENTITY_FIELD)):
        normalized[UNIVERSAL_IDENTITY_FIELD] = canonicalize_universal_identity_block(item.get(UNIVERSAL_IDENTITY_FIELD))
    fingerprint_seed = dict(normalized)
    fingerprint_seed.pop(UNIVERSAL_IDENTITY_FIELD, None)
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(fingerprint_seed)
    return normalized


def _release_index_signing_payload(payload: Mapping[str, object] | None) -> dict:
    normalized = canonicalize_release_index(payload)
    out = dict(normalized)
    out.pop("signatures", None)
    out["deterministic_fingerprint"] = ""
    return out


def canonicalize_update_plan(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    add_rows = sorted(
        (
            _update_component_row(row)
            for row in _as_list(item.get("components_to_add"))
            if _token(_as_map(row).get("component_id"))
        ),
        key=lambda row: (_token(row.get("component_id")), _token(row.get("reason"))),
    )
    remove_rows = sorted(
        (
            _update_component_row(row)
            for row in _as_list(item.get("components_to_remove"))
            if _token(_as_map(row).get("component_id"))
        ),
        key=lambda row: (_token(row.get("component_id")), _token(row.get("reason"))),
    )
    upgrade_rows = sorted(
        (
            _update_component_row(row)
            for row in _as_list(item.get("components_to_upgrade"))
            if _token(_as_map(row).get("component_id"))
        ),
        key=lambda row: (_token(row.get("component_id")), _token(row.get("to_content_hash")), _token(row.get("reason"))),
    )
    verification_rows = sorted(
        (
            _verification_step_row(row)
            for row in _as_list(item.get("verification_steps"))
            if _token(_as_map(row).get("step_id"))
        ),
        key=lambda row: (_token(row.get("step_id")), _token(row.get("component_id")), _token(row.get("action"))),
    )
    normalized = {
        "plan_id": _token(item.get("plan_id")),
        "from_release_id": _token(item.get("from_release_id")),
        "to_release_id": _token(item.get("to_release_id")),
        "target_platform": _token(item.get("target_platform")),
        "install_profile_id": _token(item.get("install_profile_id")),
        "resolution_policy_id": _canonical_release_resolution_policy_id(item.get("resolution_policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
        "components_to_add": add_rows,
        "components_to_remove": remove_rows,
        "components_to_upgrade": upgrade_rows,
        "verification_steps": verification_rows,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def load_release_index(path: str) -> dict:
    return canonicalize_release_index(_read_json(path))


def write_release_index(path: str, payload: Mapping[str, object]) -> str:
    return _write_json(path, canonicalize_release_index(payload))


def infer_release_index_path(install_root: str, explicit_path: str = "") -> str:
    explicit = _token(explicit_path)
    if explicit:
        return _norm(explicit)
    root = _norm(install_root)
    return os.path.join(root, DEFAULT_RELEASE_INDEX_REL)


def release_index_hash(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(canonicalize_release_index(payload))


def release_index_signed_hash(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(_release_index_signing_payload(payload))


def component_managed_paths(component_descriptor: Mapping[str, object] | None) -> list[str]:
    descriptor = canonicalize_component_descriptor(component_descriptor)
    extensions = _as_map(descriptor.get("extensions"))
    managed = _sorted_unique_strings(extensions.get("managed_paths"))
    if managed:
        return managed
    component_id = _token(descriptor.get("component_id"))
    component_kind = _token(descriptor.get("component_kind"))
    if component_kind == COMPONENT_KIND_BINARY:
        product_id = _token(extensions.get("product_id")) or component_id.replace("binary.", "", 1)
        rows = [
            "bin/{}".format(product_id),
            "bin/{}.cmd".format(product_id),
            "bin/{}.descriptor.json".format(product_id),
        ]
        return sorted({row for row in rows if row})
    if component_kind == COMPONENT_KIND_PACK:
        rel_token = _norm_rel(extensions.get("distribution_rel"))
        if rel_token:
            if rel_token.startswith("store/") or rel_token.startswith("packs/"):
                return [rel_token]
            return ["store/{}".format(rel_token)]
    if component_kind == COMPONENT_KIND_PROFILE and component_id == "profile.bundle.mvp_default":
        return ["store/profiles/bundles/bundle.mvp_default.json"]
    if component_kind == COMPONENT_KIND_LOCK and component_id == "lock.pack_lock.mvp_default":
        return ["store/locks/pack_lock.mvp_default.json"]
    if component_kind == COMPONENT_KIND_DOCS:
        rel_token = _norm_rel(extensions.get("doc_rel"))
        if rel_token:
            return [rel_token]
    if component_kind == COMPONENT_KIND_MANIFEST:
        manifest_map = {
            "manifest.release_manifest": "manifests/release_manifest.json",
            "manifest.instance.default": "instances/default/instance.manifest.json",
        }
        if component_id in manifest_map:
            return [manifest_map[component_id]]
    return []


def resolve_release_index_platform_entry(
    release_index: Mapping[str, object] | None,
    *,
    target_platform: str = "",
    target_arch: str = "",
    target_abi: str = "",
) -> dict:
    index = canonicalize_release_index(release_index)
    rows = list(index.get("platform_matrix") or [])
    platform_token = _token(target_platform)
    arch_token = _token(target_arch)
    abi_token = _token(target_abi)
    if not any((platform_token, arch_token, abi_token)):
        return dict(rows[0]) if rows else {}
    matches = []
    for row in rows:
        item = _platform_matrix_row(row)
        extensions = _as_map(item.get("extensions"))
        platform_candidates = {
            _token(item.get("os")),
            _token(extensions.get("platform_id")),
            _token(extensions.get("platform_tag")),
        }
        if platform_token and platform_token not in platform_candidates:
            continue
        if arch_token and arch_token != _token(item.get("arch")):
            continue
        if abi_token and abi_token != _token(item.get("abi")):
            continue
        matches.append(item)
    return dict(matches[0]) if matches else {}


def resolve_release_artifact_root(release_index_path: str, platform_entry: Mapping[str, object] | None) -> str:
    index_dir = os.path.dirname(_norm(release_index_path))
    artifact_rel = _norm_rel(_as_map(platform_entry).get("artifact_url_or_path"))
    if not artifact_rel:
        return os.path.dirname(index_dir)
    return _norm(os.path.join(index_dir, artifact_rel.replace("/", os.sep)))


def load_install_transaction_log(path: str) -> dict:
    payload = _read_json(path)
    rows = []
    for row in _as_list(_as_map(payload).get("transactions")):
        item = _as_map(row)
        rows.append(
            {
                "transaction_id": _token(item.get("transaction_id")),
                "action": _token(item.get("action")),
                "from_release_id": _token(item.get("from_release_id")),
                "to_release_id": _token(item.get("to_release_id")),
                "status": _token(item.get("status")),
                "backup_path": _norm_rel(item.get("backup_path")),
                "install_profile_id": _token(item.get("install_profile_id")),
                "resolution_policy_id": _canonical_release_resolution_policy_id(item.get("resolution_policy_id")),
                "install_plan_hash": _token(item.get("install_plan_hash")).lower(),
                "prior_component_set_hash": _token(item.get("prior_component_set_hash")).lower(),
                "selected_component_ids": _sorted_unique_strings(item.get("selected_component_ids")),
                "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
                "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
            }
        )
    normalized = {
        "transactions": rows,
        "deterministic_fingerprint": _token(payload.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(payload.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def append_install_transaction(path: str, entry: Mapping[str, object]) -> dict:
    payload = load_install_transaction_log(path)
    row = {
        "transaction_id": _token(_as_map(entry).get("transaction_id")),
        "action": _token(_as_map(entry).get("action")),
        "from_release_id": _token(_as_map(entry).get("from_release_id")),
        "to_release_id": _token(_as_map(entry).get("to_release_id")),
        "status": _token(_as_map(entry).get("status")) or "complete",
        "backup_path": _norm_rel(_as_map(entry).get("backup_path")),
        "install_profile_id": _token(_as_map(entry).get("install_profile_id")),
        "resolution_policy_id": _canonical_release_resolution_policy_id(_as_map(entry).get("resolution_policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
        "install_plan_hash": _token(_as_map(entry).get("install_plan_hash")).lower(),
        "prior_component_set_hash": _token(_as_map(entry).get("prior_component_set_hash")).lower(),
        "selected_component_ids": _sorted_unique_strings(_as_map(entry).get("selected_component_ids")),
        "deterministic_fingerprint": "",
        "extensions": dict(_normalize_tree(_as_map(_as_map(entry).get("extensions")))),
    }
    row["deterministic_fingerprint"] = deterministic_fingerprint(row)
    payload.setdefault("transactions", [])
    payload["transactions"] = list(payload.get("transactions") or []) + [row]
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    _write_json(path, payload)
    return payload


def select_rollback_transaction(path: str, *, to_release_id: str = "") -> dict:
    payload = load_install_transaction_log(path)
    transactions = list(payload.get("transactions") or [])
    target_release_id = _token(to_release_id)
    if target_release_id:
        for row in reversed(transactions):
            item = _as_map(row)
            if _token(item.get("status")) != "complete":
                continue
            if _token(item.get("from_release_id")) == target_release_id:
                return dict(item)
        return {}
    for row in reversed(transactions):
        item = _as_map(row)
        if _token(item.get("status")) == "complete":
            return dict(item)
    return {}


def _normalize_current_component_rows(install_manifest: Mapping[str, object] | None) -> list[dict]:
    manifest = normalize_install_manifest(_as_map(install_manifest))
    extensions = _as_map(manifest.get("extensions"))
    rows = list(extensions.get("official.selected_component_descriptors") or [])
    normalized = [
        canonicalize_component_descriptor(row)
        for row in rows
        if _token(_as_map(row).get("component_id"))
    ]
    if normalized:
        return sorted(normalized, key=lambda row: _token(row.get("component_id")))
    descriptors = []
    for product_id, row in sorted(_as_map(manifest.get("product_build_descriptors")).items()):
        item = _as_map(row)
        descriptors.append(
            canonicalize_component_descriptor(
                {
                    "component_id": "binary.{}".format(_token(product_id)),
                    "component_kind": COMPONENT_KIND_BINARY,
                    "content_hash": _token(item.get("binary_hash")).lower(),
                    "version": _token(_as_map(item.get("extensions")).get("official.product_version")),
                    "extensions": {
                        "product_id": _token(product_id),
                        "managed_paths": component_managed_paths(
                            {
                                "component_id": "binary.{}".format(_token(product_id)),
                                "component_kind": COMPONENT_KIND_BINARY,
                                "extensions": {"product_id": _token(product_id)},
                            }
                        ),
                    },
                }
            )
        )
    return sorted(descriptors, key=lambda row: _token(row.get("component_id")))


def _protocol_overlap(current_row: Mapping[str, object], target_row: Mapping[str, object]) -> bool:
    current_min = _token(current_row.get("min_version"))
    current_max = _token(current_row.get("max_version"))
    target_min = _token(target_row.get("min_version"))
    target_max = _token(target_row.get("max_version"))
    if not current_min or not current_max or not target_min or not target_max:
        return True
    current_min_tuple = tuple(int(token) for token in current_min.split("."))
    current_max_tuple = tuple(int(token) for token in current_max.split("."))
    target_min_tuple = tuple(int(token) for token in target_min.split("."))
    target_max_tuple = tuple(int(token) for token in target_max.split("."))
    return not (current_max_tuple < target_min_tuple or target_max_tuple < current_min_tuple)


def _descriptor_upgrade_row(current_row: Mapping[str, object], target_row: Mapping[str, object], reason: str) -> dict:
    current_descriptor = canonicalize_component_descriptor(current_row)
    target_descriptor = canonicalize_component_descriptor(target_row)
    return _update_component_row(
        {
            "component_id": _token(target_descriptor.get("component_id")),
            "component_kind": _token(target_descriptor.get("component_kind")),
            "from_content_hash": _token(current_descriptor.get("content_hash")).lower(),
            "to_content_hash": _token(target_descriptor.get("content_hash")).lower(),
            "from_version": _token(current_descriptor.get("version")),
            "to_version": _token(target_descriptor.get("version")),
            "build_id": _token(_as_map(target_descriptor.get("extensions")).get("build_id")),
            "reason": reason,
            "extensions": {"managed_paths": component_managed_paths(target_descriptor)},
        }
    )


def _descriptor_add_row(target_row: Mapping[str, object], reason: str) -> dict:
    target_descriptor = canonicalize_component_descriptor(target_row)
    return _update_component_row(
        {
            "component_id": _token(target_descriptor.get("component_id")),
            "component_kind": _token(target_descriptor.get("component_kind")),
            "from_content_hash": "",
            "to_content_hash": _token(target_descriptor.get("content_hash")).lower(),
            "from_version": "",
            "to_version": _token(target_descriptor.get("version")),
            "build_id": _token(_as_map(target_descriptor.get("extensions")).get("build_id")),
            "reason": reason,
            "extensions": {"managed_paths": component_managed_paths(target_descriptor)},
        }
    )


def _descriptor_remove_row(current_row: Mapping[str, object], reason: str) -> dict:
    current_descriptor = canonicalize_component_descriptor(current_row)
    return _update_component_row(
        {
            "component_id": _token(current_descriptor.get("component_id")),
            "component_kind": _token(current_descriptor.get("component_kind")),
            "from_content_hash": _token(current_descriptor.get("content_hash")).lower(),
            "to_content_hash": "",
            "from_version": _token(current_descriptor.get("version")),
            "to_version": "",
            "reason": reason,
            "extensions": {"managed_paths": component_managed_paths(current_descriptor)},
        }
    )


def _verification_steps(
    *,
    release_index_path: str,
    release_root: str,
    add_rows: Sequence[Mapping[str, object]],
    remove_rows: Sequence[Mapping[str, object]],
    upgrade_rows: Sequence[Mapping[str, object]],
) -> list[dict]:
    rows = [
        {
            "step_id": "verify.release_index",
            "action": "verify_release_index_hash",
            "artifact_ref": _norm_rel(os.path.relpath(_norm(release_index_path), _norm(release_root))),
            "reason": "update_resolution",
        },
        {
            "step_id": "verify.release_manifest",
            "action": "verify_release_manifest",
            "artifact_ref": "manifests/release_manifest.json",
            "reason": "update_resolution",
        },
    ]
    for row in list(add_rows or []):
        item = _as_map(row)
        rows.append(
            {
                "step_id": "verify.component.add.{}".format(_token(item.get("component_id"))),
                "action": "verify_content_hash",
                "component_id": _token(item.get("component_id")),
                "artifact_ref": ",".join(_sorted_unique_strings(_as_map(item.get("extensions")).get("managed_paths"))),
                "reason": "component_add",
            }
        )
    for row in list(upgrade_rows or []):
        item = _as_map(row)
        rows.append(
            {
                "step_id": "verify.component.upgrade.{}".format(_token(item.get("component_id"))),
                "action": "verify_content_hash",
                "component_id": _token(item.get("component_id")),
                "artifact_ref": ",".join(_sorted_unique_strings(_as_map(item.get("extensions")).get("managed_paths"))),
                "reason": "component_upgrade",
            }
        )
    for row in list(remove_rows or []):
        item = _as_map(row)
        rows.append(
            {
                "step_id": "verify.component.remove.{}".format(_token(item.get("component_id"))),
                "action": "verify_removal_policy",
                "component_id": _token(item.get("component_id")),
                "artifact_ref": ",".join(_sorted_unique_strings(_as_map(item.get("extensions")).get("managed_paths"))),
                "reason": "component_remove",
            }
    )
    return [_verification_step_row(row) for row in rows]


def _descriptor_matches_target(
    descriptor: Mapping[str, object] | None,
    *,
    target_platform: str,
    target_arch: str,
    target_abi: str,
) -> bool:
    item = canonicalize_component_descriptor(descriptor)
    filters = _as_map(item.get("platform_filters"))
    platform_token = _token(target_platform)
    arch_token = _token(target_arch)
    abi_token = _token(target_abi)
    allowed_platforms = _sorted_unique_strings(filters.get("platform_ids"))
    excluded_platforms = set(_sorted_unique_strings(filters.get("exclude_platform_ids")))
    allowed_arches = _sorted_unique_strings(filters.get("arch_ids"))
    excluded_arches = set(_sorted_unique_strings(filters.get("exclude_arch_ids")))
    allowed_abis = _sorted_unique_strings(filters.get("abi_ids"))
    excluded_abis = set(_sorted_unique_strings(filters.get("exclude_abi_ids")))
    if allowed_platforms and platform_token not in allowed_platforms:
        return False
    if platform_token and platform_token in excluded_platforms:
        return False
    if allowed_arches and arch_token not in allowed_arches:
        return False
    if arch_token and arch_token in excluded_arches:
        return False
    if allowed_abis and abi_token not in allowed_abis:
        return False
    if abi_token and abi_token in excluded_abis:
        return False
    return True


def _descriptor_matches_trust_policy(descriptor: Mapping[str, object] | None, trust_policy: Mapping[str, object] | None) -> bool:
    if not trust_policy:
        return True
    item = canonicalize_component_descriptor(descriptor)
    required_tier = _token(_as_map(item.get("trust_requirements")).get("min_trust_tier"))
    if not required_tier:
        return True
    return required_tier == _token(_as_map(trust_policy).get("trust_tier"))


def _select_exact_candidate(
    pinned_descriptor: Mapping[str, object] | None,
    candidate_rows: Sequence[Mapping[str, object]],
) -> dict:
    pinned = canonicalize_component_descriptor(pinned_descriptor)
    pinned_hash = _token(pinned.get("content_hash")).lower()
    pinned_version = _token(pinned.get("version"))
    pinned_build_id = _token(_as_map(pinned.get("extensions")).get("build_id"))
    pinned_artifact_id = _descriptor_artifact_id(pinned)
    for row in list(candidate_rows or []):
        candidate = canonicalize_component_descriptor(row)
        if _token(candidate.get("content_hash")).lower() == pinned_hash and pinned_hash:
            return candidate
    for row in list(candidate_rows or []):
        candidate = canonicalize_component_descriptor(row)
        if (
            _token(candidate.get("version")) == pinned_version
            and _token(_as_map(candidate.get("extensions")).get("build_id")) == pinned_build_id
            and _descriptor_artifact_id(candidate) == pinned_artifact_id
        ):
            return candidate
    return pinned


def _candidate_rank_key(descriptor: Mapping[str, object] | None) -> tuple:
    item = canonicalize_component_descriptor(descriptor)
    extensions = _as_map(item.get("extensions"))
    return (
        _semver_key(item.get("version")),
        _token(extensions.get("build_id")),
        _descriptor_artifact_id(item),
        _token(item.get("content_hash")).lower(),
    )


def _selected_component_set_hash(descriptor_rows: Sequence[Mapping[str, object]]) -> str:
    normalized = [
        canonicalize_component_descriptor(row)
        for row in sorted(list(descriptor_rows or []), key=_component_descriptor_sort_key)
    ]
    return canonical_sha256({"selected_component_descriptors": normalized})


def _resolve_release_component_candidates(
    *,
    index: Mapping[str, object],
    base_component_rows: Sequence[Mapping[str, object]],
    target_platform: str,
    target_arch: str,
    target_abi: str,
    trust_policy: Mapping[str, object] | None,
    resolution_policy_id: str,
    resolution_policy: Mapping[str, object] | None,
) -> dict:
    policy_row = canonicalize_release_resolution_policy(
        resolution_policy
        or select_release_resolution_policy({}, policy_id=resolution_policy_id)
        or {"policy_id": resolution_policy_id or DEFAULT_RELEASE_RESOLUTION_POLICY_ID}
    )
    effective_policy_id = _token(policy_row.get("policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID
    allow_yanked = bool(policy_row.get("allow_yanked"))
    candidate_map: dict[str, list[dict]] = {}
    for row in _as_list(_as_map(index).get("components")):
        descriptor = canonicalize_component_descriptor(row)
        component_id = _token(descriptor.get("component_id"))
        if not component_id:
            continue
        if not _descriptor_matches_target(descriptor, target_platform=target_platform, target_arch=target_arch, target_abi=target_abi):
            continue
        if not _descriptor_matches_trust_policy(descriptor, trust_policy):
            continue
        candidate_map.setdefault(component_id, []).append(descriptor)
    for component_id in list(candidate_map.keys()):
        candidate_map[component_id] = sorted(candidate_map[component_id], key=_component_descriptor_sort_key)

    selected_rows: list[dict] = []
    warnings: list[dict] = []
    errors: list[dict] = []
    explain_rows: list[dict] = []
    skipped_yanked_rows: list[dict] = []
    yanked_selected_ids: list[str] = []
    base_rows = [
        canonicalize_component_descriptor(row)
        for row in sorted(list(base_component_rows or []), key=_component_descriptor_sort_key)
        if _token(_as_map(row).get("component_id"))
    ]
    for base_row in base_rows:
        component_id = _token(base_row.get("component_id"))
        candidates = list(candidate_map.get(component_id) or [])
        selected = {}
        if effective_policy_id == RESOLUTION_POLICY_EXACT_SUITE:
            selected = _select_exact_candidate(base_row, candidates)
            explain_rows.append(
                {
                    "event_id": "explain.component_selected",
                    "component_id": component_id,
                    "resolution_policy_id": effective_policy_id,
                    "reason": "exact_suite_pinned_descriptor",
                    "selected_version": _token(_as_map(selected).get("version")),
                    "selected_build_id": _token(_as_map(_as_map(selected).get("extensions")).get("build_id")),
                    "selected_artifact_id": _descriptor_artifact_id(selected),
                }
            )
        else:
            eligible = []
            for candidate in candidates:
                if bool(candidate.get("yanked")) and not allow_yanked:
                    skipped_yanked_rows.append(
                        {
                            "event_id": "explain.component_skipped_yanked",
                            "component_id": component_id,
                            "resolution_policy_id": effective_policy_id,
                            "candidate_version": _token(candidate.get("version")),
                            "candidate_build_id": _token(_as_map(candidate.get("extensions")).get("build_id")),
                            "artifact_id": _descriptor_artifact_id(candidate),
                            "yank_reason": _token(candidate.get("yank_reason")),
                        }
                    )
                    continue
                eligible.append(candidate)
            if not eligible:
                errors.append(
                    {
                        "code": REFUSAL_UPDATE_RELEASE_UNAVAILABLE,
                        "message": "no compatible component candidate is available under the applied resolution policy",
                        "component_id": component_id,
                        "resolution_policy_id": effective_policy_id,
                    }
                )
                continue
            selected = sorted(eligible, key=_candidate_rank_key, reverse=True)[0]
            explain_rows.append(
                {
                    "event_id": "explain.component_selected",
                    "component_id": component_id,
                    "resolution_policy_id": effective_policy_id,
                    "reason": "highest_compatible_candidate",
                    "selected_version": _token(_as_map(selected).get("version")),
                    "selected_build_id": _token(_as_map(_as_map(selected).get("extensions")).get("build_id")),
                    "selected_artifact_id": _descriptor_artifact_id(selected),
                }
            )
        if not selected:
            continue
        if bool(_as_map(selected).get("yanked")):
            yanked_selected_ids.append(component_id)
            yank_policy = _token(_as_map(selected).get("yank_policy")).lower() or YANK_POLICY_WARN
            yanked_row = {
                "code": REFUSAL_UPDATE_YANKED_COMPONENT if yank_policy == YANK_POLICY_REFUSE else "warn.update.yanked_component",
                "message": _token(_as_map(selected).get("yank_reason")) or "selected component candidate is yanked",
                "component_id": component_id,
                "resolution_policy_id": effective_policy_id,
            }
            if yank_policy == YANK_POLICY_REFUSE:
                errors.append(yanked_row)
            else:
                warnings.append(yanked_row)
        selected_rows.append(dict(selected))

    explain_rows.append(
        {
            "event_id": "explain.policy_applied",
            "resolution_policy_id": effective_policy_id,
            "selection_rule_id": _token(policy_row.get("selection_rule_id")),
            "allow_yanked": bool(policy_row.get("allow_yanked")),
            "selected_component_count": int(len(selected_rows)),
        }
    )
    explain_rows.extend(skipped_yanked_rows)
    explain_rows = sorted(
        explain_rows,
        key=lambda row: (
            _token(_as_map(row).get("event_id")),
            _token(_as_map(row).get("component_id")),
            _token(_as_map(row).get("candidate_version")),
            _token(_as_map(row).get("selected_version")),
            _token(_as_map(row).get("selected_artifact_id")) or _token(_as_map(row).get("artifact_id")),
        ),
    )
    return {
        "resolution_policy": dict(policy_row),
        "selected_component_descriptors": sorted(selected_rows, key=_component_descriptor_sort_key),
        "warnings": warnings,
        "errors": errors,
        "explain_rows": explain_rows,
        "selected_yanked_component_ids": sorted(set(yanked_selected_ids)),
        "skipped_yanked_rows": skipped_yanked_rows,
    }


def resolve_update_plan(
    current_install_manifest: Mapping[str, object] | None,
    release_index: Mapping[str, object] | None,
    *,
    install_profile_id: str = "",
    install_profile: Mapping[str, object] | None = None,
    resolution_policy_id: str = "",
    resolution_policy: Mapping[str, object] | None = None,
    target_platform: str = "",
    target_arch: str = "",
    target_abi: str = "",
    component_graph: Mapping[str, object] | None = None,
    trust_policy: Mapping[str, object] | None = None,
    trust_policy_id: str = "",
    trust_roots: Sequence[Mapping[str, object]] | None = None,
    install_root: str = "",
    release_index_path: str = "",
) -> dict:
    current_manifest = normalize_install_manifest(_as_map(current_install_manifest))
    index = canonicalize_release_index(release_index)
    errors: list[dict] = []
    warnings: list[dict] = []
    if not index:
        errors.append({"code": REFUSAL_RELEASE_INDEX_MISSING, "message": "release index is missing or invalid"})
        plan = canonicalize_update_plan(
            {
                "plan_id": "update_plan.missing",
                "from_release_id": "",
                "to_release_id": "",
                "target_platform": _token(target_platform),
                "install_profile_id": _token(install_profile_id),
                "components_to_add": [],
                "components_to_remove": [],
                "components_to_upgrade": [],
                "verification_steps": [],
                "extensions": {},
            }
        )
        return {"result": "refused", "refusal_code": REFUSAL_RELEASE_INDEX_MISSING, "errors": errors, "update_plan": plan}

    effective_trust_policy_id = _token(trust_policy_id) or _token(_as_map(trust_policy).get("trust_policy_id"))
    trust_result = {}
    if trust_policy:
        trust_result = verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
            content_hash=release_index_signed_hash(index),
            signatures=_as_list(index.get("signatures")),
            trust_policy=_as_map(trust_policy),
            trust_policy_id=effective_trust_policy_id,
            trust_roots=trust_roots,
        )
        for row in _as_list(trust_result.get("warnings")):
            item = _as_map(row)
            warnings.append(
                {
                    "code": _token(item.get("code")),
                    "message": _token(item.get("message")) or "release index trust verification emitted a warning",
                }
            )
        if _token(trust_result.get("result")) == "refused":
            errors.append(
                {
                    "code": _token(trust_result.get("refusal_code")) or REFUSAL_UPDATE_TRUST_UNMET,
                    "message": _token(trust_result.get("reason")) or "release index trust verification failed",
                }
            )

    current_contract_hash = _token(current_manifest.get("semantic_contract_registry_hash")).lower()
    target_contract_hash = _token(index.get("semantic_contract_registry_hash")).lower()
    if current_contract_hash and target_contract_hash and current_contract_hash != target_contract_hash:
        errors.append(
            {
                "code": REFUSAL_UPDATE_CONTRACT_INCOMPATIBLE,
                "message": "semantic contract registry hash does not match the target release",
                "current_semantic_contract_registry_hash": current_contract_hash,
                "target_semantic_contract_registry_hash": target_contract_hash,
            }
        )

    platform_entry = resolve_release_index_platform_entry(
        index,
        target_platform=target_platform,
        target_arch=target_arch,
        target_abi=target_abi,
    )
    if not platform_entry:
        errors.append(
            {
                "code": REFUSAL_UPDATE_PLATFORM_UNAVAILABLE,
                "message": "target platform is not present in the release index",
                "target_platform": _token(target_platform),
                "target_arch": _token(target_arch),
                "target_abi": _token(target_abi),
            }
        )
    platform_extensions = _as_map(_as_map(platform_entry).get("extensions"))
    effective_platform = _token(target_platform) or _token(platform_extensions.get("platform_id")) or _token(_as_map(platform_entry).get("os"))
    effective_arch = _token(target_arch) or _token(_as_map(platform_entry).get("arch"))
    effective_abi = _token(target_abi) or _token(_as_map(platform_entry).get("abi"))

    current_protocols = merge_protocol_ranges(_as_map(current_manifest.get("supported_protocol_versions")).values())
    target_protocols = merge_protocol_ranges(_as_map(index.get("supported_protocol_ranges")).values())
    for protocol_id, target_row in sorted(target_protocols.items()):
        current_row = _as_map(current_protocols.get(protocol_id))
        if current_row and _protocol_overlap(current_row, _as_map(target_row)):
            continue
        if current_row:
            errors.append(
                {
                    "code": REFUSAL_UPDATE_PROTOCOL_INCOMPATIBLE,
                    "message": "supported protocol range does not overlap the target release",
                    "protocol_id": protocol_id,
                }
            )

    embedded_graph = canonicalize_component_graph(_as_map(_as_map(index.get("extensions")).get("component_graph")))
    effective_graph = canonicalize_component_graph(component_graph or embedded_graph)
    if not _token(effective_graph.get("graph_id")):
        errors.append(
            {
                "code": REFUSAL_UPDATE_COMPONENT_GRAPH_MISSING,
                "message": "release index does not provide a component graph payload",
            }
        )

    effective_profile = dict(install_profile or {})
    if not effective_profile:
        manifest_extensions = _as_map(current_manifest.get("extensions"))
        resolved_profile_id = _token(install_profile_id) or _token(manifest_extensions.get("official.install_profile_id"))
        if resolved_profile_id:
            effective_profile = {
                "install_profile_id": resolved_profile_id,
                "required_selectors": [],
                "optional_selectors": [],
                "default_mod_policy_id": _token(current_manifest.get("default_mod_policy_id")) or "mod.policy.default",
                "default_overlay_conflict_policy_id": "overlay.conflict.default",
                "extensions": {},
            }
    if not _token(effective_profile.get("install_profile_id")):
        errors.append(
            {
                "code": REFUSAL_UPDATE_INSTALL_PROFILE_MISSING,
                "message": "install profile is required for update resolution",
            }
        )
    effective_resolution_policy = canonicalize_release_resolution_policy(
        resolution_policy
        or select_release_resolution_policy({}, policy_id=resolution_policy_id)
        or {"policy_id": resolution_policy_id or DEFAULT_RELEASE_RESOLUTION_POLICY_ID}
    )
    effective_resolution_policy_id = _token(effective_resolution_policy.get("policy_id")) or DEFAULT_RELEASE_RESOLUTION_POLICY_ID

    target_resolution = resolve_component_graph(
        effective_graph,
        install_profile_id=_token(effective_profile.get("install_profile_id")) or _token(install_profile_id),
        install_profile=effective_profile,
        target_platform=effective_platform,
        target_arch=effective_arch,
        target_abi=effective_abi,
    ) if _token(effective_graph.get("graph_id")) and _token(effective_profile.get("install_profile_id")) else {
        "result": "refused",
        "errors": [],
        "install_plan": canonicalize_install_plan(
            {
                "plan_id": "install_plan.missing",
                "target_platform": effective_platform,
                "target_arch": effective_arch,
                "install_profile_id": _token(effective_profile.get("install_profile_id")),
                "selected_components": [],
                "resolved_providers": [],
                "verification_steps": [],
                "extensions": {},
            }
        ),
        "selected_component_descriptors": [],
    }
    if _token(target_resolution.get("result")) != "complete":
        for row in list(target_resolution.get("errors") or []):
            item = _as_map(row)
            errors.append(
                {
                    "code": _token(item.get("code")) or REFUSAL_UPDATE_RELEASE_UNAVAILABLE,
                    "message": _token(item.get("message")) or "target release component graph resolution failed",
                }
            )

    selection_result = _resolve_release_component_candidates(
        index=index,
        base_component_rows=list(target_resolution.get("selected_component_descriptors") or []),
        target_platform=effective_platform,
        target_arch=effective_arch,
        target_abi=effective_abi,
        trust_policy=trust_policy,
        resolution_policy_id=effective_resolution_policy_id,
        resolution_policy=effective_resolution_policy,
    )
    warnings.extend(list(selection_result.get("warnings") or []))
    errors.extend(list(selection_result.get("errors") or []))
    target_descriptor_rows = {
        _token(_as_map(row).get("component_id")): canonicalize_component_descriptor(row)
        for row in list(selection_result.get("selected_component_descriptors") or [])
        if _token(_as_map(row).get("component_id"))
    }
    current_descriptor_rows = {
        _token(_as_map(row).get("component_id")): canonicalize_component_descriptor(row)
        for row in _normalize_current_component_rows(current_manifest)
        if _token(_as_map(row).get("component_id"))
    }

    if trust_policy:
        trust_token = _token(_as_map(trust_policy).get("trust_tier"))
        for component_id, descriptor in sorted(target_descriptor_rows.items()):
            required_tier = _token(_as_map(descriptor.get("trust_requirements")).get("min_trust_tier"))
            if required_tier and required_tier != trust_token:
                errors.append(
                    {
                        "code": REFUSAL_UPDATE_TRUST_UNMET,
                        "message": "trust policy does not satisfy component trust requirements",
                        "component_id": component_id,
                    }
                )

    add_rows = []
    remove_rows = []
    upgrade_rows = []
    current_ids = sorted(current_descriptor_rows.keys())
    target_ids = sorted(target_descriptor_rows.keys())
    for component_id in target_ids:
        target_row = target_descriptor_rows[component_id]
        current_row = current_descriptor_rows.get(component_id)
        if not current_row:
            add_rows.append(_descriptor_add_row(target_row, "component_missing_from_current_install"))
            continue
        changed = False
        if _token(current_row.get("content_hash")).lower() != _token(target_row.get("content_hash")).lower():
            changed = True
        if _token(current_row.get("version")) != _token(target_row.get("version")):
            changed = True
        if _token(_as_map(current_row.get("extensions")).get("build_id")) != _token(_as_map(target_row.get("extensions")).get("build_id")):
            changed = True
        if changed:
            upgrade_rows.append(_descriptor_upgrade_row(current_row, target_row, "content_or_version_changed"))
    for component_id in current_ids:
        if component_id not in target_descriptor_rows:
            remove_rows.append(_descriptor_remove_row(current_descriptor_rows[component_id], "not_selected_by_target_profile"))

    release_root = resolve_release_artifact_root(release_index_path or DEFAULT_RELEASE_INDEX_REL, platform_entry)
    verification_rows = _verification_steps(
        release_index_path=release_index_path or DEFAULT_RELEASE_INDEX_REL,
        release_root=release_root,
        add_rows=add_rows,
        remove_rows=remove_rows,
        upgrade_rows=upgrade_rows,
    )

    current_release_id = _token(_as_map(current_manifest.get("extensions")).get("official.release_id"))
    target_release_id = _token(_as_map(index.get("extensions")).get("release_id"))
    install_plan = dict(target_resolution.get("install_plan") or {})
    plan = canonicalize_update_plan(
        {
            "plan_id": "update_plan.{}".format(
                canonical_sha256(
                    {
                        "from_release_id": current_release_id,
                        "to_release_id": target_release_id,
                        "target_platform": effective_platform,
                        "install_profile_id": _token(effective_profile.get("install_profile_id")),
                        "resolution_policy_id": effective_resolution_policy_id,
                        "components_to_add": add_rows,
                        "components_to_remove": remove_rows,
                        "components_to_upgrade": upgrade_rows,
                    }
                )[:16]
            ),
            "from_release_id": current_release_id,
            "to_release_id": target_release_id,
            "target_platform": effective_platform or _token(platform_extensions.get("platform_tag")) or _token(_as_map(platform_entry).get("os")),
            "install_profile_id": _token(effective_profile.get("install_profile_id")),
            "resolution_policy_id": effective_resolution_policy_id,
            "components_to_add": add_rows,
            "components_to_remove": remove_rows,
            "components_to_upgrade": upgrade_rows,
            "verification_steps": verification_rows,
            "extensions": {
                "target_arch": effective_arch,
                "target_abi": effective_abi,
                "release_index_hash": release_index_hash(index),
                "release_index_path": _norm_rel(release_index_path),
                "release_root": _norm_rel(release_root),
                "platform_entry": dict(platform_entry),
                "current_selected_component_ids": sorted(current_descriptor_rows.keys()),
                "target_selected_component_ids": sorted(target_descriptor_rows.keys()),
                "current_selected_component_descriptors": [current_descriptor_rows[key] for key in sorted(current_descriptor_rows.keys())],
                "target_selected_component_descriptors": [target_descriptor_rows[key] for key in sorted(target_descriptor_rows.keys())],
                "resolution_policy": dict(effective_resolution_policy),
                "policy_explanations": list(selection_result.get("explain_rows") or []),
                "selected_yanked_component_ids": list(selection_result.get("selected_yanked_component_ids") or []),
                "skipped_yanked_candidates": list(selection_result.get("skipped_yanked_rows") or []),
                "prior_component_set_hash": _selected_component_set_hash([current_descriptor_rows[key] for key in sorted(current_descriptor_rows.keys())]),
                "target_component_set_hash": _selected_component_set_hash([target_descriptor_rows[key] for key in sorted(target_descriptor_rows.keys())]),
                "component_graph_hash": _token(index.get("component_graph_hash")).lower(),
                "component_graph_id": _token(effective_graph.get("graph_id")),
                "trust_policy_id": effective_trust_policy_id,
                "trust_result": dict(trust_result),
                "install_root": _norm_rel(install_root),
                "selection_reasons": list(_as_map(install_plan.get("extensions")).get("selection_reasons") or []),
                "disabled_optional_components": list(_as_map(install_plan.get("extensions")).get("disabled_optional_components") or []),
                "update_required": bool(add_rows or remove_rows or upgrade_rows),
            },
        }
    )
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": _token(_as_map(errors[0]).get("code")) if errors else "",
        "errors": errors,
        "warnings": warnings,
        "release_index": index,
        "platform_entry": dict(platform_entry),
        "update_plan": plan,
        "install_plan": install_plan,
        "selected_component_descriptors": [target_descriptor_rows[key] for key in sorted(target_descriptor_rows.keys())],
        "resolution_policy": dict(effective_resolution_policy),
    }


__all__ = [
    "DEFAULT_RELEASE_RESOLUTION_POLICY_ID",
    "DEFAULT_RELEASE_RESOLUTION_POLICY_REGISTRY_REL",
    "DEFAULT_INSTALL_TRANSACTION_LOG_REL",
    "DEFAULT_RELEASE_INDEX_REL",
    "DEFAULT_RELEASE_SERIES",
    "REFUSAL_RELEASE_INDEX_MISSING",
    "REFUSAL_UPDATE_COMPONENT_GRAPH_MISSING",
    "REFUSAL_UPDATE_CONTRACT_INCOMPATIBLE",
    "REFUSAL_UPDATE_INSTALL_PROFILE_MISSING",
    "REFUSAL_UPDATE_PLATFORM_UNAVAILABLE",
    "REFUSAL_UPDATE_PROTOCOL_INCOMPATIBLE",
    "REFUSAL_UPDATE_RELEASE_UNAVAILABLE",
    "REFUSAL_UPDATE_TRUST_UNMET",
    "REFUSAL_UPDATE_YANKED_COMPONENT",
    "RESOLUTION_POLICY_EXACT_SUITE",
    "RESOLUTION_POLICY_LAB",
    "RESOLUTION_POLICY_LATEST_COMPATIBLE",
    "append_install_transaction",
    "canonicalize_release_resolution_policy",
    "canonicalize_release_index",
    "canonicalize_update_plan",
    "component_managed_paths",
    "infer_release_index_path",
    "load_release_resolution_policy_registry",
    "load_install_transaction_log",
    "load_release_index",
    "release_index_hash",
    "release_index_signed_hash",
    "resolve_release_artifact_root",
    "resolve_release_index_platform_entry",
    "resolve_update_plan",
    "select_release_resolution_policy",
    "select_rollback_transaction",
    "write_release_index",
]
