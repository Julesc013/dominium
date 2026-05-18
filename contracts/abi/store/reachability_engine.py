"""Deterministic store reachability helpers for STORE-GC-0."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Mapping, Sequence

from lib.bundle.bundle_manifest import normalize_bundle_manifest
from lib.install.install_discovery_engine import load_runtime_install_registry
from lib.install.install_validator import default_install_registry_path, normalize_install_manifest
from lib.instance.instance_validator import normalize_instance_manifest
from lib.save.save_validator import normalize_save_manifest
from release.release_manifest_engine import load_release_manifest
from release.update_resolver import load_release_index
from tools.xstack.compatx.canonical_json import canonical_sha256


STORE_ROOT_MANIFEST = "store.root.json"
STORE_LAYOUT_DIRNAME = "store"
ARTIFACT_MANIFEST_NAME = "artifact.manifest.json"
ARTIFACT_JSON_PAYLOAD = "payload.json"
ARTIFACT_TREE_PAYLOAD = "payload"
QUARANTINE_DIRNAME = "quarantine"
STORE_CATEGORY_IDS = (
    "blueprints",
    "locks",
    "logic_programs",
    "migrations",
    "packs",
    "process_definitions",
    "profiles",
    "repro",
    "resource_pack_stubs",
    "system_templates",
    "view_presets",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _layout_path(root_location: object, *parts: object) -> str:
    base = Path(_norm(root_location))
    for part in parts:
        token = _token(part)
        if token:
            base = base / token
    return _norm(str(base))


def _rel_from(path: object, root: object) -> str:
    target = _norm(path)
    base = _norm(root)
    try:
        rel_path = os.path.relpath(target, base)
    except ValueError:
        return os.path.basename(target)
    token = _norm_rel(rel_path)
    if token == ".":
        return ""
    return token


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(_norm(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_entries(path: str) -> list[dict]:
    root = _norm(path)
    rows: list[dict] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            abs_path = os.path.join(current_root, name)
            rel_path = _norm_rel(os.path.relpath(abs_path, root))
            rows.append(
                {
                    "path": rel_path,
                    "sha256": _sha256_file(abs_path),
                    "size_bytes": int(os.path.getsize(abs_path)),
                }
            )
    return rows


def _tree_artifact_hash(path: str) -> str:
    return canonical_sha256({"entries": _tree_entries(path)})


def _json_artifact_hash(path: str) -> str:
    payload = _read_json(path)
    return canonical_sha256(payload) if payload else ""


def _is_sha256_token(value: object) -> bool:
    token = _token(value).lower()
    return len(token) == 64 and all(ch in "0123456789abcdef" for ch in token)


def store_artifact_token(category: str, artifact_hash: str) -> str:
    return "{}/{}".format(_token(category).lower(), _token(artifact_hash).lower())


def parse_artifact_token(token: object) -> tuple[str, str]:
    value = _token(token)
    if "/" not in value:
        return "", ""
    category, artifact_hash = value.split("/", 1)
    return _token(category).lower(), _token(artifact_hash).lower()


def _artifact_root(store_root: str, category: str, artifact_hash: str) -> str:
    return _layout_path(store_root, STORE_LAYOUT_DIRNAME, _token(category).lower(), _token(artifact_hash).lower())


def _artifact_root_exists(store_root: str, category: str, artifact_hash: str) -> bool:
    return os.path.isdir(_artifact_root(store_root, category, artifact_hash))


def scan_store_artifacts(store_root: str) -> list[dict]:
    root = _norm(store_root)
    rows: list[dict] = []
    for category in STORE_CATEGORY_IDS:
        category_root = os.path.join(root, STORE_LAYOUT_DIRNAME, category)
        if not os.path.isdir(category_root):
            continue
        for name in sorted(os.listdir(category_root)):
            abs_path = os.path.join(category_root, name)
            if not os.path.isdir(abs_path):
                continue
            rows.append(
                {
                    "category": category,
                    "artifact_hash": _token(name).lower(),
                    "artifact_root": _norm_rel(abs_path),
                    "artifact_token": store_artifact_token(category, name),
                    "is_hash_directory": _is_sha256_token(name),
                }
            )
    return sorted(rows, key=lambda row: (_token(row.get("category")), _token(row.get("artifact_hash"))))


def _quarantined_tokens(store_root: str) -> list[str]:
    root = _layout_path(store_root)
    rows: list[str] = []
    quarantine_root = _layout_path(root, STORE_LAYOUT_DIRNAME, QUARANTINE_DIRNAME)
    for category in STORE_CATEGORY_IDS:
        category_root = _layout_path(quarantine_root, category)
        if not os.path.isdir(category_root):
            continue
        for name in sorted(os.listdir(category_root)):
            abs_path = _layout_path(category_root, name)
            if not os.path.isdir(abs_path):
                continue
            rows.append(store_artifact_token(category, name))
    return sorted(rows)


def _resolve_locator(base_root: str, locator: object) -> str:
    row = _as_map(locator)
    manifest_ref = _token(row.get("manifest_ref"))
    root_path = _token(row.get("root_path"))
    if manifest_ref:
        manifest_abs = manifest_ref if os.path.isabs(manifest_ref) else os.path.join(_norm(base_root), manifest_ref.replace("/", os.sep))
        return os.path.dirname(_norm(manifest_abs))
    if root_path:
        return _norm(root_path if os.path.isabs(root_path) else os.path.join(_norm(base_root), root_path.replace("/", os.sep)))
    return ""


def _store_root_from_install_manifest_path(manifest_path: str) -> str:
    manifest = normalize_install_manifest(_read_json(manifest_path))
    manifest_dir = os.path.dirname(_norm(manifest_path))
    return _resolve_locator(manifest_dir, _as_map(manifest.get("store_root_ref")) or _as_map(manifest.get("store_root")))


def _install_source_row(install_root: str) -> dict:
    manifest_path = os.path.join(_norm(install_root), "install.manifest.json")
    manifest = normalize_install_manifest(_read_json(manifest_path))
    return {
        "install_root": _norm(install_root),
        "install_id": _token(manifest.get("install_id")),
        "install_mode": _token(manifest.get("mode")) or "portable",
        "install_manifest_path": "install.manifest.json",
        "store_root": _store_root_from_install_manifest_path(manifest_path),
        "manifest": manifest,
    }


def _discover_install_sources(repo_root: str, store_root: str, explicit_install_roots: Sequence[str] | None = None, registry_path: str = "") -> list[dict]:
    target_store = _norm(store_root)
    rows: dict[str, dict] = {}
    for install_root in list(explicit_install_roots or []):
        root = _norm(install_root)
        manifest_path = os.path.join(root, "install.manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        item = _install_source_row(root)
        if _norm(item.get("store_root")) != target_store:
            continue
        rows[_norm_rel(manifest_path)] = item

    inferred_install_root = ""
    if os.path.basename(target_store).lower() == STORE_LAYOUT_DIRNAME:
        inferred_install_root = os.path.dirname(target_store)
    manifest_path = _layout_path(inferred_install_root, "install.manifest.json")
    if inferred_install_root and os.path.isfile(manifest_path):
        item = _install_source_row(inferred_install_root)
        if _norm(item.get("store_root")) == target_store:
            rows[_norm_rel(manifest_path)] = item

    registry_token = _token(registry_path) or default_install_registry_path(repo_root)
    runtime_registry = load_runtime_install_registry(registry_token) if registry_token else {}
    for row in _as_list(_as_map(runtime_registry.get("record")).get("installs")):
        install_root = _token(_as_map(row).get("install_root"))
        if not install_root:
            continue
        manifest_path = os.path.join(_norm(install_root), "install.manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        item = _install_source_row(install_root)
        if _norm(item.get("store_root")) != target_store:
            continue
        rows[_norm_rel(manifest_path)] = item

    return sorted(rows.values(), key=lambda row: (_token(row.get("install_id")), _token(row.get("install_manifest_path"))))


def _sorted_manifest_paths(root_path: str, filename: str) -> list[str]:
    root = _norm(root_path)
    rows: list[str] = []
    if not os.path.isdir(root):
        return rows
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        if filename in filenames:
            rows.append(os.path.join(current_root, filename))
    return sorted({_norm(path) for path in rows})


def _artifact_tokens_from_lock_payload(payload: Mapping[str, object] | None) -> list[str]:
    lock_payload = _as_map(payload)
    pack_hashes = sorted(
        {
            _token(value).lower()
            for value in _as_map(lock_payload.get("pack_hashes")).values()
            if _is_sha256_token(value)
        }
    )
    return [store_artifact_token("packs", artifact_hash) for artifact_hash in pack_hashes]


def _artifact_token_from_direct_store_path(path: str) -> str:
    abs_path = _norm(path)
    rel_parts = _norm_rel(abs_path).split("/")
    if "store" not in rel_parts:
        return ""
    store_index = rel_parts.index("store")
    if len(rel_parts) <= store_index + 1:
        return ""
    category = _token(rel_parts[store_index + 1]).lower()
    if category not in STORE_CATEGORY_IDS:
        return ""
    if os.path.isdir(abs_path):
        artifact_hash = _tree_artifact_hash(abs_path)
    elif os.path.isfile(abs_path):
        artifact_hash = _json_artifact_hash(abs_path)
    else:
        return ""
    if not _is_sha256_token(artifact_hash):
        return ""
    return store_artifact_token(category, artifact_hash)


def _artifact_tokens_from_install_manifest(install_root: str, manifest: Mapping[str, object] | None) -> list[str]:
    payload = normalize_install_manifest(_as_map(manifest))
    tokens: set[str] = set()
    extensions = _as_map(payload.get("extensions"))
    for row in _as_list(extensions.get("official.selected_component_descriptors")):
        descriptor = _as_map(row)
        component_kind = _token(descriptor.get("component_kind"))
        content_hash = _token(descriptor.get("content_hash")).lower()
        if component_kind == "component.lock" and _is_sha256_token(content_hash):
            tokens.add(store_artifact_token("locks", content_hash))
        if component_kind == "component.profile" and _is_sha256_token(content_hash):
            tokens.add(store_artifact_token("profiles", content_hash))
        for managed_path in _as_list(_as_map(descriptor.get("extensions")).get("managed_paths")):
            candidate = os.path.join(_norm(install_root), _token(managed_path).replace("/", os.sep))
            token = _artifact_token_from_direct_store_path(candidate)
            if token:
                tokens.add(token)
    return sorted(tokens)


def _artifact_tokens_from_instance_manifest(instance_root: str, manifest: Mapping[str, object] | None) -> tuple[list[str], list[str]]:
    payload = normalize_instance_manifest(_as_map(manifest))
    tokens: set[str] = set()
    extra_save_manifest_paths: list[str] = []
    if _is_sha256_token(payload.get("pack_lock_hash")):
        tokens.add(store_artifact_token("locks", payload.get("pack_lock_hash")))
    if _is_sha256_token(payload.get("profile_bundle_hash")):
        tokens.add(store_artifact_token("profiles", payload.get("profile_bundle_hash")))
    for row in _as_list(payload.get("embedded_artifacts")):
        category = _token(_as_map(row).get("category")).lower()
        artifact_hash = _token(_as_map(row).get("artifact_hash")).lower()
        if category in STORE_CATEGORY_IDS and _is_sha256_token(artifact_hash):
            tokens.add(store_artifact_token(category, artifact_hash))
    for save_ref in _as_list(payload.get("save_refs")):
        token = _token(save_ref)
        if not token:
            continue
        if os.path.isabs(token):
            candidate = token
        else:
            candidate = os.path.join(_norm(instance_root), token.replace("/", os.sep))
        if os.path.isdir(candidate):
            candidate = os.path.join(candidate, "save.manifest.json")
        if os.path.isfile(candidate):
            extra_save_manifest_paths.append(_norm(candidate))
    return sorted(tokens), sorted(set(extra_save_manifest_paths))


def _artifact_tokens_from_save_manifest(manifest: Mapping[str, object] | None) -> list[str]:
    payload = normalize_save_manifest(_as_map(manifest))
    tokens: set[str] = set()
    if _is_sha256_token(payload.get("pack_lock_hash")):
        tokens.add(store_artifact_token("locks", payload.get("pack_lock_hash")))
    return sorted(tokens)


def _artifact_tokens_from_release_manifest(bundle_root: str, manifest: Mapping[str, object] | None) -> list[str]:
    payload = _as_map(manifest)
    tokens: set[str] = set()
    for row in _as_list(payload.get("artifacts")):
        artifact_name = _token(_as_map(row).get("artifact_name"))
        if not artifact_name:
            continue
        abs_path = os.path.join(_norm(bundle_root), artifact_name.replace("/", os.sep))
        token = _artifact_token_from_direct_store_path(abs_path)
        if token:
            tokens.add(token)
    return sorted(tokens)


def _artifact_tokens_from_release_index(bundle_root: str, payload: Mapping[str, object] | None) -> list[str]:
    tokens: set[str] = set()
    for row in _as_list(_as_map(payload).get("components")):
        descriptor = _as_map(row)
        for managed_path in _as_list(_as_map(descriptor.get("extensions")).get("managed_paths")):
            candidate = os.path.join(_norm(bundle_root), _token(managed_path).replace("/", os.sep))
            token = _artifact_token_from_direct_store_path(candidate)
            if token:
                tokens.add(token)
    embedded_graph = _as_map(_as_map(payload).get("extensions")).get("component_graph")
    for row in _as_list(_as_map(embedded_graph).get("components")):
        descriptor = _as_map(row)
        for managed_path in _as_list(_as_map(descriptor.get("extensions")).get("managed_paths")):
            candidate = os.path.join(_norm(bundle_root), _token(managed_path).replace("/", os.sep))
            token = _artifact_token_from_direct_store_path(candidate)
            if token:
                tokens.add(token)
    return sorted(tokens)


def _artifact_tokens_from_bundle_manifest(bundle_root: str, manifest: Mapping[str, object] | None) -> list[str]:
    payload = normalize_bundle_manifest(_as_map(manifest))
    tokens: set[str] = set()
    content_root = os.path.join(_norm(bundle_root), "content")
    for row in _as_list(payload.get("included_artifacts")):
        relative_path = _token(_as_map(row).get("relative_path"))
        if not relative_path:
            continue
        candidate = os.path.join(content_root, relative_path.replace("/", os.sep))
        token = _artifact_token_from_direct_store_path(candidate)
        if token:
            tokens.add(token)
    return sorted(tokens)


def _manifest_source_rows(install_source: Mapping[str, object]) -> list[dict]:
    install_root = _norm(_as_map(install_source).get("install_root"))
    install_manifest_path = _token(_as_map(install_source).get("install_manifest_path"))
    rows = [
        {
            "source_kind": "install_manifest",
            "source_id": _token(_as_map(install_source).get("install_id")) or os.path.basename(install_root),
            "source_path": install_manifest_path,
            "artifact_tokens": _artifact_tokens_from_install_manifest(install_root, _as_map(install_source).get("manifest")),
        }
    ]
    extra_save_manifest_paths: set[str] = set()
    for manifest_path in _sorted_manifest_paths(_layout_path(install_root, "instances"), "instance.manifest.json"):
        payload = _read_json(manifest_path)
        artifact_tokens, extra_paths = _artifact_tokens_from_instance_manifest(os.path.dirname(manifest_path), payload)
        extra_save_manifest_paths.update(extra_paths)
        instance_manifest = normalize_instance_manifest(payload)
        rows.append(
            {
                "source_kind": "instance_manifest",
                "source_id": _token(instance_manifest.get("instance_id")) or _norm_rel(os.path.relpath(manifest_path, install_root)),
                "source_path": _norm_rel(os.path.relpath(manifest_path, install_root)),
                "artifact_tokens": artifact_tokens,
            }
        )
    save_manifest_paths = set(_sorted_manifest_paths(_layout_path(install_root, "saves"), "save.manifest.json"))
    save_manifest_paths.update(extra_save_manifest_paths)
    for manifest_path in sorted(save_manifest_paths):
        payload = _read_json(manifest_path)
        save_manifest = normalize_save_manifest(payload)
        rows.append(
            {
                "source_kind": "save_manifest",
                "source_id": _token(save_manifest.get("save_id")) or _norm_rel(os.path.relpath(manifest_path, install_root)),
                "source_path": _norm_rel(os.path.relpath(manifest_path, install_root)),
                "artifact_tokens": _artifact_tokens_from_save_manifest(payload),
            }
        )
    release_manifest_path = _layout_path(install_root, "manifests", "release_manifest.json")
    if os.path.isfile(release_manifest_path):
        payload = load_release_manifest(release_manifest_path)
        rows.append(
            {
                "source_kind": "release_manifest",
                "source_id": _token(payload.get("release_id")) or "release_manifest",
                "source_path": _norm_rel(os.path.relpath(release_manifest_path, install_root)),
                "artifact_tokens": _artifact_tokens_from_release_manifest(install_root, payload),
            }
        )
    release_index_path = _layout_path(install_root, "manifests", "release_index.json")
    if os.path.isfile(release_index_path):
        payload = load_release_index(release_index_path)
        rows.append(
            {
                "source_kind": "release_index",
                "source_id": _token(_as_map(payload.get("extensions")).get("release_id")) or "release_index",
                "source_path": _norm_rel(os.path.relpath(release_index_path, install_root)),
                "artifact_tokens": _artifact_tokens_from_release_index(install_root, payload),
            }
        )
    for manifest_path in _sorted_manifest_paths(_layout_path(install_root, "bundles"), "bundle.manifest.json"):
        payload = _read_json(manifest_path)
        bundle_manifest = normalize_bundle_manifest(payload)
        rows.append(
            {
                "source_kind": "bundle_manifest",
                "source_id": _token(bundle_manifest.get("bundle_id")) or _norm_rel(os.path.relpath(manifest_path, install_root)),
                "source_path": _norm_rel(os.path.relpath(manifest_path, install_root)),
                "artifact_tokens": _artifact_tokens_from_bundle_manifest(os.path.dirname(manifest_path), payload),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("source_kind")), _token(row.get("source_id")), _token(row.get("source_path"))))


def _load_lock_payload(store_root: str, artifact_hash: str) -> dict:
    artifact_root = _artifact_root(store_root, "locks", artifact_hash)
    payload_path = os.path.join(artifact_root, ARTIFACT_JSON_PAYLOAD)
    if os.path.isfile(payload_path):
        return _read_json(payload_path)
    return {}


def build_store_reachability_report(
    store_root: str,
    *,
    repo_root: str = ".",
    install_roots: Sequence[str] | None = None,
    registry_path: str = "",
) -> dict:
    target_store = _norm(store_root)
    store_manifest = _read_json(os.path.join(target_store, STORE_ROOT_MANIFEST))
    install_sources = _discover_install_sources(repo_root, target_store, explicit_install_roots=install_roots, registry_path=registry_path)
    source_rows: list[dict] = []
    for row in install_sources:
        source_rows.extend(_manifest_source_rows(row))
    direct_tokens = sorted(
        {
            _token(token)
            for row in source_rows
            for token in _as_list(_as_map(row).get("artifact_tokens"))
            if _token(token)
        }
    )
    reachable_tokens: set[str] = set()
    queue = list(direct_tokens)
    while queue:
        token = queue.pop(0)
        category, artifact_hash = parse_artifact_token(token)
        if not category or not artifact_hash or token in reachable_tokens:
            continue
        reachable_tokens.add(token)
        if category != "locks" or not _artifact_root_exists(target_store, category, artifact_hash):
            continue
        for child in _artifact_tokens_from_lock_payload(_load_lock_payload(target_store, artifact_hash)):
            if child not in reachable_tokens and child not in queue:
                queue.append(child)
        queue.sort()

    report = {
        "report_id": "store.reachability.v1",
        "store_id": _token(store_manifest.get("store_id")) or "store.default",
        "store_root_label": "store",
        "registry_path": os.path.basename(_token(registry_path) or default_install_registry_path(repo_root)),
        "install_ids": sorted(_token(row.get("install_id")) for row in install_sources if _token(row.get("install_id"))),
        "reachability_sources": [
            {
                "source_kind": _token(row.get("source_kind")),
                "source_id": _token(row.get("source_id")),
                "source_path": _token(row.get("source_path")),
                "artifact_tokens": sorted(_token(token) for token in _as_list(row.get("artifact_tokens")) if _token(token)),
            }
            for row in source_rows
        ],
        "direct_artifact_tokens": direct_tokens,
        "reachable_hashes": sorted(reachable_tokens),
        "quarantined_hashes": _quarantined_tokens(target_store),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


__all__ = [
    "ARTIFACT_MANIFEST_NAME",
    "ARTIFACT_JSON_PAYLOAD",
    "ARTIFACT_TREE_PAYLOAD",
    "QUARANTINE_DIRNAME",
    "STORE_CATEGORY_IDS",
    "STORE_LAYOUT_DIRNAME",
    "STORE_ROOT_MANIFEST",
    "build_store_reachability_report",
    "parse_artifact_token",
    "scan_store_artifacts",
    "store_artifact_token",
]
