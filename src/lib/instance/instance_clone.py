"""Deterministic instance clone helpers."""

from __future__ import annotations

import os
import shutil
from typing import Dict, Mapping

from src.lib.instance.instance_validator import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
    validate_instance_manifest,
)
from tools.lib.content_store import (
    JSON_PAYLOAD,
    TREE_PAYLOAD_DIR,
    artifact_payload_path,
    build_install_ref,
    build_store_locator,
    initialize_store_root,
    load_json,
    resolve_instance_artifact_root,
    resolve_locator_path,
    store_add_artifact,
    store_add_tree_artifact,
)


DEFAULT_INSTANCE_MANIFEST = "instance.manifest.json"
CLONE_IGNORE_NAMES = {"saves"}


def _ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def _copy_file(src: str, dest: str) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(dest)))
    shutil.copyfile(src, dest)


def _copy_tree(src: str, dest: str, *, ignore_names: set[str] | None = None) -> None:
    ignore = set(ignore_names or set())
    for root, dirnames, filenames in os.walk(src):
        dirnames[:] = sorted(name for name in dirnames if name not in ignore)
        rel_root = os.path.relpath(root, src)
        target_root = dest if rel_root == "." else os.path.join(dest, rel_root)
        _ensure_dir(target_root)
        for filename in sorted(filenames):
            _copy_file(os.path.join(root, filename), os.path.join(target_root, filename))


def _copy_selected_subtrees(src_root: str, dest_root: str, rel_paths: list[str]) -> None:
    for rel_path in rel_paths:
        source_path = os.path.join(src_root, rel_path)
        dest_path = os.path.join(dest_root, rel_path)
        if os.path.isdir(source_path):
            _copy_tree(source_path, dest_path)
        elif os.path.isfile(source_path):
            _copy_file(source_path, dest_path)


def _insert_embedded_artifacts_into_store(
    source_root: str,
    source_manifest: Mapping[str, object],
    store_root: str,
) -> Dict[str, object]:
    inserted = []
    for row in list(source_manifest.get("embedded_artifacts") or []):
        if not isinstance(row, Mapping):
            continue
        category = str(row.get("category", "")).strip()
        artifact_hash = str(row.get("artifact_hash", "")).strip()
        artifact_type = str(row.get("artifact_type", "")).strip()
        if not category or not artifact_hash or artifact_type not in {"json", "tree"}:
            continue
        source_artifact_root = resolve_instance_artifact_root(
            source_root,
            dict(source_manifest or {}),
            category,
            artifact_hash,
        )
        if not os.path.isdir(source_artifact_root):
            return {
                "result": "refused",
                "refusal_code": "refusal.instance.clone_missing_artifact",
                "message": "source embedded artifact missing",
                "details": {"category": category, "artifact_hash": artifact_hash},
            }
        if artifact_type == "json":
            payload_path = os.path.join(source_artifact_root, JSON_PAYLOAD)
            if not os.path.isfile(payload_path):
                return {
                    "result": "refused",
                    "refusal_code": "refusal.instance.clone_missing_artifact",
                    "message": "source embedded JSON artifact missing",
                    "details": {"category": category, "artifact_hash": artifact_hash},
                }
            payload = load_json(payload_path)
            result = store_add_artifact(store_root, category, payload, expected_hash=artifact_hash)
        else:
            payload_root = os.path.join(source_artifact_root, TREE_PAYLOAD_DIR)
            if not os.path.isdir(payload_root):
                return {
                    "result": "refused",
                    "refusal_code": "refusal.instance.clone_missing_artifact",
                    "message": "source embedded tree artifact missing",
                    "details": {"category": category, "artifact_hash": artifact_hash},
                }
            result = store_add_tree_artifact(store_root, category, payload_root)
        if str(result.get("artifact_hash", "")).strip() != artifact_hash:
            return {
                "result": "refused",
                "refusal_code": "refusal.instance.clone_hash_mismatch",
                "message": "cloned artifact hash mismatch",
                "details": {"category": category, "artifact_hash": artifact_hash},
            }
        inserted.append({"category": category, "artifact_hash": artifact_hash})
    return {"result": "complete", "inserted_artifacts": inserted}


