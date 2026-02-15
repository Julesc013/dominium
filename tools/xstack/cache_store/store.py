"""Content-addressed cache store for registry compile outputs."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256, canonical_json_text

from .merkle import merkle_root_hex, sha256_text


CACHE_SCHEMA_VERSION = "1.0.0"
TOOL_VERSION = "1.0.0"
CACHE_ROOT_REL = os.path.join(".xstack_cache", "registry_compile_cache")


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _entry_root(repo_root: str, key: str) -> str:
    return os.path.join(repo_root, CACHE_ROOT_REL, key)


def _manifest_path(repo_root: str, key: str) -> str:
    return os.path.join(_entry_root(repo_root, key), "manifest.json")


def _outputs_root(repo_root: str, key: str) -> str:
    return os.path.join(_entry_root(repo_root, key), "outputs")


def build_cache_key(
    packs: List[dict],
    contributions: List[dict],
    bundle_selection: List[str],
    tool_version: str = TOOL_VERSION,
) -> Tuple[str, Dict[str, object]]:
    manifest_leaf_hashes: List[str] = []
    contribution_leaf_hashes: List[str] = []

    sorted_packs = sorted(packs or [], key=lambda row: str(row.get("pack_id", "")))
    for row in sorted_packs:
        manifest_leaf_hashes.append(sha256_text(canonical_json_text(row.get("manifest") or {})))

    sorted_contrib = sorted(
        contributions or [],
        key=lambda row: (
            str(row.get("contrib_type", "")),
            str(row.get("id", "")),
            str(row.get("pack_id", "")),
            str(row.get("path", "")),
        ),
    )
    for row in sorted_contrib:
        descriptor = {
            "contrib_type": str(row.get("contrib_type", "")),
            "id": str(row.get("id", "")),
            "pack_id": str(row.get("pack_id", "")),
            "path": str(row.get("path", "")),
        }
        contribution_leaf_hashes.append(sha256_text(canonical_json_text(descriptor)))

    bundle_leaf = sha256_text(
        canonical_json_text(sorted(set(str(item).strip() for item in (bundle_selection or []) if str(item).strip()))
        )
    )
    tool_leaf = sha256_text(str(tool_version))

    ordered_leaves = manifest_leaf_hashes + contribution_leaf_hashes + [bundle_leaf, tool_leaf]
    key = merkle_root_hex(ordered_leaves)
    input_manifest = {
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "tool_version": str(tool_version),
        "manifest_leaf_hashes": manifest_leaf_hashes,
        "contribution_leaf_hashes": contribution_leaf_hashes,
        "bundle_leaf_hash": bundle_leaf,
        "tool_leaf_hash": tool_leaf,
        "merkle_input_hashes": ordered_leaves,
        "cache_key": key,
    }
    return key, input_manifest


def cache_hit(repo_root: str, key: str) -> bool:
    manifest_path = _manifest_path(repo_root, key)
    outputs_root = _outputs_root(repo_root, key)
    return os.path.isfile(manifest_path) and os.path.isdir(outputs_root)


def restore_cache_entry(repo_root: str, key: str, out_dir: str, lockfile_path: str) -> Dict[str, object]:
    entry_outputs_root = _outputs_root(repo_root, key)
    manifest_path = _manifest_path(repo_root, key)
    if not os.path.isfile(manifest_path) or not os.path.isdir(entry_outputs_root):
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.cache_store.missing_entry",
                    "message": "cache entry '{}' does not exist".format(key),
                    "path": "$.cache",
                }
            ],
        }

    payload = json.load(open(manifest_path, "r", encoding="utf-8"))
    outputs = payload.get("outputs") or []
    _ensure_dir(out_dir)
    lock_parent = os.path.dirname(lockfile_path)
    if lock_parent:
        _ensure_dir(lock_parent)

    for row in outputs:
        rel = str(row.get("rel_path", "")).strip()
        source = os.path.join(entry_outputs_root, rel.replace("/", os.sep))
        target = os.path.join(out_dir, rel.replace("/", os.sep))
        _ensure_dir(os.path.dirname(target))
        shutil.copy2(source, target)

    lock_rel = str((payload.get("lockfile") or {}).get("rel_path", "")).strip()
    lock_source = os.path.join(entry_outputs_root, lock_rel.replace("/", os.sep))
    shutil.copy2(lock_source, lockfile_path)

    return {
        "result": "complete",
        "cache_key": key,
        "cache_hit": True,
        "outputs": outputs,
        "lockfile": payload.get("lockfile") or {},
    }


def store_cache_entry(
    repo_root: str,
    key: str,
    input_manifest: Dict[str, object],
    out_dir: str,
    output_files: List[str],
    lockfile_path: str,
) -> Dict[str, object]:
    entry_root = _entry_root(repo_root, key)
    outputs_root = _outputs_root(repo_root, key)
    _ensure_dir(outputs_root)

    stored_outputs = []
    for abs_path in sorted(output_files):
        rel = _norm(os.path.relpath(abs_path, out_dir))
        target = os.path.join(outputs_root, rel.replace("/", os.sep))
        _ensure_dir(os.path.dirname(target))
        shutil.copy2(abs_path, target)
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
        stored_outputs.append(
            {
                "rel_path": rel,
                "sha256": canonical_sha256(payload),
            }
        )

    lock_rel = "bundle.lockfile.json"
    lock_target = os.path.join(outputs_root, lock_rel)
    shutil.copy2(lockfile_path, lock_target)
    lock_payload = json.load(open(lockfile_path, "r", encoding="utf-8"))
    lock_row = {
        "rel_path": lock_rel,
        "sha256": canonical_sha256(lock_payload),
    }

    manifest_payload = {
        "artifact_class": "RUN_META",
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "cache_key": key,
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_manifest": input_manifest,
        "outputs": stored_outputs,
        "lockfile": lock_row,
    }
    _ensure_dir(entry_root)
    with open(_manifest_path(repo_root, key), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "result": "complete",
        "cache_key": key,
        "cache_hit": False,
        "outputs": stored_outputs,
        "lockfile": lock_row,
    }

