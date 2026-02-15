"""Bundle profile loader + deterministic selection for registry compile and session boot."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from tools.xstack.compatx.validator import validate_instance
from tools.xstack.pack_loader.errors import build_error, result_complete, result_refused

from .constants import DEFAULT_BUNDLE_ID


BUNDLES_ROOT_REL = "bundles"
BUNDLE_MANIFEST_NAME = "bundle.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _rel(path: str, repo_root: str) -> str:
    return _norm(os.path.relpath(path, repo_root))


def _bundle_path(repo_root: str, bundle_id: str, bundles_root_rel: str = BUNDLES_ROOT_REL) -> str:
    return os.path.join(repo_root, bundles_root_rel, str(bundle_id), BUNDLE_MANIFEST_NAME)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def discover_bundle_files(repo_root: str, bundles_root_rel: str = BUNDLES_ROOT_REL) -> List[str]:
    root = os.path.join(repo_root, bundles_root_rel)
    if not os.path.isdir(root):
        return []
    files: List[str] = []
    for walk_root, _dirs, names in os.walk(root):
        for name in sorted(names):
            if name != BUNDLE_MANIFEST_NAME:
                continue
            files.append(os.path.join(walk_root, name))
    return sorted(files)


def _validate_bundle_payload(repo_root: str, payload: dict, schema_repo_root: str = "") -> Dict[str, object]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    errors: List[Dict[str, str]] = []
    validation = validate_instance(
        repo_root=schema_root,
        schema_name="bundle_profile",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(validation.get("valid", False)):
        for row in validation.get("errors", []):
            errors.append(
                build_error(
                    "refuse.bundle_profile.schema_invalid",
                    str(row.get("message", "")),
                    str(row.get("path", "$")),
                )
            )
        return result_refused({}, errors)

    bundle_id = str(payload.get("bundle_id", "")).strip()
    pack_ids = sorted(set(str(item).strip() for item in (payload.get("pack_ids") or []) if str(item).strip()))
    optional_pack_ids = sorted(
        set(str(item).strip() for item in (payload.get("optional_pack_ids") or []) if str(item).strip())
    )
    if not bundle_id:
        errors.append(build_error("refuse.bundle_profile.missing_bundle_id", "bundle_id must be non-empty", "$.bundle_id"))
    if not pack_ids:
        errors.append(build_error("refuse.bundle_profile.empty_pack_ids", "pack_ids must include at least one pack_id", "$.pack_ids"))
    if errors:
        return result_refused({}, errors)

    return result_complete(
        {
            "bundle_id": bundle_id,
            "description": str(payload.get("description", "")),
            "pack_ids": pack_ids,
            "optional_pack_ids": optional_pack_ids,
            "payload": payload,
        }
    )


def validate_bundle_file(repo_root: str, bundle_file_path: str, schema_repo_root: str = "") -> Dict[str, object]:
    abs_path = os.path.normpath(os.path.abspath(bundle_file_path))
    payload, error = _read_json(abs_path)
    if error:
        return result_refused(
            {},
            [
                build_error(
                    "refuse.bundle_profile.invalid_json",
                    "unable to parse bundle file '{}'".format(_rel(abs_path, repo_root)),
                    "$",
                )
            ],
        )
    valid = _validate_bundle_payload(repo_root=repo_root, payload=payload, schema_repo_root=schema_repo_root)
    if valid.get("result") != "complete":
        return valid
    normalized = dict(valid)
    normalized["bundle_path"] = _rel(abs_path, repo_root)
    return normalized


def load_bundle_profile(
    repo_root: str,
    bundle_id: str,
    schema_repo_root: str = "",
    bundles_root_rel: str = BUNDLES_ROOT_REL,
) -> Dict[str, object]:
    token = str(bundle_id or "").strip() or DEFAULT_BUNDLE_ID
    path = _bundle_path(repo_root, token, bundles_root_rel=bundles_root_rel)
    if not os.path.isfile(path):
        return result_refused(
            {},
            [
                build_error(
                    "refuse.bundle_profile.missing_bundle",
                    "bundle '{}' not found at '{}'".format(token, _rel(path, repo_root)),
                    "$.bundle_id",
                )
            ],
        )
    validated = validate_bundle_file(repo_root=repo_root, bundle_file_path=path, schema_repo_root=schema_repo_root)
    if validated.get("result") != "complete":
        return validated

    declared = str(validated.get("bundle_id", "")).strip()
    if declared != token:
        return result_refused(
            {},
            [
                build_error(
                    "refuse.bundle_profile.bundle_id_path_mismatch",
                    "bundle_id '{}' does not match requested '{}'".format(declared, token),
                    "$.bundle_id",
                )
            ],
        )
    return validated


def load_bundle_profiles(
    repo_root: str,
    schema_repo_root: str = "",
    bundles_root_rel: str = BUNDLES_ROOT_REL,
) -> Dict[str, object]:
    files = discover_bundle_files(repo_root=repo_root, bundles_root_rel=bundles_root_rel)
    bundles: List[dict] = []
    errors: List[Dict[str, str]] = []
    seen: Dict[str, str] = {}
    for path in files:
        item = validate_bundle_file(repo_root=repo_root, bundle_file_path=path, schema_repo_root=schema_repo_root)
        if item.get("result") != "complete":
            errors.extend(item.get("errors") or [])
            continue
        bundle_id = str(item.get("bundle_id", ""))
        existing = seen.get(bundle_id)
        if existing:
            errors.append(
                build_error(
                    "refuse.bundle_profile.duplicate_bundle_id",
                    "duplicate bundle_id '{}' at '{}' and '{}'".format(
                        bundle_id,
                        existing,
                        str(item.get("bundle_path", "")),
                    ),
                    "$.bundle_id",
                )
            )
            continue
        seen[bundle_id] = str(item.get("bundle_path", ""))
        bundles.append(
            {
                "bundle_id": bundle_id,
                "description": str(item.get("description", "")),
                "pack_ids": list(item.get("pack_ids") or []),
                "optional_pack_ids": list(item.get("optional_pack_ids") or []),
                "bundle_path": str(item.get("bundle_path", "")),
            }
        )
    if errors:
        return result_refused({"bundle_count": len(bundles), "bundles": bundles}, errors)
    return result_complete(
        {
            "bundle_count": len(bundles),
            "bundles": sorted(bundles, key=lambda row: str(row.get("bundle_id", ""))),
        }
    )


def resolve_bundle_selection(
    bundle_id: str,
    packs: List[dict],
    repo_root: str,
    schema_repo_root: str = "",
) -> Dict[str, object]:
    loaded = load_bundle_profile(repo_root=repo_root, bundle_id=bundle_id, schema_repo_root=schema_repo_root)
    if loaded.get("result") != "complete":
        return loaded

    packs_by_id = {
        str(row.get("pack_id", "")).strip(): row
        for row in sorted(packs or [], key=lambda item: str(item.get("pack_id", "")))
        if str(row.get("pack_id", "")).strip()
    }
    required_pack_ids = list(loaded.get("pack_ids") or [])
    optional_pack_ids = list(loaded.get("optional_pack_ids") or [])
    errors: List[Dict[str, str]] = []
    optional_missing: List[str] = []

    selected = []
    for pack_id in required_pack_ids:
        if pack_id not in packs_by_id:
            errors.append(
                build_error(
                    "refuse.bundle_profile.required_pack_missing",
                    "bundle '{}' references missing required pack '{}'".format(
                        str(loaded.get("bundle_id", "")),
                        pack_id,
                    ),
                    "$.pack_ids",
                )
            )
            continue
        selected.append(pack_id)

    for pack_id in optional_pack_ids:
        if pack_id in packs_by_id:
            selected.append(pack_id)
        else:
            optional_missing.append(pack_id)

    if errors:
        return result_refused({}, errors)

    selected_pack_ids = sorted(set(selected))
    if not selected_pack_ids:
        return result_refused(
            {},
            [
                build_error(
                    "refuse.bundle_profile.empty_selection",
                    "bundle '{}' resolved to an empty pack selection".format(str(loaded.get("bundle_id", ""))),
                    "$.pack_ids",
                )
            ],
        )

    return result_complete(
        {
            "bundle_id": str(loaded.get("bundle_id", "")),
            "bundle_path": str(loaded.get("bundle_path", "")),
            "selected_pack_ids": selected_pack_ids,
            "required_pack_ids": required_pack_ids,
            "optional_pack_ids": optional_pack_ids,
            "optional_missing_pack_ids": sorted(optional_missing),
            "selection_strategy": "bundle_profile_v1",
        }
    )