def clone_instance_local(
    *,
    repo_root: str,
    source_manifest_path: str,
    target_root: str,
    instance_id: str,
    created_at: str,
    deterministic: bool,
    fork_only: bool = False,
    duplicate_embedded_artifacts: bool = False,
    store_root: str = "",
) -> Dict[str, object]:
    del deterministic
    source_validation = validate_instance_manifest(
        repo_root=repo_root,
        instance_manifest_path=source_manifest_path,
    )
    if source_validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(source_validation.get("refusal_code", "")).strip() or "refusal.instance.clone_invalid_source",
            "message": "source instance manifest validation failed",
            "details": {"manifest": os.path.basename(source_manifest_path)},
        }

    source_manifest = dict(source_validation.get("instance_manifest") or {})
    source_root = os.path.dirname(os.path.abspath(source_manifest_path))
    source_mode = str(source_manifest.get("mode", "portable") or "portable").strip().lower()
    source_store_root = resolve_locator_path(source_root, source_manifest.get("store_root"))
    effective_store_root = os.path.abspath(str(store_root or source_store_root or "").strip()) if str(store_root or source_store_root or "").strip() else ""

    clone_mode = source_mode
    if source_mode == "portable" and not duplicate_embedded_artifacts and effective_store_root:
        clone_mode = "linked"

    if clone_mode == source_mode and not fork_only:
        _copy_tree(source_root, target_root, ignore_names=CLONE_IGNORE_NAMES)
    else:
        _ensure_dir(target_root)
        selected_rel_paths = ["lockfiles"]
        if clone_mode == "portable":
            selected_rel_paths.extend(["embedded_artifacts", "embedded_builds"])
        elif fork_only and source_mode == "portable" and duplicate_embedded_artifacts:
            selected_rel_paths.extend(["embedded_artifacts", "embedded_builds"])
        _copy_selected_subtrees(source_root, target_root, selected_rel_paths)

    if clone_mode == "linked" and source_mode == "portable":
        if not effective_store_root:
            return {
                "result": "refused",
                "refusal_code": "refusal.instance.clone_store_required",
                "message": "portable to linked clone requires store_root",
                "details": {},
            }
        initialize_store_root(effective_store_root)
        insert_result = _insert_embedded_artifacts_into_store(source_root, source_manifest, effective_store_root)
        if insert_result.get("result") != "complete":
            return insert_result

    payload = dict(source_manifest)
    payload["instance_id"] = str(instance_id or "").strip()
    payload["created_at"] = str(created_at or payload.get("created_at", "")).strip() or str(payload.get("created_at", "")).strip()
    payload["last_used_at"] = str(created_at or payload.get("last_used_at", "")).strip() or str(payload.get("last_used_at", "")).strip()
    payload["data_root"] = str(payload.get("data_root", ".")).strip() or "."

    if clone_mode == "linked":
        payload["mode"] = "linked"
        payload["embedded_artifacts"] = []
        payload["embedded_builds"] = {}
        payload["capability_lockfile"] = str(payload.get("capability_lockfile", "")).strip()
        if effective_store_root:
            store_manifest = initialize_store_root(effective_store_root)
            payload["store_root"] = build_store_locator(target_root, effective_store_root, store_manifest)
    else:
        payload["mode"] = "portable"
        payload["store_root"] = {}

    source_install_manifest_path = ""
    install_ref = dict(source_manifest.get("install_ref") or {})
    manifest_ref = str(install_ref.get("manifest_ref", "")).strip()
    if manifest_ref:
        source_install_manifest_path = os.path.abspath(
            manifest_ref if os.path.isabs(manifest_ref) else os.path.join(source_root, manifest_ref)
        )
    if source_install_manifest_path and os.path.isfile(source_install_manifest_path):
        try:
            source_install_manifest = load_json(source_install_manifest_path)
        except (OSError, ValueError):
            source_install_manifest = {}
        if source_install_manifest:
            payload["install_ref"] = build_install_ref(target_root, source_install_manifest_path, source_install_manifest)
            payload["install_id"] = source_install_manifest.get("install_id") or payload.get("install_id")

    manifest_path = os.path.join(target_root, DEFAULT_INSTANCE_MANIFEST)
    payload = normalize_instance_manifest(payload)
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    validation = validate_instance_manifest(
        repo_root=repo_root,
        instance_manifest_path=manifest_path,
        manifest_payload=payload,
    )
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", "")).strip() or "refusal.instance.clone_invalid_target",
            "message": "cloned instance manifest validation failed",
            "details": {"instance_id": payload.get("instance_id", "")},
        }

    manifest_payload = dict(validation.get("instance_manifest") or payload)
    _ensure_dir(target_root)
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as handle:
        import json

        json.dump(manifest_payload, handle, indent=2, sort_keys=False)
        handle.write("\n")

    return {
        "result": "complete",
        "instance_manifest": manifest_payload,
        "instance_manifest_path": manifest_path.replace("\\", "/"),
        "clone_mode": clone_mode,
    }
