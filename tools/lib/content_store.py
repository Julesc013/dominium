"""Deterministic content-addressable storage helpers for linked and portable flows."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from typing import Dict, Iterable, List, Optional, Tuple

from src.lib.artifact import (
    ARTIFACT_DEGRADE_STRICT_REFUSE,
    ARTIFACT_KIND_PROFILE_BUNDLE,
    artifact_kind_from_store_category,
    canonicalize_artifact_manifest,
)


HASH_ALGORITHM = "sha256"
STORE_ROOT_MANIFEST = "store.root.json"
ARTIFACT_MANIFEST = "artifact.manifest.json"
JSON_PAYLOAD = "payload.json"
TREE_PAYLOAD_DIR = "payload"

STORE_CATEGORIES = (
    "packs",
    "profiles",
    "blueprints",
    "system_templates",
    "process_definitions",
    "logic_programs",
    "view_presets",
    "resource_pack_stubs",
    "locks",
    "migrations",
    "repro",
)

PATH_LIKE_KEYS = {
    "artifact_path",
    "compat_report_ref",
    "instance_manifest_ref",
    "lockfile_ref",
    "manifest_path",
    "pack_path",
    "root_path",
    "store_root",
}


def _ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def _normalize_slashes(value: str) -> str:
    text = str(value or "").replace("\\", "/")
    if text.startswith("./"):
        text = text[2:]
    return text


def _normalize_value(value: object, key: str = "") -> object:
    if isinstance(value, dict):
        return {
            str(name): _normalize_value(item, str(name))
            for name, item in sorted(value.items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, str):
        if key in PATH_LIKE_KEYS or key.endswith(("_path", "_root", "_ref")):
            return _normalize_slashes(value)
        return value
    return value


def canonical_json_text(payload: object) -> str:
    return json.dumps(
        _normalize_value(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_sha256(payload: object) -> str:
    return hashlib.sha256(canonical_json_text(payload).encode("utf-8")).hexdigest()


def deterministic_fingerprint(payload: Dict[str, object]) -> str:
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def pretty_write_json(path: str, payload: object) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(_normalize_value(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def copy_dir(src: str, dest: str) -> None:
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_entries(source_dir: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    for root, dirnames, filenames in os.walk(source_dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            abs_path = os.path.join(root, filename)
            rel_path = _normalize_slashes(os.path.relpath(abs_path, source_dir))
            entries.append(
                {
                    "path": rel_path,
                    "sha256": sha256_file(abs_path),
                    "size_bytes": int(os.path.getsize(abs_path)),
                }
            )
    return entries


def _tree_descriptor(entries: List[Dict[str, object]]) -> Dict[str, object]:
    return {"entries": list(entries)}


def _store_root_manifest_payload(root_path: str, store_id: str) -> Dict[str, object]:
    payload = {
        "store_id": str(store_id or "").strip() or "store.default",
        "root_path": _normalize_slashes(os.path.abspath(root_path)),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def initialize_store_root(root_path: str, store_id: str = "store.default") -> Dict[str, object]:
    _ensure_dir(root_path)
    for rel_path in (
        "bin",
        os.path.join("store", "packs"),
        os.path.join("store", "profiles"),
        os.path.join("store", "blueprints"),
        os.path.join("store", "system_templates"),
        os.path.join("store", "process_definitions"),
        os.path.join("store", "logic_programs"),
        os.path.join("store", "view_presets"),
        os.path.join("store", "resource_pack_stubs"),
        os.path.join("store", "locks"),
        os.path.join("store", "migrations"),
        os.path.join("store", "repro"),
        "instances",
        "saves",
        "exports",
    ):
        _ensure_dir(os.path.join(root_path, rel_path))
    manifest = _store_root_manifest_payload(root_path, store_id)
    pretty_write_json(os.path.join(root_path, STORE_ROOT_MANIFEST), manifest)
    return manifest


def load_store_root_manifest(root_path: str) -> Dict[str, object]:
    path = os.path.join(root_path, STORE_ROOT_MANIFEST)
    if os.path.isfile(path):
        return load_json(path)
    return initialize_store_root(root_path)


def _category_token(category: str) -> str:
    token = str(category or "").strip().lower()
    if token.endswith("/"):
        token = token[:-1]
    if token in STORE_CATEGORIES:
        return token
    raise ValueError("unsupported store category: {}".format(category))


def store_artifact_root(root_path: str, category: str, artifact_hash: str) -> str:
    return os.path.join(root_path, "store", _category_token(category), str(artifact_hash))


def embedded_artifact_root(instance_root: str, category: str, artifact_hash: str) -> str:
    return os.path.join(instance_root, "embedded_artifacts", _category_token(category), str(artifact_hash))


def artifact_payload_path(artifact_root: str, artifact_type: str) -> str:
    if artifact_type == "tree":
        return os.path.join(artifact_root, TREE_PAYLOAD_DIR)
    return os.path.join(artifact_root, JSON_PAYLOAD)


def _artifact_manifest_payload(
    *,
    category: str,
    artifact_hash: str,
    artifact_type: str,
    payload_ref: str,
    descriptor: Dict[str, object],
) -> Dict[str, object]:
    payload = {
        "category": _category_token(category),
        "artifact_hash": str(artifact_hash),
        "artifact_type": str(artifact_type),
        "hash_algorithm": HASH_ALGORITHM,
        "payload_ref": _normalize_slashes(payload_ref),
        "content_descriptor": descriptor,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    artifact_kind_id = artifact_kind_from_store_category(category)
    if artifact_kind_id:
        payload["artifact_kind_id"] = artifact_kind_id
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _write_json_artifact(
    artifact_root: str,
    category: str,
    payload: Dict[str, object],
    expected_hash: Optional[str] = None,
) -> Dict[str, object]:
    artifact_hash = str(expected_hash or canonical_sha256(payload))
    if os.path.isdir(artifact_root):
        return {
            "created": False,
            "artifact_hash": artifact_hash,
            "artifact_root": _normalize_slashes(artifact_root),
            "artifact_type": "json",
        }
    _ensure_dir(artifact_root)
    pretty_write_json(os.path.join(artifact_root, JSON_PAYLOAD), payload)
    manifest = _artifact_manifest_payload(
        category=category,
        artifact_hash=artifact_hash,
        artifact_type="json",
        payload_ref=JSON_PAYLOAD,
        descriptor={"canonical_sha256": artifact_hash},
    )
    pretty_write_json(os.path.join(artifact_root, ARTIFACT_MANIFEST), manifest)
    return {
        "created": True,
        "artifact_hash": artifact_hash,
        "artifact_root": _normalize_slashes(artifact_root),
        "artifact_type": "json",
    }


def _copy_tree(source_dir: str, dest_dir: str) -> None:
    for entry in _tree_entries(source_dir):
        rel_path = str(entry["path"])
        abs_src = os.path.join(source_dir, rel_path.replace("/", os.sep))
        abs_dest = os.path.join(dest_dir, rel_path.replace("/", os.sep))
        _ensure_dir(os.path.dirname(abs_dest))
        shutil.copyfile(abs_src, abs_dest)


def _write_tree_artifact(artifact_root: str, category: str, source_dir: str) -> Dict[str, object]:
    entries = _tree_entries(source_dir)
    artifact_hash = canonical_sha256(_tree_descriptor(entries))
    if os.path.isdir(artifact_root):
        return {
            "created": False,
            "artifact_hash": artifact_hash,
            "artifact_root": _normalize_slashes(artifact_root),
            "artifact_type": "tree",
        }
    payload_root = os.path.join(artifact_root, TREE_PAYLOAD_DIR)
    _ensure_dir(payload_root)
    _copy_tree(source_dir, payload_root)
    manifest = _artifact_manifest_payload(
        category=category,
        artifact_hash=artifact_hash,
        artifact_type="tree",
        payload_ref=TREE_PAYLOAD_DIR,
        descriptor=_tree_descriptor(entries),
    )
    pretty_write_json(os.path.join(artifact_root, ARTIFACT_MANIFEST), manifest)
    return {
        "created": True,
        "artifact_hash": artifact_hash,
        "artifact_root": _normalize_slashes(artifact_root),
        "artifact_type": "tree",
    }


def store_add_artifact(
    store_root: str,
    category: str,
    artifact: Dict[str, object],
    expected_hash: Optional[str] = None,
) -> Dict[str, object]:
    load_store_root_manifest(store_root)
    artifact_hash = str(expected_hash or canonical_sha256(artifact))
    return _write_json_artifact(
        store_artifact_root(store_root, category, artifact_hash),
        category,
        artifact,
        expected_hash=artifact_hash,
    )


def store_add_tree_artifact(store_root: str, category: str, source_dir: str) -> Dict[str, object]:
    load_store_root_manifest(store_root)
    entries = _tree_entries(source_dir)
    artifact_hash = canonical_sha256(_tree_descriptor(entries))
    return _write_tree_artifact(store_artifact_root(store_root, category, artifact_hash), category, source_dir)


def embed_json_artifact(
    instance_root: str,
    category: str,
    payload: Dict[str, object],
    expected_hash: Optional[str] = None,
) -> Dict[str, object]:
    artifact_hash = str(expected_hash or canonical_sha256(payload))
    return _write_json_artifact(
        embedded_artifact_root(instance_root, category, artifact_hash),
        category,
        payload,
        expected_hash=artifact_hash,
    )


def embed_tree_artifact(instance_root: str, category: str, source_dir: str) -> Dict[str, object]:
    entries = _tree_entries(source_dir)
    artifact_hash = canonical_sha256(_tree_descriptor(entries))
    return _write_tree_artifact(embedded_artifact_root(instance_root, category, artifact_hash), category, source_dir)


def store_get_artifact(store_root: str, category: str, artifact_hash: str) -> Dict[str, object]:
    artifact_root = store_artifact_root(store_root, category, artifact_hash)
    manifest_path = os.path.join(artifact_root, ARTIFACT_MANIFEST)
    if not os.path.isfile(manifest_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.store.not_found",
            "artifact_hash": str(artifact_hash),
            "category": _category_token(category),
        }
    manifest = load_json(manifest_path)
    return {
        "result": "ok",
        "artifact_hash": str(artifact_hash),
        "artifact_root": _normalize_slashes(artifact_root),
        "manifest": manifest,
    }


def _verify_json_artifact(artifact_root: str, manifest: Dict[str, object]) -> bool:
    payload = load_json(os.path.join(artifact_root, JSON_PAYLOAD))
    return canonical_sha256(payload) == str(manifest.get("artifact_hash", "")).strip()


def _verify_tree_artifact(artifact_root: str, manifest: Dict[str, object]) -> bool:
    payload_root = os.path.join(artifact_root, TREE_PAYLOAD_DIR)
    actual = _tree_descriptor(_tree_entries(payload_root))
    return canonical_sha256(actual) == str(manifest.get("artifact_hash", "")).strip()


def store_verify(store_root: str, category: str, artifact_hash: str) -> Dict[str, object]:
    lookup = store_get_artifact(store_root, category, artifact_hash)
    if lookup.get("result") != "ok":
        return lookup
    artifact_root = str(lookup.get("artifact_root", "")).replace("/", os.sep)
    manifest = dict(lookup.get("manifest") or {})
    artifact_type = str(manifest.get("artifact_type", "")).strip()
    verified = False
    if artifact_type == "json":
        verified = _verify_json_artifact(artifact_root, manifest)
    elif artifact_type == "tree":
        verified = _verify_tree_artifact(artifact_root, manifest)
    return {
        "result": "ok" if verified else "refused",
        "artifact_hash": str(artifact_hash),
        "category": _category_token(category),
        "verified": bool(verified),
        "refusal_code": "" if verified else "refusal.store.hash_mismatch",
    }


def load_artifact_manifest(artifact_root: str) -> Dict[str, object]:
    manifest_path = os.path.join(artifact_root, ARTIFACT_MANIFEST)
    if not os.path.isfile(manifest_path):
        return {}
    return load_json(manifest_path)


def manifest_ref_path(base_root: str, target_path: str) -> str:
    try:
        rel_path = os.path.relpath(os.path.abspath(target_path), os.path.abspath(base_root))
    except ValueError:
        rel_path = os.path.abspath(target_path)
    return _normalize_slashes(rel_path)


def resolve_locator_path(base_root: str, locator: object) -> str:
    if isinstance(locator, dict):
        root_path = str(locator.get("root_path", "")).strip()
        manifest_ref = str(locator.get("manifest_ref", "")).strip()
        if manifest_ref:
            candidate = manifest_ref if os.path.isabs(manifest_ref) else os.path.join(base_root, manifest_ref)
            return os.path.dirname(os.path.abspath(candidate))
        if root_path:
            return os.path.abspath(root_path if os.path.isabs(root_path) else os.path.join(base_root, root_path))
        return ""
    token = str(locator or "").strip()
    if not token:
        return ""
    return os.path.abspath(token if os.path.isabs(token) else os.path.join(base_root, token))


def build_pack_lock_payload(
    *,
    instance_id: str,
    pack_ids: Iterable[str],
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    source_payload: Optional[Dict[str, object]] = None,
) -> Tuple[Dict[str, object], str]:
    ordered_pack_ids = sorted({str(item).strip() for item in list(pack_ids or []) if str(item).strip()})
    payload = dict(source_payload or {})
    payload.setdefault("schema_id", "dominium.schema.packs.pack_lock")
    payload.setdefault("schema_version", "1.0.0")
    payload.setdefault("format_version", "1.0.0")
    payload.setdefault("pack_lock_id", "pack_lock.{}".format(instance_id))
    payload.setdefault("ordered_pack_ids", ordered_pack_ids)
    payload.setdefault("ordered_pack_versions", ["unversioned"] * len(ordered_pack_ids))
    payload.setdefault("pack_hashes", {})
    payload.setdefault("pack_compat_hashes", {})
    payload.setdefault("mod_policy_id", mod_policy_id)
    payload.setdefault("overlay_conflict_policy_id", overlay_conflict_policy_id)
    payload.setdefault("engine_version_created", "unknown")
    payload.setdefault("extensions", {})
    payload["ordered_pack_ids"] = ordered_pack_ids
    payload["ordered_pack_versions"] = list(payload.get("ordered_pack_versions") or ["unversioned"] * len(ordered_pack_ids))
    payload["pack_hashes"] = dict(payload.get("pack_hashes") or {})
    payload["pack_compat_hashes"] = dict(payload.get("pack_compat_hashes") or {})
    payload["deterministic_fingerprint"] = ""
    payload.pop("pack_lock_hash", None)
    hash_seed = dict(payload)
    artifact_hash = canonical_sha256(hash_seed)
    payload["pack_lock_hash"] = artifact_hash
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload, artifact_hash


def build_profile_bundle_payload(
    *,
    instance_id: str,
    profile_ids: Iterable[str],
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
) -> Tuple[Dict[str, object], str]:
    payload = canonicalize_artifact_manifest(
        {
        "schema_id": "dominium.schema.profile.bundle",
        "schema_version": "1.0.0",
        "format_version": "1.0.0",
        "artifact_kind_id": ARTIFACT_KIND_PROFILE_BUNDLE,
        "artifact_id": "profile_bundle.{}".format(instance_id),
        "profile_bundle_id": "profile_bundle.{}".format(instance_id),
        "profile_ids": sorted({str(item).strip() for item in list(profile_ids or []) if str(item).strip()}),
        "required_contract_ranges": {},
        "required_capabilities": [],
        "compatible_topology_profiles": [],
        "compatible_physics_profiles": [],
        "degrade_mode_id": ARTIFACT_DEGRADE_STRICT_REFUSE,
        "migration_refs": [],
        "mod_policy_id": str(mod_policy_id),
        "overlay_conflict_policy_id": str(overlay_conflict_policy_id),
        "engine_version_created": "unknown",
        "extensions": {},
        },
        expected_kind_id=ARTIFACT_KIND_PROFILE_BUNDLE,
    )
    artifact_hash = canonical_sha256(payload)
    return payload, artifact_hash


def build_store_locator(instance_root: str, store_root: str, store_manifest: Dict[str, object]) -> Dict[str, object]:
    return {
        "store_id": str(store_manifest.get("store_id", "store.default")),
        "root_path": manifest_ref_path(instance_root, store_root),
        "manifest_ref": manifest_ref_path(instance_root, os.path.join(store_root, STORE_ROOT_MANIFEST)),
    }


def build_install_ref(instance_root: str, install_manifest_path: str, install_manifest: Dict[str, object]) -> Dict[str, object]:
    install_root_token = str(install_manifest.get("install_root", "") or "").strip()
    if not install_root_token or install_root_token == ".":
        install_root_path = os.path.dirname(os.path.abspath(install_manifest_path))
    elif os.path.isabs(install_root_token):
        install_root_path = install_root_token
    else:
        install_root_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(install_manifest_path)), install_root_token))
    return {
        "install_id": str(install_manifest.get("install_id", "")).strip(),
        "manifest_ref": manifest_ref_path(instance_root, install_manifest_path),
        "root_path": manifest_ref_path(instance_root, install_root_path),
    }


def resolve_instance_artifact_root(
    instance_root: str,
    instance_manifest: Dict[str, object],
    category: str,
    artifact_hash: str,
) -> str:
    embedded_root = embedded_artifact_root(instance_root, category, artifact_hash)
    if os.path.isdir(embedded_root):
        return embedded_root
    store_root = resolve_locator_path(instance_root, instance_manifest.get("store_root"))
    if store_root:
        linked_root = store_artifact_root(store_root, category, artifact_hash)
        if os.path.isdir(linked_root):
            return linked_root
    return embedded_root


def load_instance_json_artifact(
    instance_root: str,
    instance_manifest: Dict[str, object],
    category: str,
    artifact_hash: str,
) -> Dict[str, object]:
    artifact_root = resolve_instance_artifact_root(instance_root, instance_manifest, category, artifact_hash)
    payload_path = os.path.join(artifact_root, JSON_PAYLOAD)
    if not os.path.isfile(payload_path):
        return {}
    return load_json(payload_path)


def load_instance_artifact_manifest(
    instance_root: str,
    instance_manifest: Dict[str, object],
    category: str,
    artifact_hash: str,
) -> Dict[str, object]:
    artifact_root = resolve_instance_artifact_root(instance_root, instance_manifest, category, artifact_hash)
    return load_artifact_manifest(artifact_root)


def artifact_ref(
    *,
    category: str,
    artifact_hash: str,
    artifact_type: str,
    artifact_root: str,
    instance_root: str,
    artifact_id: str = "",
) -> Dict[str, object]:
    payload = {
        "category": _category_token(category),
        "artifact_hash": str(artifact_hash),
        "artifact_type": str(artifact_type),
        "artifact_path": manifest_ref_path(instance_root, artifact_root),
    }
    if artifact_id:
        payload["artifact_id"] = str(artifact_id)
    return payload


def index_file_tree(root_path: str, ignore_rel_paths: Optional[Iterable[str]] = None) -> List[Dict[str, object]]:
    ignored = { _normalize_slashes(path) for path in list(ignore_rel_paths or []) if str(path).strip() }
    entries: List[Dict[str, object]] = []
    for root, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            abs_path = os.path.join(root, filename)
            rel_path = _normalize_slashes(os.path.relpath(abs_path, root_path))
            if rel_path in ignored:
                continue
            entries.append(
                {
                    "content_path": rel_path,
                    "content_kind": "file",
                    "sha256": sha256_file(abs_path),
                    "size_bytes": int(os.path.getsize(abs_path)),
                }
            )
    return entries
