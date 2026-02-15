"""Pack manifest discovery + validation for deterministic Pack System v1."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.validator import validate_instance

from .constants import (
    FORBIDDEN_PACK_EXTENSIONS,
    PACK_CATEGORIES,
    PACK_MANIFEST_NAME,
    PACKS_ROOT_REL,
)
from .dependency_resolver import parse_dependency_token, resolve_packs
from .errors import build_error, result_complete, result_refused


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _rel(path: str, repo_root: str) -> str:
    return _norm(os.path.relpath(path, repo_root))


def _is_manifest_path_valid(rel_path: str) -> bool:
    parts = _norm(rel_path).split("/")
    if len(parts) != 4:
        return False
    return parts[0] == PACKS_ROOT_REL and parts[3] == PACK_MANIFEST_NAME


def _discover_pack_manifests(repo_root: str, packs_root: str) -> List[str]:
    manifests = []
    if not os.path.isdir(packs_root):
        return manifests
    for root, _dirs, files in os.walk(packs_root):
        for name in files:
            if name != PACK_MANIFEST_NAME:
                continue
            manifests.append(os.path.join(root, name))
    return sorted(_norm(path) for path in manifests)


def _scan_forbidden_files(pack_dir: str, pack_id: str, repo_root: str) -> List[Dict[str, str]]:
    errors = []
    for root, _dirs, files in os.walk(pack_dir):
        for name in files:
            _, ext = os.path.splitext(name)
            if ext.lower() not in FORBIDDEN_PACK_EXTENSIONS:
                continue
            path = _rel(os.path.join(root, name), repo_root)
            errors.append(
                build_error(
                    "refuse.pack.executable_content_forbidden",
                    "pack '{}' contains forbidden executable file '{}'".format(pack_id, path),
                    "$.packs.{}.files".format(pack_id),
                )
            )
    return errors


def _read_manifest(path: str) -> Tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid manifest root"
    return payload, ""


def load_pack_set(
    repo_root: str,
    packs_root_rel: str = PACKS_ROOT_REL,
    schema_repo_root: str = "",
) -> Dict[str, object]:
    packs_root = os.path.join(repo_root, packs_root_rel)
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    manifests = _discover_pack_manifests(repo_root, packs_root)
    errors: List[Dict[str, str]] = []
    packs: List[dict] = []
    seen_pack_ids: Dict[str, dict] = {}

    for manifest_path in manifests:
        rel_manifest = _rel(manifest_path, repo_root)
        if not _is_manifest_path_valid(rel_manifest):
            errors.append(
                build_error(
                    "refuse.pack.invalid_manifest_location",
                    "manifest must be at packs/<category>/<pack_id>/pack.json: '{}'".format(rel_manifest),
                    "$.packs",
                )
            )
            continue

        parts = rel_manifest.split("/")
        category = parts[1]
        directory_pack_id = parts[2]
        if category not in PACK_CATEGORIES:
            errors.append(
                build_error(
                    "refuse.pack.invalid_category",
                    "invalid pack category '{}' for '{}'".format(category, rel_manifest),
                    "$.packs",
                )
            )
            continue

        manifest, manifest_error = _read_manifest(manifest_path)
        if manifest_error:
            errors.append(
                build_error(
                    "refuse.pack.manifest_parse_failed",
                    "unable to parse pack manifest '{}'".format(rel_manifest),
                    "$.packs",
                )
            )
            continue

        schema_validation = validate_instance(
            repo_root=schema_root,
            schema_name="pack_manifest",
            payload=manifest,
            strict_top_level=True,
        )
        if not bool(schema_validation.get("valid", False)):
            for row in schema_validation.get("errors", []):
                errors.append(
                    build_error(
                        "refuse.pack.manifest_invalid",
                        "{}: {}".format(
                            rel_manifest,
                            str(row.get("message", "")),
                        ),
                        str(row.get("path", "$")),
                    )
                )
            continue

        pack_id = str(manifest.get("pack_id", "")).strip()
        version = str(manifest.get("version", "")).strip()
        if pack_id != directory_pack_id:
            errors.append(
                build_error(
                    "refuse.pack.pack_id_path_mismatch",
                    "pack_id '{}' does not match directory '{}' in '{}'".format(
                        pack_id,
                        directory_pack_id,
                        rel_manifest,
                    ),
                    "$.pack_id",
                )
            )
            continue

        existing = seen_pack_ids.get(pack_id)
        if existing:
            errors.append(
                build_error(
                    "refuse.pack.duplicate_pack_id",
                    "duplicate pack_id '{}' at '{}' and '{}'".format(
                        pack_id,
                        str(existing.get("manifest_rel", "")),
                        rel_manifest,
                    ),
                    "$.pack_id",
                )
            )
            if str(existing.get("version", "")) != version:
                errors.append(
                    build_error(
                        "refuse.pack.version_conflict",
                        "pack_id '{}' has conflicting versions '{}' and '{}'".format(
                            pack_id,
                            str(existing.get("version", "")),
                            version,
                        ),
                        "$.version",
                    )
                )
            continue

        pack_dir = os.path.dirname(manifest_path)
        dependency_specs = []
        for raw in sorted(str(item) for item in (manifest.get("dependencies") or [])):
            dep_id, dep_version = parse_dependency_token(raw)
            dependency_specs.append(
                {
                    "raw": raw,
                    "pack_id": dep_id,
                    "required_version": dep_version,
                }
            )

        pack_row = {
            "pack_id": pack_id,
            "version": version,
            "category": category,
            "signature_status": str(manifest.get("signature_status", "")).strip(),
            "manifest": manifest,
            "manifest_path": manifest_path,
            "manifest_rel": rel_manifest,
            "pack_dir": pack_dir,
            "pack_dir_rel": _rel(pack_dir, repo_root),
            "dependencies": sorted(str(item) for item in (manifest.get("dependencies") or [])),
            "dependency_specs": sorted(
                dependency_specs,
                key=lambda row: (
                    str(row.get("pack_id", "")),
                    str(row.get("required_version", "")),
                    str(row.get("raw", "")),
                ),
            ),
        }
        seen_pack_ids[pack_id] = pack_row
        packs.append(pack_row)
        errors.extend(_scan_forbidden_files(pack_dir, pack_id, repo_root))

    packs = sorted(packs, key=lambda row: str(row.get("pack_id", "")))
    if errors:
        return result_refused({"pack_count": len(packs), "packs": packs}, errors)

    dependency_result = resolve_packs(packs, bundle_selection=None)
    if dependency_result.get("result") == "refused":
        return result_refused({"pack_count": len(packs), "packs": packs}, dependency_result.get("errors", []))

    return result_complete(
        {
            "pack_count": len(packs),
            "packs": packs,
            "ordered_pack_ids": list(dependency_result.get("ordered_pack_ids", [])),
        }
    )
