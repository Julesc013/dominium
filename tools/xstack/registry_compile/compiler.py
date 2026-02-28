"""Deterministic registry compile pipeline with cache and lockfile emission."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Dict, List, Tuple

from tools.xstack.cache_store import build_cache_key, cache_hit, restore_cache_entry, store_cache_entry
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.pack_contrib.parser import parse_contributions
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.sessionx.universe_physics import write_null_boot_artifacts

from .bundle_profile import resolve_bundle_selection
from .constants import (
    COMPILER_VERSION,
    DEFAULT_BUNDLE_ID,
    DEFAULT_COMPATIBILITY_VERSION,
    DEFAULT_LOCKFILE_OUT_REL,
    DEFAULT_REGISTRY_OUT_DIR_REL,
    REGISTRY_FORMAT_VERSION,
    REGISTRY_OUTPUT_FILENAMES,
)
from .lockfile import compute_pack_lock_hash, validate_lockfile_payload


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _refusal(code: str, message: str, path: str = "$") -> Dict[str, object]:
    return {
        "result": "refused",
        "errors": [
            {
                "code": str(code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _generated_from_rows(ordered_packs: List[dict]) -> List[dict]:
    rows = []
    for row in ordered_packs:
        manifest = row.get("manifest") or {}
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "version": str(row.get("version", "")),
                "canonical_hash": str(manifest.get("canonical_hash", "")),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    return rows


def _payload_from_contribution(contrib: dict) -> Tuple[dict, str]:
    payload = contrib.get("payload")
    if not isinstance(payload, dict):
        return {}, "contribution payload must be object JSON"
    return payload, ""


def _normalize_search_key(value: object) -> str:
    token = str(value).strip().lower()
    if not token:
        return ""
    token = unicodedata.normalize("NFKD", token)
    token = token.encode("ascii", "ignore").decode("ascii")
    token = " ".join(token.split())
    return token


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _search_index(rows: List[dict], id_field: str) -> Dict[str, List[str]]:
    bucket: Dict[str, List[str]] = {}
    for row in rows:
        row_id = str(row.get(id_field, "")).strip()
        if not row_id:
            continue
        for key in row.get("search_keys") or []:
            normalized = _normalize_search_key(key)
            if not normalized:
                continue
            bucket.setdefault(normalized, []).append(row_id)
    out: Dict[str, List[str]] = {}
    for key in sorted(bucket.keys()):
        out[key] = sorted(set(str(item).strip() for item in bucket.get(key) or [] if str(item).strip()))
    return out


def _validate_schema_item(schema_root: str, schema_name: str, payload: dict, path: str) -> List[dict]:
    result = validate_instance(
        repo_root=schema_root,
        schema_name=schema_name,
        payload=payload,
        strict_top_level=True,
    )
    if bool(result.get("valid", False)):
        return []
    rows: List[dict] = []
    for err in result.get("errors") or []:
        if not isinstance(err, dict):
            continue
        rows.append(
            {
                "code": "refuse.registry_compile.invalid_{}".format(schema_name),
                "message": "{}: {}".format(path, str(err.get("message", ""))),
                "path": str(err.get("path", "$")),
            }
        )
    return rows


def _domain_rows(contrib: List[dict]) -> Tuple[List[dict], List[dict]]:
    rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "domain":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append({"code": "refuse.registry_compile.invalid_domain_payload", "message": err, "path": "$.domains"})
            continue
        domain_id = str(row.get("id", "")).strip()
        payload_domain_id = str(payload.get("domain_id", "")).strip()
        if not payload_domain_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_domain_id",
                    "message": "domain contribution '{}' missing payload field domain_id".format(domain_id),
                    "path": "$.domains",
                }
            )
            continue
        if payload_domain_id != domain_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.domain_id_mismatch",
                    "message": "domain payload domain_id '{}' does not match contribution id '{}'".format(
                        payload_domain_id,
                        domain_id,
                    ),
                    "path": "$.domains",
                }
            )
            continue
        rows.append(
            {
                "domain_id": domain_id,
                "pack_id": str(row.get("pack_id", "")),
                "path": str(row.get("path", "")),
                "declared_version": str(payload.get("version", "")).strip(),
            }
        )
    return sorted(rows, key=lambda item: (item["domain_id"], item["pack_id"])), errors


def _law_rows(contrib: List[dict]) -> Tuple[List[dict], List[dict]]:
    rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "law_profile":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append({"code": "refuse.registry_compile.invalid_law_payload", "message": err, "path": "$.law_profiles"})
            continue
        law_id = str(row.get("id", "")).strip()
        payload_law_id = str(payload.get("law_profile_id", "")).strip()
        if not payload_law_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_law_profile_id",
                    "message": "law contribution '{}' missing payload field law_profile_id".format(law_id),
                    "path": "$.law_profiles",
                }
            )
            continue
        if payload_law_id != law_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.law_profile_id_mismatch",
                    "message": "law payload id '{}' does not match contribution id '{}'".format(payload_law_id, law_id),
                    "path": "$.law_profiles",
                }
            )
            continue
        allowed_lenses = payload.get("allowed_lenses")
        if not isinstance(allowed_lenses, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_allowed_lenses",
                    "message": "law contribution '{}' missing allowed_lenses list".format(law_id),
                    "path": "$.law_profiles",
                }
            )
            continue
        epistemic_limits = payload.get("epistemic_limits")
        if not isinstance(epistemic_limits, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_epistemic_limits",
                    "message": "law contribution '{}' missing epistemic_limits object".format(law_id),
                    "path": "$.law_profiles",
                }
            )
            continue
        if "max_view_radius_km" not in epistemic_limits or "allow_hidden_state_access" not in epistemic_limits:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_epistemic_limits",
                    "message": "law contribution '{}' epistemic_limits missing required fields".format(law_id),
                    "path": "$.law_profiles",
                }
            )
            continue
        epistemic_policy_id = str(payload.get("epistemic_policy_id", "")).strip()
        if not epistemic_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_epistemic_policy_id",
                    "message": "law contribution '{}' missing epistemic_policy_id".format(law_id),
                    "path": "$.law_profiles.epistemic_policy_id",
                }
            )
            continue
        rows.append(
            {
                "law_profile_id": law_id,
                "epistemic_policy_id": epistemic_policy_id,
                "pack_id": str(row.get("pack_id", "")),
                "path": str(row.get("path", "")),
                "allowed_processes": sorted(
                    set(str(item).strip() for item in (payload.get("allowed_processes") or []) if str(item).strip())
                ),
                "forbidden_processes": sorted(
                    set(str(item).strip() for item in (payload.get("forbidden_processes") or []) if str(item).strip())
                ),
                "allowed_lenses": sorted(set(str(item).strip() for item in allowed_lenses if str(item).strip())),
                "epistemic_limits": {
                    "max_view_radius_km": epistemic_limits.get("max_view_radius_km"),
                    "allow_hidden_state_access": bool(epistemic_limits.get("allow_hidden_state_access", False)),
                },
                "process_entitlement_requirements": dict(payload.get("process_entitlement_requirements") or {}),
                "process_privilege_requirements": dict(payload.get("process_privilege_requirements") or {}),
                "debug_allowances": dict(payload.get("debug_allowances") or {}),
            }
        )
    return sorted(rows, key=lambda item: (item["law_profile_id"], item["pack_id"])), errors


def _experience_rows(contrib: List[dict]) -> Tuple[List[dict], List[dict]]:
    rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "experience_profile":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append(
                {"code": "refuse.registry_compile.invalid_experience_payload", "message": err, "path": "$.experience_profiles"}
            )
            continue
        if str(payload.get("schema_version", "")).strip() != "1.0.0":
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_experience_schema_version",
                    "message": "experience contribution '{}' missing schema_version=1.0.0".format(
                        str(row.get("id", ""))
                    ),
                    "path": "$.experience_profiles",
                }
            )
            continue
        experience_id = str(row.get("id", "")).strip()
        payload_id = str(payload.get("experience_id", "")).strip()
        if not payload_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_experience_id",
                    "message": "experience contribution '{}' missing payload field experience_id".format(experience_id),
                    "path": "$.experience_profiles",
                }
            )
            continue
        if payload_id != experience_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.experience_id_mismatch",
                    "message": "experience payload id '{}' does not match contribution id '{}'".format(
                        payload_id,
                        experience_id,
                    ),
                    "path": "$.experience_profiles",
                }
            )
            continue
        presentation_defaults = payload.get("presentation_defaults")
        if not isinstance(presentation_defaults, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_presentation_defaults",
                    "message": "experience contribution '{}' missing presentation_defaults object".format(experience_id),
                    "path": "$.experience_profiles",
                }
            )
            continue
        default_lens_id = str(presentation_defaults.get("default_lens_id", "")).strip()
        hud_layout_id = str(presentation_defaults.get("hud_layout_id", "")).strip()
        if not default_lens_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_default_lens_id",
                    "message": "experience contribution '{}' missing presentation_defaults.default_lens_id".format(
                        experience_id
                    ),
                    "path": "$.experience_profiles",
                }
            )
            continue
        if not hud_layout_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_hud_layout_id",
                    "message": "experience contribution '{}' missing presentation_defaults.hud_layout_id".format(
                        experience_id
                    ),
                    "path": "$.experience_profiles",
                }
            )
            continue
        allowed_lenses = payload.get("allowed_lenses")
        if not isinstance(allowed_lenses, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_allowed_lenses",
                    "message": "experience contribution '{}' missing allowed_lenses list".format(experience_id),
                    "path": "$.experience_profiles",
                }
            )
            continue
        suggested_parameter_bundles = payload.get("suggested_parameter_bundles")
        if not isinstance(suggested_parameter_bundles, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_suggested_parameter_bundles",
                    "message": "experience contribution '{}' missing suggested_parameter_bundles list".format(
                        experience_id
                    ),
                    "path": "$.experience_profiles",
                }
            )
            continue
        allowed_transitions = payload.get("allowed_transitions")
        if not isinstance(allowed_transitions, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_allowed_transitions",
                    "message": "experience contribution '{}' missing allowed_transitions list".format(experience_id),
                    "path": "$.experience_profiles",
                }
            )
            continue
        default_law_profile_id = str(payload.get("default_law_profile_id", "")).strip()
        if not default_law_profile_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_default_law_profile_id",
                    "message": "experience contribution '{}' missing default_law_profile_id".format(experience_id),
                    "path": "$.experience_profiles",
                }
            )
            continue
        rows.append(
            {
                "experience_id": experience_id,
                "pack_id": str(row.get("pack_id", "")),
                "path": str(row.get("path", "")),
                "default_lens_id": default_lens_id,
                "default_law_profile_id": default_law_profile_id,
                "presentation_defaults": {
                    "default_lens_id": default_lens_id,
                    "hud_layout_id": hud_layout_id,
                },
                "allowed_lenses": sorted(
                    set(str(item).strip() for item in allowed_lenses if str(item).strip())
                ),
                "suggested_parameter_bundles": sorted(
                    set(str(item).strip() for item in suggested_parameter_bundles if str(item).strip())
                ),
                "allowed_transitions": sorted(
                    set(str(item).strip() for item in allowed_transitions if str(item).strip())
                ),
            }
        )
    return sorted(rows, key=lambda item: (item["experience_id"], item["pack_id"])), errors


def _lens_rows(contrib: List[dict]) -> Tuple[List[dict], List[dict]]:
    rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "lens":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append({"code": "refuse.registry_compile.invalid_lens_payload", "message": err, "path": "$.lenses"})
            continue
        lens_id = str(row.get("id", "")).strip()
        payload_lens_id = str(payload.get("lens_id", "")).strip()
        if not payload_lens_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_lens_id",
                    "message": "lens contribution '{}' missing payload field lens_id".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        if payload_lens_id != lens_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.lens_id_mismatch",
                    "message": "lens payload id '{}' does not match contribution id '{}'".format(payload_lens_id, lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        lens_type = str(payload.get("lens_type", "")).strip()
        if lens_type not in ("diegetic", "nondiegetic"):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_lens_type",
                    "message": "lens contribution '{}' missing valid payload field lens_type".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        required_entitlements = payload.get("required_entitlements")
        if not isinstance(required_entitlements, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_required_entitlements",
                    "message": "lens contribution '{}' missing required_entitlements list".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        epistemic_constraints = payload.get("epistemic_constraints")
        if not isinstance(epistemic_constraints, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_epistemic_constraints",
                    "message": "lens contribution '{}' missing epistemic_constraints object".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        if "visibility_policy" not in epistemic_constraints or "max_resolution_tier" not in epistemic_constraints:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_epistemic_constraints",
                    "message": "lens contribution '{}' epistemic_constraints missing required fields".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        try:
            max_resolution_tier = int(epistemic_constraints.get("max_resolution_tier", 0) or 0)
        except (TypeError, ValueError):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_max_resolution_tier",
                    "message": "lens contribution '{}' has non-integer max_resolution_tier".format(lens_id),
                    "path": "$.lenses",
                }
            )
            continue
        rows.append(
            {
                "lens_id": lens_id,
                "lens_type": lens_type,
                "pack_id": str(row.get("pack_id", "")),
                "path": str(row.get("path", "")),
                "transform_description": str(payload.get("transform_description", "")).strip(),
                "required_entitlements": sorted(
                    set(str(item).strip() for item in required_entitlements if str(item).strip())
                ),
                "observation_channels": sorted(
                    set(str(item).strip() for item in (payload.get("observation_channels") or []) if str(item).strip())
                ),
                "epistemic_constraints": {
                    "visibility_policy": str(epistemic_constraints.get("visibility_policy", "")),
                    "max_resolution_tier": max_resolution_tier,
                },
            }
        )
    return sorted(rows, key=lambda item: (item["lens_id"], item["pack_id"])), errors


def _astronomy_rows(contrib: List[dict], schema_root: str) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    astronomy_rows: List[dict] = []
    frame_rows: List[dict] = []
    site_rows: List[dict] = []
    errors: List[dict] = []
    for row in contrib:
        contrib_type = str(row.get("contrib_type", ""))
        payload, err = _payload_from_contribution(row)
        if err:
            if contrib_type in ("assets", "domain", "registry_entries"):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_astronomy_source_payload",
                        "message": err,
                        "path": "$.entries",
                    }
                )
            continue

        pack_id = str(row.get("pack_id", "")).strip()
        contrib_path = str(row.get("path", "")).strip()

        if contrib_type in ("assets", "domain"):
            entries = payload.get("astronomy_entries", [])
            if entries is None:
                entries = []
            if not isinstance(entries, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_astronomy_entries_shape",
                        "message": "astronomy_entries must be list for contribution '{}'".format(str(row.get("id", ""))),
                        "path": "$.entries",
                    }
                )
                continue
            for item in entries:
                if not isinstance(item, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_astronomy_entry",
                            "message": "astronomy entry must be object in contribution '{}'".format(str(row.get("id", ""))),
                            "path": "$.entries",
                        }
                    )
                    continue
                object_id = str(item.get("object_id", "")).strip()
                kind = str(item.get("kind", "")).strip()
                search_keys = item.get("search_keys")
                if not object_id or not kind or not isinstance(search_keys, list):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.missing_astronomy_fields",
                            "message": "astronomy entry in contribution '{}' missing required fields".format(
                                str(row.get("id", ""))
                            ),
                            "path": "$.entries",
                        }
                    )
                    continue
                astronomy_rows.append(
                    {
                        "object_id": object_id,
                        "kind": kind,
                        "parent_id": None,
                        "frame_id": "frame.unknown",
                        "physical_params": {},
                        "bounds": {"kind": "sphere", "sphere_radius_mm": 0},
                        "pack_id": pack_id,
                        "path": contrib_path,
                        "search_keys": _sorted_unique_strings(search_keys),
                    }
                )
            continue

        if contrib_type != "registry_entries":
            continue

        entry_type = str(payload.get("entry_type", "")).strip()
        if entry_type == "astronomy_catalog_collection":
            entries = payload.get("entries")
            if not isinstance(entries, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_astronomy_entries_shape",
                        "message": "astronomy_catalog_collection requires entries[] in '{}'".format(contrib_path),
                        "path": "$.entries",
                    }
                )
                continue
            for idx, item in enumerate(entries):
                if not isinstance(item, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_astronomy_entry",
                            "message": "astronomy entry at index {} must be object in '{}'".format(idx, contrib_path),
                            "path": "$.entries[{}]".format(idx),
                        }
                    )
                    continue
                schema_errors = _validate_schema_item(
                    schema_root=schema_root,
                    schema_name="astronomy_catalog_entry",
                    payload=item,
                    path=contrib_path,
                )
                if schema_errors:
                    errors.extend(schema_errors)
                    continue
                payload_pack_id = str(item.get("pack_id", "")).strip()
                if payload_pack_id != pack_id:
                    errors.append(
                        {
                            "code": "refuse.registry_compile.astronomy_pack_id_mismatch",
                            "message": "astronomy object '{}' pack_id '{}' does not match contribution pack '{}'".format(
                                str(item.get("object_id", "")),
                                payload_pack_id,
                                pack_id,
                            ),
                            "path": "$.pack_id",
                        }
                    )
                    continue
                row_out = {
                    "object_id": str(item.get("object_id", "")).strip(),
                    "kind": str(item.get("kind", "")).strip(),
                    "parent_id": item.get("parent_id"),
                    "frame_id": str(item.get("frame_id", "")).strip(),
                    "physical_params": dict(item.get("physical_params") or {}),
                    "bounds": dict(item.get("bounds") or {}),
                    "pack_id": pack_id,
                    "path": contrib_path,
                    "search_keys": _sorted_unique_strings(item.get("search_keys") or []),
                }
                orbit_params = item.get("orbit_params")
                if isinstance(orbit_params, dict):
                    row_out["orbit_params"] = dict(orbit_params)
                astronomy_rows.append(row_out)
            continue

        if entry_type == "reference_frame_collection":
            frames = payload.get("frames")
            if not isinstance(frames, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_reference_frames_shape",
                        "message": "reference_frame_collection requires frames[] in '{}'".format(contrib_path),
                        "path": "$.frames",
                    }
                )
                continue
            for idx, item in enumerate(frames):
                if not isinstance(item, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_reference_frame",
                            "message": "reference frame at index {} must be object in '{}'".format(idx, contrib_path),
                            "path": "$.frames[{}]".format(idx),
                        }
                    )
                    continue
                schema_errors = _validate_schema_item(
                    schema_root=schema_root,
                    schema_name="reference_frame",
                    payload=item,
                    path=contrib_path,
                )
                if schema_errors:
                    errors.extend(schema_errors)
                    continue
                frame_rows.append(
                    {
                        "frame_id": str(item.get("frame_id", "")).strip(),
                        "parent_frame_id": item.get("parent_frame_id"),
                        "transform": dict(item.get("transform") or {}),
                        "semantics": str(item.get("semantics", "")).strip(),
                        "pack_id": pack_id,
                        "path": contrib_path,
                    }
                )
            continue

        if entry_type == "site_collection":
            sites = payload.get("sites")
            if not isinstance(sites, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_site_entries_shape",
                        "message": "site_collection requires sites[] in '{}'".format(contrib_path),
                        "path": "$.sites",
                    }
                )
                continue
            for idx, item in enumerate(sites):
                if not isinstance(item, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_site_entry",
                            "message": "site entry at index {} must be object in '{}'".format(idx, contrib_path),
                            "path": "$.sites[{}]".format(idx),
                        }
                    )
                    continue
                schema_errors = _validate_schema_item(
                    schema_root=schema_root,
                    schema_name="site_entry",
                    payload=item,
                    path=contrib_path,
                )
                if schema_errors:
                    errors.extend(schema_errors)
                    continue
                site_rows.append(
                    {
                        "site_id": str(item.get("site_id", "")).strip(),
                        "object_id": str(item.get("object_id", "")).strip(),
                        "kind": str(item.get("kind", "")).strip(),
                        "frame_id": str(item.get("frame_id", "")).strip(),
                        "position": dict(item.get("position") or {}),
                        "bounds": dict(item.get("bounds") or {}),
                        "search_keys": _sorted_unique_strings(item.get("search_keys") or []),
                        "tags": _sorted_unique_strings(item.get("tags") or []),
                        "pack_id": pack_id,
                        "path": contrib_path,
                    }
                )
            continue
    astronomy_rows = sorted(
        astronomy_rows,
        key=lambda item: (
            str(item.get("kind", "")),
            str(item.get("object_id", "")),
            str(item.get("pack_id", "")),
        ),
    )
    frame_rows = sorted(
        frame_rows,
        key=lambda item: (
            str(item.get("frame_id", "")),
            str(item.get("pack_id", "")),
        ),
    )
    site_rows = sorted(
        site_rows,
        key=lambda item: (
            str(item.get("object_id", "")),
            str(item.get("site_id", "")),
            str(item.get("pack_id", "")),
        ),
    )
    return astronomy_rows, frame_rows, site_rows, errors


def _real_data_rows(contrib: List[dict], schema_root: str) -> Tuple[List[dict], List[dict], List[dict]]:
    ephemeris_rows: List[dict] = []
    terrain_rows: List[dict] = []
    errors: List[dict] = []
    seen_body_ids: Dict[str, str] = {}
    seen_tile_ids: Dict[str, str] = {}

    def _as_int(value: object, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(default)

    for row in contrib:
        if str(row.get("contrib_type", "")) != "registry_entries":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_real_data_payload",
                    "message": err,
                    "path": "$.registry_entries",
                }
            )
            continue
        entry_type = str(payload.get("entry_type", "")).strip()
        if entry_type not in ("ephemeris_table_collection", "terrain_tile_pyramid"):
            continue

        contrib_path = str(row.get("path", "")).strip()
        pack_id = str(row.get("pack_id", "")).strip()
        provenance = payload.get("provenance")
        if not isinstance(provenance, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.missing_provenance",
                    "message": "derived payload '{}' is missing provenance object".format(contrib_path),
                    "path": "$.provenance",
                }
            )
            continue
        provenance_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="derived_provenance",
            payload=provenance,
            path=contrib_path,
        )
        if provenance_errors:
            errors.extend(provenance_errors)
            continue

        if entry_type == "ephemeris_table_collection":
            tables = payload.get("tables")
            if not isinstance(tables, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_ephemeris_tables_shape",
                        "message": "ephemeris_table_collection requires tables[] in '{}'".format(contrib_path),
                        "path": "$.tables",
                    }
                )
                continue
            source_id = str(payload.get("source_id", "")).strip()
            reference_frame = str(payload.get("reference_frame", "")).strip()
            time_range = payload.get("time_range")
            if not source_id or not reference_frame or not isinstance(time_range, dict):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_ephemeris_header",
                        "message": "ephemeris_table_collection in '{}' missing source_id/reference_frame/time_range".format(
                            contrib_path
                        ),
                        "path": "$",
                    }
                )
                continue
            normalized_time_range = {
                "start_tick": _as_int(time_range.get("start_tick", 0), 0),
                "end_tick": _as_int(time_range.get("end_tick", 0), 0),
                "step_ticks": max(1, _as_int(time_range.get("step_ticks", 1), 1)),
            }
            for idx, item in enumerate(tables):
                if not isinstance(item, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_ephemeris_table",
                            "message": "ephemeris table entry at index {} must be object in '{}'".format(idx, contrib_path),
                            "path": "$.tables[{}]".format(idx),
                        }
                    )
                    continue
                body_id = str(item.get("body_id", "")).strip()
                samples = item.get("samples")
                if not body_id or not isinstance(samples, list):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_ephemeris_table_fields",
                            "message": "ephemeris table '{}' missing body_id or samples[] in '{}'".format(
                                body_id or "<missing>",
                                contrib_path,
                            ),
                            "path": "$.tables[{}]".format(idx),
                        }
                    )
                    continue
                prior = seen_body_ids.get(body_id)
                if prior:
                    errors.append(
                        {
                            "code": "refuse.registry_compile.duplicate_ephemeris_body",
                            "message": "duplicate ephemeris body_id '{}' in '{}' and '{}'".format(
                                body_id,
                                prior,
                                contrib_path,
                            ),
                            "path": "$.tables[{}].body_id".format(idx),
                        }
                    )
                    continue
                sample_rows: List[dict] = []
                for sample_idx, sample in enumerate(samples):
                    if not isinstance(sample, dict):
                        errors.append(
                            {
                                "code": "refuse.registry_compile.invalid_ephemeris_sample",
                                "message": "ephemeris sample at index {} must be object for '{}'".format(
                                    sample_idx,
                                    body_id,
                                ),
                                "path": "$.tables[{}].samples[{}]".format(idx, sample_idx),
                            }
                        )
                        continue
                    position = sample.get("position_mm")
                    if not isinstance(position, dict):
                        errors.append(
                            {
                                "code": "refuse.registry_compile.invalid_ephemeris_sample_position",
                                "message": "ephemeris sample for '{}' is missing position_mm object".format(body_id),
                                "path": "$.tables[{}].samples[{}].position_mm".format(idx, sample_idx),
                            }
                        )
                        continue
                    sample_rows.append(
                        {
                            "tick": _as_int(sample.get("tick", 0), 0),
                            "position_mm": {
                                "x": _as_int(position.get("x", 0), 0),
                                "y": _as_int(position.get("y", 0), 0),
                                "z": _as_int(position.get("z", 0), 0),
                            },
                        }
                    )
                sample_rows = sorted(sample_rows, key=lambda item: int(item.get("tick", 0)))
                seen_body_ids[body_id] = contrib_path
                ephemeris_rows.append(
                    {
                        "body_id": body_id,
                        "reference_frame": reference_frame,
                        "source_id": source_id,
                        "time_range": normalized_time_range,
                        "samples": sample_rows,
                        "pack_id": pack_id,
                        "path": contrib_path,
                        "provenance": dict(provenance),
                    }
                )
            continue

        levels = payload.get("levels")
        if not isinstance(levels, list):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_terrain_levels_shape",
                    "message": "terrain_tile_pyramid requires levels[] in '{}'".format(contrib_path),
                    "path": "$.levels",
                }
            )
            continue
        source_id = str(payload.get("source_id", "")).strip()
        if not source_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_terrain_source_id",
                    "message": "terrain_tile_pyramid in '{}' missing source_id".format(contrib_path),
                    "path": "$.source_id",
                }
            )
            continue
        for level_idx, level in enumerate(levels):
            if not isinstance(level, dict):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_terrain_level",
                        "message": "terrain level at index {} must be object in '{}'".format(level_idx, contrib_path),
                        "path": "$.levels[{}]".format(level_idx),
                    }
                )
                continue
            tiles = level.get("tiles")
            if not isinstance(tiles, list):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_terrain_tiles",
                        "message": "terrain level at index {} must provide tiles[] in '{}'".format(level_idx, contrib_path),
                        "path": "$.levels[{}].tiles".format(level_idx),
                    }
                )
                continue
            for tile_idx, tile in enumerate(tiles):
                if not isinstance(tile, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_terrain_tile",
                            "message": "terrain tile at index {} must be object in '{}'".format(tile_idx, contrib_path),
                            "path": "$.levels[{}].tiles[{}]".format(level_idx, tile_idx),
                        }
                    )
                    continue
                tile_id = str(tile.get("tile_id", "")).strip()
                if not tile_id:
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_terrain_tile_id",
                            "message": "terrain tile at index {} is missing tile_id in '{}'".format(tile_idx, contrib_path),
                            "path": "$.levels[{}].tiles[{}].tile_id".format(level_idx, tile_idx),
                        }
                    )
                    continue
                prior = seen_tile_ids.get(tile_id)
                if prior:
                    errors.append(
                        {
                            "code": "refuse.registry_compile.duplicate_terrain_tile_id",
                            "message": "duplicate terrain tile_id '{}' in '{}' and '{}'".format(
                                tile_id,
                                prior,
                                contrib_path,
                            ),
                            "path": "$.levels[{}].tiles[{}].tile_id".format(level_idx, tile_idx),
                        }
                    )
                    continue
                stats = tile.get("stats")
                if not isinstance(stats, dict):
                    errors.append(
                        {
                            "code": "refuse.registry_compile.invalid_terrain_tile_stats",
                            "message": "terrain tile '{}' missing stats object".format(tile_id),
                            "path": "$.levels[{}].tiles[{}].stats".format(level_idx, tile_idx),
                        }
                    )
                    continue
                seen_tile_ids[tile_id] = contrib_path
                terrain_rows.append(
                    {
                        "tile_id": tile_id,
                        "z": _as_int(tile.get("z", level.get("z", 0)), 0),
                        "x": _as_int(tile.get("x", 0), 0),
                        "y": _as_int(tile.get("y", 0), 0),
                        "source_id": source_id,
                        "stats": {
                            "sample_count": max(0, _as_int(stats.get("sample_count", 0), 0)),
                            "min_height_mm": _as_int(stats.get("min_height_mm", 0), 0),
                            "max_height_mm": _as_int(stats.get("max_height_mm", 0), 0),
                            "mean_height_mm": _as_int(stats.get("mean_height_mm", 0), 0),
                        },
                        "children": _sorted_unique_strings(tile.get("children") or []),
                        "pack_id": pack_id,
                        "path": contrib_path,
                        "provenance": dict(provenance),
                    }
                )

    ephemeris_rows = sorted(ephemeris_rows, key=lambda item: (str(item.get("body_id", "")), str(item.get("pack_id", ""))))
    terrain_rows = sorted(
        terrain_rows,
        key=lambda item: (
            _as_int(item.get("z", 0), 0),
            _as_int(item.get("x", 0), 0),
            _as_int(item.get("y", 0), 0),
            str(item.get("tile_id", "")),
        ),
    )
    return ephemeris_rows, terrain_rows, errors


def _policy_rows(contrib: List[dict], schema_root: str) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    activation_rows = []
    budget_rows = []
    fidelity_rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "registry_entries":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_policy_payload",
                    "message": err,
                    "path": "$.policy",
                }
            )
            continue
        entry_type = str(payload.get("entry_type", "")).strip()
        if entry_type not in ("activation_policy", "budget_policy", "fidelity_policy"):
            continue

        policy_payload = payload.get("policy")
        if not isinstance(policy_payload, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_policy_shape",
                    "message": "policy contribution '{}' must include object field policy".format(str(row.get("id", ""))),
                    "path": "$.policy",
                }
            )
            continue
        schema_name = entry_type
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name=schema_name,
            payload=policy_payload,
            path=str(row.get("path", "")),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        policy_id = str(policy_payload.get("policy_id", "")).strip()
        contribution_id = str(row.get("id", "")).strip()
        if policy_id != contribution_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.policy_id_mismatch",
                    "message": "policy payload id '{}' does not match contribution id '{}'".format(
                        policy_id,
                        contribution_id,
                    ),
                    "path": "$.policy.policy_id",
                }
            )
            continue
        pack_id = str(row.get("pack_id", "")).strip()
        path = str(row.get("path", "")).strip()
        if entry_type == "activation_policy":
            activation_rows.append(
                {
                    "policy_id": policy_id,
                    "pack_id": pack_id,
                    "path": path,
                    "interest_radius_rules": list(policy_payload.get("interest_radius_rules") or []),
                    "activation_thresholds": dict(policy_payload.get("activation_thresholds") or {}),
                    "hysteresis": dict(policy_payload.get("hysteresis") or {}),
                    "deterministic_inputs": _sorted_unique_strings(policy_payload.get("deterministic_inputs") or []),
                }
            )
            continue
        if entry_type == "budget_policy":
            budget_rows.append(
                {
                    "policy_id": policy_id,
                    "activation_policy_id": str(policy_payload.get("activation_policy_id", "")).strip(),
                    "pack_id": pack_id,
                    "path": path,
                    "max_compute_units_per_tick": int(policy_payload.get("max_compute_units_per_tick", 0) or 0),
                    "max_entities_micro": int(policy_payload.get("max_entities_micro", 0) or 0),
                    "max_regions_micro": int(policy_payload.get("max_regions_micro", 0) or 0),
                    "fallback_behavior": str(policy_payload.get("fallback_behavior", "")).strip(),
                    "logging_level": int(policy_payload.get("logging_level", 0) or 0),
                    "tier_compute_weights": dict(policy_payload.get("tier_compute_weights") or {}),
                    "entity_compute_weight": int(policy_payload.get("entity_compute_weight", 0) or 0),
                }
            )
            continue
        fidelity_rows.append(
            {
                "policy_id": policy_id,
                "pack_id": pack_id,
                "path": path,
                "tiers": list(policy_payload.get("tiers") or []),
                "switching_rules": dict(policy_payload.get("switching_rules") or {}),
                "minimum_tier_by_kind": dict(policy_payload.get("minimum_tier_by_kind") or {}),
            }
        )

    activation_rows = sorted(activation_rows, key=lambda item: (str(item.get("policy_id", "")), str(item.get("pack_id", ""))))
    budget_rows = sorted(budget_rows, key=lambda item: (str(item.get("policy_id", "")), str(item.get("pack_id", ""))))
    fidelity_rows = sorted(fidelity_rows, key=lambda item: (str(item.get("policy_id", "")), str(item.get("pack_id", ""))))
    return activation_rows, budget_rows, fidelity_rows, errors


def _worldgen_constraints_rows(contrib: List[dict], schema_root: str) -> Tuple[List[dict], List[dict]]:
    rows: List[dict] = []
    errors: List[dict] = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "worldgen_constraints":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_worldgen_constraints_payload",
                    "message": err,
                    "path": "$.worldgen_constraints",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="worldgen_constraints",
            payload=payload,
            path=str(row.get("path", "")),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        constraints_id = str(payload.get("constraints_id", "")).strip()
        contribution_id = str(row.get("id", "")).strip()
        if constraints_id != contribution_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.worldgen_constraints_id_mismatch",
                    "message": "constraints payload id '{}' does not match contribution id '{}'".format(
                        constraints_id,
                        contribution_id,
                    ),
                    "path": "$.worldgen_constraints.constraints_id",
                }
            )
            continue

        extensions = payload.get("extensions")
        if not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.worldgen_constraints_extensions_missing",
                    "message": "worldgen constraints '{}' must include extensions object with description/status".format(
                        constraints_id
                    ),
                    "path": "$.worldgen_constraints.extensions",
                }
            )
            continue
        description = str(extensions.get("description", "")).strip()
        status = str(extensions.get("status", "")).strip()
        if not description:
            errors.append(
                {
                    "code": "refuse.registry_compile.worldgen_constraints_description_missing",
                    "message": "worldgen constraints '{}' must declare extensions.description".format(constraints_id),
                    "path": "$.worldgen_constraints.extensions.description",
                }
            )
            continue
        if status not in ("active", "experimental", "deprecated"):
            errors.append(
                {
                    "code": "refuse.registry_compile.worldgen_constraints_status_invalid",
                    "message": "worldgen constraints '{}' must declare extensions.status as active|experimental|deprecated".format(
                        constraints_id
                    ),
                    "path": "$.worldgen_constraints.extensions.status",
                }
            )
            continue

        rows.append(
            {
                "constraints_id": constraints_id,
                "description": description,
                "pack_id": str(row.get("pack_id", "")).strip(),
                "status": status,
                "path": str(row.get("path", "")).strip(),
                "deterministic_seed_policy": str(payload.get("deterministic_seed_policy", "")).strip(),
                "candidate_count": int(payload.get("candidate_count", 0) or 0),
                "tie_break_policy": str(payload.get("tie_break_policy", "")).strip(),
                "refusal_codes": _sorted_unique_strings(payload.get("refusal_codes") or []),
            }
        )

    rows = sorted(rows, key=lambda item: (str(item.get("constraints_id", "")), str(item.get("pack_id", ""))))
    return rows, errors


def _read_json_payload(path: str) -> Tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "payload root must be object json"
    return payload, ""


def _load_registry_record(
    repo_root: str,
    registry_rel_path: str,
    expected_schema_id: str,
    expected_schema_version: str,
    expected_entry_key: str,
) -> Tuple[dict, List[dict], List[dict]]:
    abs_path = os.path.join(repo_root, registry_rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {}, [], [
            {
                "code": "refuse.registry_compile.source_registry_missing",
                "message": "required source registry '{}' is missing".format(_norm(registry_rel_path)),
                "path": "$.{}".format(expected_entry_key),
            }
        ]

    payload, payload_err = _read_json_payload(abs_path)
    if payload_err:
        return {}, [], [
            {
                "code": "refuse.registry_compile.invalid_source_registry_payload",
                "message": "failed to parse source registry '{}': {}".format(_norm(registry_rel_path), payload_err),
                "path": "$",
            }
        ]

    schema_id = str(payload.get("schema_id", "")).strip()
    if schema_id != str(expected_schema_id):
        return {}, [], [
            {
                "code": "refuse.registry_compile.source_registry_schema_id_mismatch",
                "message": "source registry '{}' schema_id '{}' does not match '{}'".format(
                    _norm(registry_rel_path),
                    schema_id,
                    expected_schema_id,
                ),
                "path": "$.schema_id",
            }
        ]

    schema_version = str(payload.get("schema_version", "")).strip()
    if schema_version != str(expected_schema_version):
        return {}, [], [
            {
                "code": "refuse.registry_compile.source_registry_schema_version_mismatch",
                "message": "source registry '{}' schema_version '{}' does not match '{}'".format(
                    _norm(registry_rel_path),
                    schema_version,
                    expected_schema_version,
                ),
                "path": "$.schema_version",
            }
        ]

    record = payload.get("record")
    if not isinstance(record, dict):
        return {}, [], [
            {
                "code": "refuse.registry_compile.source_registry_record_missing",
                "message": "source registry '{}' missing object field record".format(_norm(registry_rel_path)),
                "path": "$.record",
            }
        ]

    rows = record.get(expected_entry_key)
    if not isinstance(rows, list):
        return {}, [], [
            {
                "code": "refuse.registry_compile.source_registry_entries_invalid",
                "message": "source registry '{}' missing list field record.{}".format(
                    _norm(registry_rel_path),
                    expected_entry_key,
                ),
                "path": "$.record.{}".format(expected_entry_key),
            }
        ]
    return record, list(rows), []


def _control_registry_rows(
    repo_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _action_record, action_rows_raw, action_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/control_action_registry.json",
        expected_schema_id="dominium.registry.control_action_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="actions",
    )
    if action_load_errors:
        return [], [], action_load_errors

    control_action_rows: List[dict] = []
    action_id_set = set()
    for entry in sorted(action_rows_raw, key=lambda row: str((row or {}).get("action_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_control_action_entry",
                    "message": "control action entry must be object",
                    "path": "$.actions",
                }
            )
            continue
        action_id = str(entry.get("action_id", "")).strip()
        required_entitlements = entry.get("required_entitlements")
        extensions = entry.get("extensions")
        if (
            not action_id
            or not isinstance(required_entitlements, list)
            or not str(entry.get("produces_intent_id", "")).strip()
            or not str(entry.get("payload_schema_id", "")).strip()
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_control_action_entry",
                    "message": "control action entry missing required fields",
                    "path": "$.actions",
                }
            )
            continue
        if action_id in action_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_control_action_id",
                    "message": "duplicate control action_id '{}'".format(action_id),
                    "path": "$.actions.action_id",
                }
            )
            continue
        action_id_set.add(action_id)
        control_action_rows.append(
            {
                "action_id": action_id,
                "description": str(entry.get("description", "")).strip(),
                "required_entitlements": _sorted_unique_strings(required_entitlements),
                "produces_intent_id": str(entry.get("produces_intent_id", "")).strip(),
                "payload_schema_id": str(entry.get("payload_schema_id", "")).strip(),
                "extensions": dict(extensions),
            }
        )
    control_action_rows = sorted(control_action_rows, key=lambda row: str(row.get("action_id", "")))

    _controller_record, controller_rows_raw, controller_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/controller_type_registry.json",
        expected_schema_id="dominium.registry.controller_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="controller_types",
    )
    if controller_load_errors:
        return [], [], controller_load_errors

    controller_type_rows: List[dict] = []
    controller_type_set = set()
    for entry in sorted(controller_rows_raw, key=lambda row: str((row or {}).get("controller_type", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_controller_type_entry",
                    "message": "controller type entry must be object",
                    "path": "$.controller_types",
                }
            )
            continue
        controller_type = str(entry.get("controller_type", "")).strip()
        allowed_actions = entry.get("allowed_actions")
        default_bindings = entry.get("default_bindings")
        extensions = entry.get("extensions")
        if (
            not controller_type
            or not isinstance(allowed_actions, list)
            or not isinstance(default_bindings, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_controller_type_entry",
                    "message": "controller type entry missing required fields",
                    "path": "$.controller_types",
                }
            )
            continue
        if controller_type in controller_type_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_controller_type",
                    "message": "duplicate controller_type '{}'".format(controller_type),
                    "path": "$.controller_types.controller_type",
                }
            )
            continue
        action_tokens = _sorted_unique_strings(allowed_actions)
        unknown_actions = [token for token in action_tokens if token not in action_id_set]
        if unknown_actions:
            errors.append(
                {
                    "code": "refuse.registry_compile.controller_type_action_missing",
                    "message": "controller type '{}' references unknown control actions: {}".format(
                        controller_type,
                        ",".join(sorted(unknown_actions)),
                    ),
                    "path": "$.controller_types.allowed_actions",
                }
            )
            continue
        controller_type_set.add(controller_type)
        controller_type_rows.append(
            {
                "controller_type": controller_type,
                "description": str(entry.get("description", "")).strip(),
                "allowed_actions": action_tokens,
                "default_bindings": _sorted_unique_strings(default_bindings),
                "extensions": dict(extensions),
            }
        )
    controller_type_rows = sorted(controller_type_rows, key=lambda row: str(row.get("controller_type", "")))
    return control_action_rows, controller_type_rows, errors


def _interaction_registry_rows(
    repo_root: str,
) -> Tuple[List[dict], List[dict]]:
    _record, action_rows_raw, load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/interaction_action_registry.json",
        expected_schema_id="dominium.registry.interaction_action_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="actions",
    )
    if load_errors:
        return [], load_errors

    errors: List[dict] = []
    action_rows: List[dict] = []
    action_seen = set()
    allowed_target_kinds = {
        "agent",
        "cohort",
        "faction",
        "territory",
        "blueprint",
        "logistics_node",
        "manifest",
        "shipment_commitment",
        "construction_project",
        "installed_structure",
        "micro_part",
        "materialization_state",
        "distribution_aggregate",
        "provenance_event",
        "asset_health",
        "failure_event",
        "maintenance_commitment",
        "commitment",
        "event_stream",
        "reenactment_request",
        "reenactment_artifact",
    }
    allowed_preview_modes = {"none", "cheap", "expensive"}
    for entry in sorted(action_rows_raw, key=lambda row: str((row or {}).get("action_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_interaction_action_entry",
                    "message": "interaction action entry must be object",
                    "path": "$.actions",
                }
            )
            continue
        action_id = str(entry.get("action_id", "")).strip()
        process_id = str(entry.get("process_id", "")).strip()
        display_name = str(entry.get("display_name", "")).strip()
        target_kinds = entry.get("target_kinds")
        preview_mode = str(entry.get("preview_mode", "")).strip()
        required_lens_channels = entry.get("required_lens_channels")
        default_ui_hints = entry.get("default_ui_hints")
        extensions = entry.get("extensions")
        parameter_schema_id = entry.get("parameter_schema_id")
        if (
            not action_id
            or not process_id
            or not display_name
            or not isinstance(target_kinds, list)
            or preview_mode not in allowed_preview_modes
            or not isinstance(required_lens_channels, list)
            or not isinstance(default_ui_hints, dict)
            or not isinstance(extensions, dict)
            or (parameter_schema_id is not None and not isinstance(parameter_schema_id, str))
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_interaction_action_entry",
                    "message": "interaction action '{}' missing required fields".format(action_id or "<missing>"),
                    "path": "$.actions",
                }
            )
            continue
        if action_id in action_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_interaction_action_id",
                    "message": "duplicate interaction action_id '{}'".format(action_id),
                    "path": "$.actions.action_id",
                }
            )
            continue
        normalized_target_kinds = _sorted_unique_strings(target_kinds)
        if not normalized_target_kinds or any(token not in allowed_target_kinds for token in normalized_target_kinds):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_interaction_action_targets",
                    "message": "interaction action '{}' has invalid target_kinds".format(action_id),
                    "path": "$.actions.target_kinds",
                }
            )
            continue
        action_seen.add(action_id)
        action_rows.append(
            {
                "action_id": action_id,
                "process_id": process_id,
                "display_name": display_name,
                "target_kinds": normalized_target_kinds,
                "parameter_schema_id": str(parameter_schema_id).strip() if isinstance(parameter_schema_id, str) else None,
                "preview_mode": preview_mode,
                "default_ui_hints": dict((str(key), default_ui_hints[key]) for key in sorted(default_ui_hints.keys())),
                "required_lens_channels": _sorted_unique_strings(required_lens_channels),
                "extensions": dict(extensions),
            }
        )
    action_rows = sorted(action_rows, key=lambda row: str(row.get("action_id", "")))
    return action_rows, errors


def _action_surface_registry_rows(
    repo_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _surface_type_record, surface_type_rows_raw, surface_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/surface_type_registry.json",
        expected_schema_id="dominium.registry.surface_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="surface_types",
    )
    if surface_type_load_errors:
        return [], [], [], surface_type_load_errors

    surface_type_rows: List[dict] = []
    surface_type_seen = set()
    for entry in sorted(surface_type_rows_raw, key=lambda row: str((row or {}).get("surface_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_surface_type_entry",
                    "message": "surface type entry must be object",
                    "path": "$.surface_types",
                }
            )
            continue
        surface_type_id = str(entry.get("surface_type_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        default_icon_tag = entry.get("default_icon_tag")
        extensions = entry.get("extensions")
        if (
            (not surface_type_id)
            or (not description)
            or (default_icon_tag is not None and not isinstance(default_icon_tag, str))
            or (not isinstance(extensions, dict))
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_surface_type_entry",
                    "message": "surface type entry missing required fields",
                    "path": "$.surface_types",
                }
            )
            continue
        if surface_type_id in surface_type_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_surface_type_id",
                    "message": "duplicate surface_type_id '{}'".format(surface_type_id),
                    "path": "$.surface_types.surface_type_id",
                }
            )
            continue
        surface_type_seen.add(surface_type_id)
        surface_type_rows.append(
            {
                "schema_version": "1.0.0",
                "surface_type_id": surface_type_id,
                "description": description,
                "default_icon_tag": str(default_icon_tag).strip() if isinstance(default_icon_tag, str) else None,
                "extensions": dict(extensions),
            }
        )
    surface_type_rows = sorted(surface_type_rows, key=lambda row: str(row.get("surface_type_id", "")))

    _tool_tag_record, tool_tag_rows_raw, tool_tag_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/tool_tag_registry.json",
        expected_schema_id="dominium.registry.tool_tag_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="tool_tags",
    )
    if tool_tag_load_errors:
        return [], [], [], tool_tag_load_errors

    tool_tag_rows: List[dict] = []
    tool_tag_seen = set()
    for entry in sorted(tool_tag_rows_raw, key=lambda row: str((row or {}).get("tool_tag_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_tool_tag_entry",
                    "message": "tool tag entry must be object",
                    "path": "$.tool_tags",
                }
            )
            continue
        tool_tag_id = str(entry.get("tool_tag_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        extensions = entry.get("extensions")
        if (not tool_tag_id) or (not description) or (not isinstance(extensions, dict)):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_tool_tag_entry",
                    "message": "tool tag entry missing required fields",
                    "path": "$.tool_tags",
                }
            )
            continue
        if tool_tag_id in tool_tag_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_tool_tag_id",
                    "message": "duplicate tool_tag_id '{}'".format(tool_tag_id),
                    "path": "$.tool_tags.tool_tag_id",
                }
            )
            continue
        tool_tag_seen.add(tool_tag_id)
        tool_tag_rows.append(
            {
                "schema_version": "1.0.0",
                "tool_tag_id": tool_tag_id,
                "description": description,
                "extensions": dict(extensions),
            }
        )
    tool_tag_rows = sorted(tool_tag_rows, key=lambda row: str(row.get("tool_tag_id", "")))

    _policy_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/surface_visibility_policy_registry.json",
        expected_schema_id="dominium.registry.surface_visibility_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], [], policy_load_errors

    visibility_policy_rows: List[dict] = []
    policy_seen = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_surface_visibility_policy_entry",
                    "message": "surface visibility policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        requires_entitlement = entry.get("requires_entitlement")
        requires_lens_channel = entry.get("requires_lens_channel")
        extensions = entry.get("extensions")
        if (
            (not policy_id)
            or (requires_entitlement is not None and not isinstance(requires_entitlement, str))
            or (requires_lens_channel is not None and not isinstance(requires_lens_channel, str))
            or (not isinstance(extensions, dict))
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_surface_visibility_policy_entry",
                    "message": "surface visibility policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        if policy_id in policy_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_surface_visibility_policy_id",
                    "message": "duplicate surface visibility policy id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue
        policy_seen.add(policy_id)
        visibility_policy_rows.append(
            {
                "schema_version": "1.0.0",
                "policy_id": policy_id,
                "requires_entitlement": (
                    str(requires_entitlement).strip() if isinstance(requires_entitlement, str) else None
                ),
                "requires_lens_channel": (
                    str(requires_lens_channel).strip() if isinstance(requires_lens_channel, str) else None
                ),
                "extensions": dict(extensions),
            }
        )
    visibility_policy_rows = sorted(visibility_policy_rows, key=lambda row: str(row.get("policy_id", "")))
    return surface_type_rows, tool_tag_rows, visibility_policy_rows, errors


def _civilisation_registry_rows(
    repo_root: str,
) -> Tuple[
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
    List[dict],
]:
    errors: List[dict] = []

    _governance_record, governance_rows_raw, governance_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/governance_type_registry.json",
        expected_schema_id="dominium.registry.governance_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="governance_types",
    )
    if governance_load_errors:
        return [], [], [], [], [], [], [], [], [], [], governance_load_errors

    governance_rows: List[dict] = []
    governance_seen = set()
    for entry in sorted(governance_rows_raw, key=lambda row: str((row or {}).get("governance_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_governance_type_entry",
                    "message": "governance type entry must be object",
                    "path": "$.governance_types",
                }
            )
            continue
        governance_type_id = str(entry.get("governance_type_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        extensions = entry.get("extensions")
        if not governance_type_id or not description or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_governance_type_entry",
                    "message": "governance type entry missing required fields",
                    "path": "$.governance_types",
                }
            )
            continue
        if governance_type_id in governance_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_governance_type_id",
                    "message": "duplicate governance_type_id '{}'".format(governance_type_id),
                    "path": "$.governance_types.governance_type_id",
                }
            )
            continue
        governance_seen.add(governance_type_id)
        governance_rows.append(
            {
                "governance_type_id": governance_type_id,
                "description": description,
                "extensions": dict(extensions),
            }
        )
    governance_rows = sorted(governance_rows, key=lambda row: str(row.get("governance_type_id", "")))

    _diplomatic_record, diplomatic_rows_raw, diplomatic_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/diplomatic_state_registry.json",
        expected_schema_id="dominium.registry.diplomatic_state_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="states",
    )
    if diplomatic_load_errors:
        return [], [], [], [], [], [], [], [], [], [], diplomatic_load_errors

    diplomatic_rows: List[dict] = []
    diplomatic_seen = set()
    for entry in sorted(diplomatic_rows_raw, key=lambda row: str((row or {}).get("relation_state", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_diplomatic_state_entry",
                    "message": "diplomatic state entry must be object",
                    "path": "$.states",
                }
            )
            continue
        relation_state = str(entry.get("relation_state", "")).strip()
        description = str(entry.get("description", "")).strip()
        extensions = entry.get("extensions")
        if not relation_state or not description or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_diplomatic_state_entry",
                    "message": "diplomatic state entry missing required fields",
                    "path": "$.states",
                }
            )
            continue
        if relation_state in diplomatic_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_diplomatic_state",
                    "message": "duplicate relation_state '{}'".format(relation_state),
                    "path": "$.states.relation_state",
                }
            )
            continue
        diplomatic_seen.add(relation_state)
        diplomatic_rows.append(
            {
                "relation_state": relation_state,
                "description": description,
                "extensions": dict(extensions),
            }
        )
    diplomatic_rows = sorted(diplomatic_rows, key=lambda row: str(row.get("relation_state", "")))

    _cohort_record, cohort_rows_raw, cohort_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/cohort_mapping_policy_registry.json",
        expected_schema_id="dominium.registry.cohort_mapping_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if cohort_load_errors:
        return [], [], [], [], [], [], [], [], [], [], cohort_load_errors

    cohort_rows: List[dict] = []
    cohort_seen = set()
    for entry in sorted(cohort_rows_raw, key=lambda row: str((row or {}).get("mapping_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cohort_mapping_policy_entry",
                    "message": "cohort mapping policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        mapping_policy_id = str(entry.get("mapping_policy_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        max_micro_agents_per_cohort = int(entry.get("max_micro_agents_per_cohort", 0) or 0)
        spawn_distribution_rules = entry.get("spawn_distribution_rules")
        collapse_aggregation_rules = entry.get("collapse_aggregation_rules")
        anonymous_micro_agents = entry.get("anonymous_micro_agents")
        extensions = entry.get("extensions")
        if (
            not mapping_policy_id
            or not description
            or max_micro_agents_per_cohort < 0
            or not isinstance(spawn_distribution_rules, dict)
            or not isinstance(collapse_aggregation_rules, dict)
            or not isinstance(anonymous_micro_agents, bool)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cohort_mapping_policy_entry",
                    "message": "cohort mapping policy '{}' missing required fields".format(
                        mapping_policy_id or "<missing>"
                    ),
                    "path": "$.policies",
                }
            )
            continue
        if mapping_policy_id in cohort_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_cohort_mapping_policy_id",
                    "message": "duplicate mapping_policy_id '{}'".format(mapping_policy_id),
                    "path": "$.policies.mapping_policy_id",
                }
            )
            continue
        cohort_seen.add(mapping_policy_id)
        cohort_rows.append(
            {
                "mapping_policy_id": mapping_policy_id,
                "description": description,
                "max_micro_agents_per_cohort": int(max_micro_agents_per_cohort),
                "spawn_distribution_rules": dict(
                    (str(key), spawn_distribution_rules[key]) for key in sorted(spawn_distribution_rules.keys())
                ),
                "collapse_aggregation_rules": dict(
                    (str(key), collapse_aggregation_rules[key]) for key in sorted(collapse_aggregation_rules.keys())
                ),
                "anonymous_micro_agents": bool(anonymous_micro_agents),
                "extensions": dict(extensions),
            }
        )
    cohort_rows = sorted(cohort_rows, key=lambda row: str(row.get("mapping_policy_id", "")))

    _order_type_record, order_type_rows_raw, order_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/order_type_registry.json",
        expected_schema_id="dominium.registry.order_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="order_types",
    )
    if order_type_load_errors:
        return [], [], [], [], [], [], [], [], [], [], order_type_load_errors

    order_type_rows: List[dict] = []
    order_type_seen = set()
    allowed_target_kind_set = {"agent", "cohort", "faction", "territory"}
    for entry in sorted(order_type_rows_raw, key=lambda row: str((row or {}).get("order_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_order_type_entry",
                    "message": "order type entry must be object",
                    "path": "$.order_types",
                }
            )
            continue
        order_type_id = str(entry.get("order_type_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        payload_schema_id = str(entry.get("payload_schema_id", "")).strip()
        allowed_target_kinds = entry.get("allowed_target_kinds")
        required_capabilities = entry.get("required_capabilities")
        extensions = entry.get("extensions")
        try:
            default_priority = int(entry.get("default_priority", -1) or 0)
        except (TypeError, ValueError):
            default_priority = -1
        if (
            not order_type_id
            or not description
            or not payload_schema_id
            or default_priority < 0
            or not isinstance(allowed_target_kinds, list)
            or not isinstance(required_capabilities, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_order_type_entry",
                    "message": "order type '{}' missing required fields".format(order_type_id or "<missing>"),
                    "path": "$.order_types",
                }
            )
            continue
        if order_type_id in order_type_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_order_type_id",
                    "message": "duplicate order_type_id '{}'".format(order_type_id),
                    "path": "$.order_types.order_type_id",
                }
            )
            continue
        target_kinds = _sorted_unique_strings(allowed_target_kinds)
        if not target_kinds or any(token not in allowed_target_kind_set for token in target_kinds):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_order_type_targets",
                    "message": "order type '{}' has invalid allowed_target_kinds".format(order_type_id),
                    "path": "$.order_types.allowed_target_kinds",
                }
            )
            continue
        order_type_seen.add(order_type_id)
        order_type_rows.append(
            {
                "order_type_id": order_type_id,
                "description": description,
                "payload_schema_id": payload_schema_id,
                "allowed_target_kinds": target_kinds,
                "default_priority": int(default_priority),
                "required_capabilities": _sorted_unique_strings(required_capabilities),
                "extensions": dict(extensions),
            }
        )
    order_type_rows = sorted(order_type_rows, key=lambda row: str(row.get("order_type_id", "")))

    _role_record, role_rows_raw, role_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/role_registry.json",
        expected_schema_id="dominium.registry.role_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="roles",
    )
    if role_load_errors:
        return [], [], [], [], [], [], [], [], [], [], role_load_errors

    role_rows: List[dict] = []
    role_seen = set()
    for entry in sorted(role_rows_raw, key=lambda row: str((row or {}).get("role_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_role_entry",
                    "message": "role entry must be object",
                    "path": "$.roles",
                }
            )
            continue
        role_id = str(entry.get("role_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        granted_entitlements = entry.get("granted_entitlements")
        extensions = entry.get("extensions")
        if not role_id or not description or not isinstance(granted_entitlements, list) or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_role_entry",
                    "message": "role '{}' missing required fields".format(role_id or "<missing>"),
                    "path": "$.roles",
                }
            )
            continue
        if role_id in role_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_role_id",
                    "message": "duplicate role_id '{}'".format(role_id),
                    "path": "$.roles.role_id",
                }
            )
            continue
        role_seen.add(role_id)
        role_rows.append(
            {
                "role_id": role_id,
                "description": description,
                "granted_entitlements": _sorted_unique_strings(granted_entitlements),
                "extensions": dict(extensions),
            }
        )
    role_rows = sorted(role_rows, key=lambda row: str(row.get("role_id", "")))

    _institution_record, institution_rows_raw, institution_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/institution_type_registry.json",
        expected_schema_id="dominium.registry.institution_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="institution_types",
    )
    if institution_load_errors:
        return [], [], [], [], [], [], [], [], [], [], institution_load_errors

    role_id_set = set(str(row.get("role_id", "")).strip() for row in role_rows)
    institution_rows: List[dict] = []
    institution_seen = set()
    for entry in sorted(institution_rows_raw, key=lambda row: str((row or {}).get("institution_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_institution_type_entry",
                    "message": "institution type entry must be object",
                    "path": "$.institution_types",
                }
            )
            continue
        institution_type_id = str(entry.get("institution_type_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        allowed_role_ids = entry.get("allowed_role_ids")
        extensions = entry.get("extensions")
        if not institution_type_id or not description or not isinstance(allowed_role_ids, list) or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_institution_type_entry",
                    "message": "institution type '{}' missing required fields".format(institution_type_id or "<missing>"),
                    "path": "$.institution_types",
                }
            )
            continue
        if institution_type_id in institution_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_institution_type_id",
                    "message": "duplicate institution_type_id '{}'".format(institution_type_id),
                    "path": "$.institution_types.institution_type_id",
                }
            )
            continue
        allowed_roles = _sorted_unique_strings(allowed_role_ids)
        missing_roles = [token for token in allowed_roles if token not in role_id_set]
        if missing_roles:
            errors.append(
                {
                    "code": "refuse.registry_compile.institution_type_role_missing",
                    "message": "institution type '{}' references unknown role ids: {}".format(
                        institution_type_id,
                        ",".join(sorted(missing_roles)),
                    ),
                    "path": "$.institution_types.allowed_role_ids",
                }
            )
            continue
        institution_seen.add(institution_type_id)
        institution_rows.append(
            {
                "institution_type_id": institution_type_id,
                "description": description,
                "allowed_role_ids": allowed_roles,
                "extensions": dict(extensions),
            }
        )
    institution_rows = sorted(institution_rows, key=lambda row: str(row.get("institution_type_id", "")))

    _demography_policy_record, demography_policy_rows_raw, demography_policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/demography_policy_registry.json",
        expected_schema_id="dominium.registry.demography_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if demography_policy_load_errors:
        return [], [], [], [], [], [], [], [], [], [], demography_policy_load_errors

    _death_model_record, death_model_rows_raw, death_model_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/death_model_registry.json",
        expected_schema_id="dominium.registry.death_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="death_models",
    )
    if death_model_load_errors:
        return [], [], [], [], [], [], [], [], [], [], death_model_load_errors

    death_model_rows: List[dict] = []
    death_model_seen = set()
    for entry in sorted(death_model_rows_raw, key=lambda row: str((row or {}).get("death_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_death_model_entry",
                    "message": "death model entry must be object",
                    "path": "$.death_models",
                }
            )
            continue
        death_model_id = str(entry.get("death_model_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        modifiers = entry.get("modifiers")
        extensions = entry.get("extensions")
        try:
            base_death_rate_per_tick = float(entry.get("base_death_rate_per_tick", -1))
        except (TypeError, ValueError):
            base_death_rate_per_tick = -1.0
        if (
            not death_model_id
            or not description
            or base_death_rate_per_tick < 0
            or not isinstance(modifiers, dict)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_death_model_entry",
                    "message": "death model '{}' missing required fields".format(death_model_id or "<missing>"),
                    "path": "$.death_models",
                }
            )
            continue
        if death_model_id in death_model_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_death_model_id",
                    "message": "duplicate death_model_id '{}'".format(death_model_id),
                    "path": "$.death_models.death_model_id",
                }
            )
            continue
        death_model_seen.add(death_model_id)
        death_model_rows.append(
            {
                "death_model_id": death_model_id,
                "description": description,
                "base_death_rate_per_tick": float(base_death_rate_per_tick),
                "modifiers": dict((str(key), modifiers[key]) for key in sorted(modifiers.keys())),
                "extensions": dict(extensions),
            }
        )
    death_model_rows = sorted(death_model_rows, key=lambda row: str(row.get("death_model_id", "")))

    _birth_model_record, birth_model_rows_raw, birth_model_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/birth_model_registry.json",
        expected_schema_id="dominium.registry.birth_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="birth_models",
    )
    if birth_model_load_errors:
        return [], [], [], [], [], [], [], [], [], [], birth_model_load_errors

    birth_model_rows: List[dict] = []
    birth_model_seen = set()
    for entry in sorted(birth_model_rows_raw, key=lambda row: str((row or {}).get("birth_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_birth_model_entry",
                    "message": "birth model entry must be object",
                    "path": "$.birth_models",
                }
            )
            continue
        birth_model_id = str(entry.get("birth_model_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        modifiers = entry.get("modifiers")
        extensions = entry.get("extensions")
        try:
            base_birth_rate_per_tick = float(entry.get("base_birth_rate_per_tick", -1))
        except (TypeError, ValueError):
            base_birth_rate_per_tick = -1.0
        if (
            not birth_model_id
            or not description
            or base_birth_rate_per_tick < 0
            or not isinstance(modifiers, dict)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_birth_model_entry",
                    "message": "birth model '{}' missing required fields".format(birth_model_id or "<missing>"),
                    "path": "$.birth_models",
                }
            )
            continue
        if birth_model_id in birth_model_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_birth_model_id",
                    "message": "duplicate birth_model_id '{}'".format(birth_model_id),
                    "path": "$.birth_models.birth_model_id",
                }
            )
            continue
        birth_model_seen.add(birth_model_id)
        birth_model_rows.append(
            {
                "birth_model_id": birth_model_id,
                "description": description,
                "base_birth_rate_per_tick": float(base_birth_rate_per_tick),
                "modifiers": dict((str(key), modifiers[key]) for key in sorted(modifiers.keys())),
                "extensions": dict(extensions),
            }
        )
    birth_model_rows = sorted(birth_model_rows, key=lambda row: str(row.get("birth_model_id", "")))

    _migration_model_record, migration_model_rows_raw, migration_model_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/migration_model_registry.json",
        expected_schema_id="dominium.registry.migration_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="migration_models",
    )
    if migration_model_load_errors:
        return [], [], [], [], [], [], [], [], [], [], migration_model_load_errors

    migration_model_rows: List[dict] = []
    migration_model_seen = set()
    for entry in sorted(migration_model_rows_raw, key=lambda row: str((row or {}).get("migration_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_migration_model_entry",
                    "message": "migration model entry must be object",
                    "path": "$.migration_models",
                }
            )
            continue
        migration_model_id = str(entry.get("migration_model_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        travel_time_policy_id = str(entry.get("travel_time_policy_id", "")).strip()
        capacity_limits = entry.get("capacity_limits")
        extensions = entry.get("extensions")
        if (
            not migration_model_id
            or not description
            or not travel_time_policy_id
            or not isinstance(capacity_limits, dict)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_migration_model_entry",
                    "message": "migration model '{}' missing required fields".format(migration_model_id or "<missing>"),
                    "path": "$.migration_models",
                }
            )
            continue
        if migration_model_id in migration_model_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_migration_model_id",
                    "message": "duplicate migration_model_id '{}'".format(migration_model_id),
                    "path": "$.migration_models.migration_model_id",
                }
            )
            continue
        migration_model_seen.add(migration_model_id)
        migration_model_rows.append(
            {
                "migration_model_id": migration_model_id,
                "description": description,
                "travel_time_policy_id": travel_time_policy_id,
                "capacity_limits": dict((str(key), capacity_limits[key]) for key in sorted(capacity_limits.keys())),
                "extensions": dict(extensions),
            }
        )
    migration_model_rows = sorted(migration_model_rows, key=lambda row: str(row.get("migration_model_id", "")))

    death_model_id_set = set(str(row.get("death_model_id", "")).strip() for row in death_model_rows)
    birth_model_id_set = set(str(row.get("birth_model_id", "")).strip() for row in birth_model_rows)
    migration_model_id_set = set(str(row.get("migration_model_id", "")).strip() for row in migration_model_rows)
    demography_policy_rows: List[dict] = []
    demography_policy_seen = set()
    for entry in sorted(demography_policy_rows_raw, key=lambda row: str((row or {}).get("demography_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_demography_policy_entry",
                    "message": "demography policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        demography_policy_id = str(entry.get("demography_policy_id", "")).strip()
        births_enabled = entry.get("births_enabled")
        death_model_id = str(entry.get("death_model_id", "")).strip()
        birth_model_id = str(entry.get("birth_model_id", "")).strip()
        migration_model_id = str(entry.get("migration_model_id", "")).strip()
        deterministic_tie_break_id = str(entry.get("deterministic_tie_break_id", "")).strip()
        extensions = entry.get("extensions")
        try:
            tick_rate = int(entry.get("tick_rate", 0) or 0)
        except (TypeError, ValueError):
            tick_rate = 0
        if (
            not demography_policy_id
            or not isinstance(births_enabled, bool)
            or not death_model_id
            or not birth_model_id
            or not migration_model_id
            or tick_rate < 1
            or not deterministic_tie_break_id
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_demography_policy_entry",
                    "message": "demography policy '{}' missing required fields".format(
                        demography_policy_id or "<missing>"
                    ),
                    "path": "$.policies",
                }
            )
            continue
        if demography_policy_id in demography_policy_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_demography_policy_id",
                    "message": "duplicate demography_policy_id '{}'".format(demography_policy_id),
                    "path": "$.policies.demography_policy_id",
                }
            )
            continue
        missing_refs = []
        if death_model_id not in death_model_id_set:
            missing_refs.append("death_model_id={}".format(death_model_id))
        if birth_model_id not in birth_model_id_set:
            missing_refs.append("birth_model_id={}".format(birth_model_id))
        if migration_model_id not in migration_model_id_set:
            missing_refs.append("migration_model_id={}".format(migration_model_id))
        if missing_refs:
            errors.append(
                {
                    "code": "refuse.registry_compile.demography_policy_model_missing",
                    "message": "demography policy '{}' references unknown model ids: {}".format(
                        demography_policy_id,
                        ",".join(sorted(missing_refs)),
                    ),
                    "path": "$.policies",
                }
            )
            continue
        demography_policy_seen.add(demography_policy_id)
        demography_policy_rows.append(
            {
                "demography_policy_id": demography_policy_id,
                "births_enabled": bool(births_enabled),
                "death_model_id": death_model_id,
                "birth_model_id": birth_model_id,
                "migration_model_id": migration_model_id,
                "tick_rate": int(tick_rate),
                "deterministic_tie_break_id": deterministic_tie_break_id,
                "extensions": dict(extensions),
            }
        )
    demography_policy_rows = sorted(demography_policy_rows, key=lambda row: str(row.get("demography_policy_id", "")))

    return (
        governance_rows,
        diplomatic_rows,
        cohort_rows,
        order_type_rows,
        role_rows,
        institution_rows,
        demography_policy_rows,
        death_model_rows,
        birth_model_rows,
        migration_model_rows,
        errors,
    )


def _conservation_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _quantity_record, quantity_rows_raw, quantity_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/quantity_registry.json",
        expected_schema_id="dominium.registry.quantity_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="quantities",
    )
    if quantity_load_errors:
        return [], [], [], quantity_load_errors

    _exception_record, exception_type_rows_raw, exception_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/exception_type_registry.json",
        expected_schema_id="dominium.registry.exception_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="exception_types",
    )
    if exception_type_load_errors:
        return [], [], [], exception_type_load_errors

    _contract_set_record, contract_set_rows_raw, contract_set_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/conservation_contract_set_registry.json",
        expected_schema_id="dominium.registry.conservation_contract_set_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="contract_sets",
    )
    if contract_set_load_errors:
        return [], [], [], contract_set_load_errors

    quantity_rows: List[dict] = []
    quantity_seen = set()
    for entry in sorted(quantity_rows_raw, key=lambda row: str((row or {}).get("quantity_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quantity_entry",
                    "message": "quantity entry must be object",
                    "path": "$.quantities",
                }
            )
            continue
        quantity_id = str(entry.get("quantity_id", "")).strip()
        if not quantity_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quantity_entry",
                    "message": "quantity_id is missing",
                    "path": "$.quantities.quantity_id",
                }
            )
            continue
        if quantity_id in quantity_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_quantity_id",
                    "message": "duplicate quantity_id '{}'".format(quantity_id),
                    "path": "$.quantities.quantity_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="quantity",
            payload=entry,
            path="data/registries/quantity_registry.json#{}".format(quantity_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        quantity_seen.add(quantity_id)
        quantity_rows.append(
            {
                "quantity_id": quantity_id,
                "description": str(entry.get("description", "")).strip(),
                "numeric_type": str(entry.get("numeric_type", "fixed_point")).strip() or "fixed_point",
                "units_id": str(entry.get("units_id", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    quantity_rows = sorted(quantity_rows, key=lambda row: str(row.get("quantity_id", "")))

    exception_type_rows: List[dict] = []
    exception_type_seen = set()
    for entry in sorted(exception_type_rows_raw, key=lambda row: str((row or {}).get("exception_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_exception_type_entry",
                    "message": "exception type entry must be object",
                    "path": "$.exception_types",
                }
            )
            continue
        exception_type_id = str(entry.get("exception_type_id", "")).strip()
        if not exception_type_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_exception_type_entry",
                    "message": "exception_type_id is missing",
                    "path": "$.exception_types.exception_type_id",
                }
            )
            continue
        if exception_type_id in exception_type_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_exception_type_id",
                    "message": "duplicate exception_type_id '{}'".format(exception_type_id),
                    "path": "$.exception_types.exception_type_id",
                }
            )
            continue
        description = str(entry.get("description", "")).strip()
        if not description:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_exception_type_entry",
                    "message": "exception type '{}' is missing description".format(exception_type_id),
                    "path": "$.exception_types.description",
                }
            )
            continue
        extensions = entry.get("extensions")
        if not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_exception_type_entry",
                    "message": "exception type '{}' extensions must be object".format(exception_type_id),
                    "path": "$.exception_types.extensions",
                }
            )
            continue
        exception_type_seen.add(exception_type_id)
        exception_type_rows.append(
            {
                "exception_type_id": exception_type_id,
                "description": description,
                "extensions": dict(extensions),
            }
        )
    exception_type_rows = sorted(exception_type_rows, key=lambda row: str(row.get("exception_type_id", "")))

    quantity_ids = set(str(row.get("quantity_id", "")).strip() for row in quantity_rows)
    exception_type_ids = set(str(row.get("exception_type_id", "")).strip() for row in exception_type_rows)

    contract_set_rows: List[dict] = []
    contract_set_seen = set()
    for entry in sorted(contract_set_rows_raw, key=lambda row: str((row or {}).get("contract_set_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_conservation_contract_set_entry",
                    "message": "conservation contract set entry must be object",
                    "path": "$.contract_sets",
                }
            )
            continue
        contract_set_id = str(entry.get("contract_set_id", "")).strip()
        if not contract_set_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_conservation_contract_set_entry",
                    "message": "contract_set_id is missing",
                    "path": "$.contract_sets.contract_set_id",
                }
            )
            continue
        if contract_set_id in contract_set_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_conservation_contract_set_id",
                    "message": "duplicate contract_set_id '{}'".format(contract_set_id),
                    "path": "$.contract_sets.contract_set_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="conservation_contract_set",
            payload=entry,
            path="data/registries/conservation_contract_set_registry.json#{}".format(contract_set_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        quantities = list(entry.get("quantities") or [])
        missing_refs: List[str] = []
        for quantity_row in quantities:
            if not isinstance(quantity_row, dict):
                continue
            quantity_id = str(quantity_row.get("quantity_id", "")).strip()
            if quantity_id not in quantity_ids:
                missing_refs.append("quantity_id={}".format(quantity_id))
            for exception_type_id in sorted(
                set(str(item).strip() for item in (quantity_row.get("allowed_exception_types") or []) if str(item).strip())
            ):
                if exception_type_id not in exception_type_ids:
                    missing_refs.append("allowed_exception_types={}".format(exception_type_id))
        if missing_refs:
            errors.append(
                {
                    "code": "refuse.registry_compile.conservation_contract_set_reference_missing",
                    "message": "contract_set '{}' references unknown ids: {}".format(
                        contract_set_id,
                        ",".join(sorted(set(missing_refs))),
                    ),
                    "path": "$.contract_sets",
                }
            )
            continue
        contract_set_seen.add(contract_set_id)
        normalized_quantities = []
        for quantity_row in sorted(
            (dict(item) for item in quantities if isinstance(item, dict)),
            key=lambda row: (
                str(row.get("quantity_id", "")),
                str(row.get("mode", "")),
            ),
        ):
            normalized_quantities.append(
                {
                    "quantity_id": str(quantity_row.get("quantity_id", "")).strip(),
                    "mode": str(quantity_row.get("mode", "")).strip(),
                    "tolerance": int(quantity_row.get("tolerance", 0) or 0),
                    "allowed_exception_types": sorted(
                        set(str(item).strip() for item in (quantity_row.get("allowed_exception_types") or []) if str(item).strip())
                    ),
                    "notes": str(quantity_row.get("notes", "")).strip(),
                }
            )
        contract_set_rows.append(
            {
                "contract_set_id": contract_set_id,
                "description": str(entry.get("description", "")).strip(),
                "quantities": normalized_quantities,
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )

    contract_set_rows = sorted(contract_set_rows, key=lambda row: str(row.get("contract_set_id", "")))
    return quantity_rows, exception_type_rows, contract_set_rows, errors


def _materials_dimension_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _base_record, base_rows_raw, base_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/base_dimension_registry.json",
        expected_schema_id="dominium.registry.base_dimension_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="base_dimensions",
    )
    if base_load_errors:
        return [], [], [], [], base_load_errors

    _dimension_record, dimension_rows_raw, dimension_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/dimension_registry.json",
        expected_schema_id="dominium.registry.dimension_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="dimensions",
    )
    if dimension_load_errors:
        return [], [], [], [], dimension_load_errors

    _unit_record, unit_rows_raw, unit_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/unit_registry.json",
        expected_schema_id="dominium.registry.unit_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="units",
    )
    if unit_load_errors:
        return [], [], [], [], unit_load_errors

    _quantity_type_record, quantity_type_rows_raw, quantity_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/quantity_type_registry.json",
        expected_schema_id="dominium.registry.quantity_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="quantity_types",
    )
    if quantity_type_load_errors:
        return [], [], [], [], quantity_type_load_errors

    base_dimension_rows: List[dict] = []
    seen_base_ids = set()
    for entry in sorted(base_rows_raw, key=lambda row: str((row or {}).get("base_dimension_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_base_dimension_entry",
                    "message": "base dimension entry must be object",
                    "path": "$.base_dimensions",
                }
            )
            continue
        base_dimension_id = str(entry.get("base_dimension_id", "")).strip()
        if not base_dimension_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_base_dimension_entry",
                    "message": "base_dimension_id is missing",
                    "path": "$.base_dimensions.base_dimension_id",
                }
            )
            continue
        if base_dimension_id in seen_base_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_base_dimension_id",
                    "message": "duplicate base_dimension_id '{}'".format(base_dimension_id),
                    "path": "$.base_dimensions.base_dimension_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="base_dimension",
            payload=entry,
            path="data/registries/base_dimension_registry.json#{}".format(base_dimension_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        seen_base_ids.add(base_dimension_id)
        base_dimension_rows.append(
            {
                "base_dimension_id": base_dimension_id,
                "description": str(entry.get("description", "")).strip(),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    base_dimension_rows = sorted(base_dimension_rows, key=lambda row: str(row.get("base_dimension_id", "")))
    base_dimension_ids = set(str(row.get("base_dimension_id", "")).strip() for row in base_dimension_rows)

    dimension_rows: List[dict] = []
    seen_dimension_ids = set()
    for entry in sorted(dimension_rows_raw, key=lambda row: str((row or {}).get("dimension_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_dimension_entry",
                    "message": "dimension entry must be object",
                    "path": "$.dimensions",
                }
            )
            continue
        dimension_id = str(entry.get("dimension_id", "")).strip()
        if not dimension_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_dimension_entry",
                    "message": "dimension_id is missing",
                    "path": "$.dimensions.dimension_id",
                }
            )
            continue
        if dimension_id in seen_dimension_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_dimension_id",
                    "message": "duplicate dimension_id '{}'".format(dimension_id),
                    "path": "$.dimensions.dimension_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="dimension",
            payload=entry,
            path="data/registries/dimension_registry.json#{}".format(dimension_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        raw_exponents = dict(entry.get("base_exponents") or {})
        normalized_exponents = {}
        missing_base_ids = []
        for base_dimension_id in sorted(raw_exponents.keys()):
            token = str(base_dimension_id).strip()
            if not token:
                continue
            exponent = int(raw_exponents.get(base_dimension_id, 0) or 0)
            if exponent == 0:
                continue
            if token not in base_dimension_ids:
                missing_base_ids.append(token)
                continue
            normalized_exponents[token] = int(exponent)
        if missing_base_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.dimension_reference_missing",
                    "message": "dimension '{}' references unknown base dimensions: {}".format(
                        dimension_id,
                        ",".join(sorted(set(missing_base_ids))),
                    ),
                    "path": "$.dimensions.base_exponents",
                }
            )
            continue
        seen_dimension_ids.add(dimension_id)
        dimension_rows.append(
            {
                "dimension_id": dimension_id,
                "base_exponents": dict(normalized_exponents),
                "description": str(entry.get("description", "")).strip(),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    dimension_rows = sorted(dimension_rows, key=lambda row: str(row.get("dimension_id", "")))
    dimension_ids = set(str(row.get("dimension_id", "")).strip() for row in dimension_rows)

    unit_rows: List[dict] = []
    seen_unit_ids = set()
    for entry in sorted(unit_rows_raw, key=lambda row: str((row or {}).get("unit_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_unit_entry",
                    "message": "unit entry must be object",
                    "path": "$.units",
                }
            )
            continue
        unit_id = str(entry.get("unit_id", "")).strip()
        if not unit_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_unit_entry",
                    "message": "unit_id is missing",
                    "path": "$.units.unit_id",
                }
            )
            continue
        if unit_id in seen_unit_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_unit_id",
                    "message": "duplicate unit_id '{}'".format(unit_id),
                    "path": "$.units.unit_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="unit",
            payload=entry,
            path="data/registries/unit_registry.json#{}".format(unit_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        dimension_id = str(entry.get("dimension_id", "")).strip()
        if dimension_id not in dimension_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.unit_reference_missing",
                    "message": "unit '{}' references unknown dimension_id '{}'".format(unit_id, dimension_id),
                    "path": "$.units.dimension_id",
                }
            )
            continue
        scale_factor_to_canonical = int(entry.get("scale_factor_to_canonical", 0) or 0)
        if scale_factor_to_canonical <= 0:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_unit_entry",
                    "message": "unit '{}' must declare scale_factor_to_canonical > 0".format(unit_id),
                    "path": "$.units.scale_factor_to_canonical",
                }
            )
            continue
        seen_unit_ids.add(unit_id)
        unit_rows.append(
            {
                "unit_id": unit_id,
                "dimension_id": dimension_id,
                "scale_factor_to_canonical": int(scale_factor_to_canonical),
                "display_symbol": str(entry.get("display_symbol", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    unit_rows = sorted(unit_rows, key=lambda row: str(row.get("unit_id", "")))
    unit_ids = set(str(row.get("unit_id", "")).strip() for row in unit_rows)
    unit_dimension_by_id = {
        str(row.get("unit_id", "")).strip(): str(row.get("dimension_id", "")).strip()
        for row in unit_rows
        if str(row.get("unit_id", "")).strip()
    }

    quantity_type_rows: List[dict] = []
    seen_quantity_ids = set()
    for entry in sorted(quantity_type_rows_raw, key=lambda row: str((row or {}).get("quantity_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quantity_type_entry",
                    "message": "quantity type entry must be object",
                    "path": "$.quantity_types",
                }
            )
            continue
        quantity_id = str(entry.get("quantity_id", "")).strip()
        if not quantity_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quantity_type_entry",
                    "message": "quantity_id is missing",
                    "path": "$.quantity_types.quantity_id",
                }
            )
            continue
        if quantity_id in seen_quantity_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_quantity_type_id",
                    "message": "duplicate quantity_id '{}'".format(quantity_id),
                    "path": "$.quantity_types.quantity_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="quantity_type",
            payload=entry,
            path="data/registries/quantity_type_registry.json#{}".format(quantity_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        dimension_id = str(entry.get("dimension_id", "")).strip()
        default_unit_id = str(entry.get("default_unit_id", "")).strip()
        missing_refs = []
        if dimension_id not in dimension_ids:
            missing_refs.append("dimension_id={}".format(dimension_id))
        if default_unit_id not in unit_ids:
            missing_refs.append("default_unit_id={}".format(default_unit_id))
        if missing_refs:
            errors.append(
                {
                    "code": "refuse.registry_compile.quantity_type_reference_missing",
                    "message": "quantity type '{}' references unknown ids: {}".format(
                        quantity_id,
                        ",".join(sorted(set(missing_refs))),
                    ),
                    "path": "$.quantity_types",
                }
            )
            continue
        unit_dimension_id = str(unit_dimension_by_id.get(default_unit_id, "")).strip()
        if unit_dimension_id and unit_dimension_id != dimension_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.quantity_type_dimension_mismatch",
                    "message": "quantity type '{}' dimension '{}' does not match default unit '{}' dimension '{}'".format(
                        quantity_id,
                        dimension_id,
                        default_unit_id,
                        unit_dimension_id,
                    ),
                    "path": "$.quantity_types",
                }
            )
            continue
        seen_quantity_ids.add(quantity_id)
        quantity_type_rows.append(
            {
                "quantity_id": quantity_id,
                "dimension_id": dimension_id,
                "invariant_numeric_type": str(entry.get("invariant_numeric_type", "")).strip(),
                "default_unit_id": default_unit_id,
                "conservation_applicable": bool(entry.get("conservation_applicable", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    quantity_type_rows = sorted(quantity_type_rows, key=lambda row: str(row.get("quantity_id", "")))

    return base_dimension_rows, dimension_rows, unit_rows, quantity_type_rows, errors


def _material_taxonomy_registry_rows(
    repo_root: str,
    schema_root: str,
    *,
    dimension_rows: List[dict],
    unit_rows: List[dict],
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _element_record, element_rows_raw, element_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/element_registry.json",
        expected_schema_id="dominium.registry.element_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="elements",
    )
    if element_load_errors:
        return [], [], [], [], [], element_load_errors

    _compound_record, compound_rows_raw, compound_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/compound_registry.json",
        expected_schema_id="dominium.registry.compound_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="compounds",
    )
    if compound_load_errors:
        return [], [], [], [], [], compound_load_errors

    _mixture_record, mixture_rows_raw, mixture_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/mixture_registry.json",
        expected_schema_id="dominium.registry.mixture_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="mixtures",
    )
    if mixture_load_errors:
        return [], [], [], [], [], mixture_load_errors

    _material_record, material_rows_raw, material_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/material_class_registry.json",
        expected_schema_id="dominium.registry.material_class_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="materials",
    )
    if material_load_errors:
        return [], [], [], [], [], material_load_errors

    _quality_record, quality_rows_raw, quality_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/quality_distribution_registry.json",
        expected_schema_id="dominium.registry.quality_distribution_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="quality_distribution_models",
    )
    if quality_load_errors:
        return [], [], [], [], [], quality_load_errors

    dimension_ids = set(str(row.get("dimension_id", "")).strip() for row in dimension_rows if str(row.get("dimension_id", "")).strip())
    unit_dimension_by_id = {
        str(row.get("unit_id", "")).strip(): str(row.get("dimension_id", "")).strip()
        for row in unit_rows
        if str(row.get("unit_id", "")).strip()
    }
    fixed_scale = 16777216
    fixed_tolerance = 1

    def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
        if int(denominator) == 0:
            return 0
        n = int(numerator)
        d = int(denominator)
        sign = -1 if (n < 0) ^ (d < 0) else 1
        abs_n = abs(n)
        abs_d = abs(d)
        out = abs_n // abs_d
        rem = abs_n % abs_d
        if rem * 2 >= abs_d:
            out += 1
        return int(sign * out)

    element_rows: List[dict] = []
    element_mass_by_id: Dict[str, int] = {}
    element_id_seen = set()
    for entry in sorted(element_rows_raw, key=lambda row: str((row or {}).get("element_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_element_entry",
                    "message": "element entry must be object",
                    "path": "$.elements",
                }
            )
            continue
        element_id = str(entry.get("element_id", "")).strip()
        if not element_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_element_entry",
                    "message": "element_id is missing",
                    "path": "$.elements.element_id",
                }
            )
            continue
        if element_id in element_id_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_element_id",
                    "message": "duplicate element_id '{}'".format(element_id),
                    "path": "$.elements.element_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="element",
            payload=entry,
            path="data/registries/element_registry.json#{}".format(element_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        molar_mass_raw = int(entry.get("molar_mass_raw", 0) or 0)
        atomic_number = entry.get("atomic_number")
        if molar_mass_raw <= 0:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_element_entry",
                    "message": "element '{}' must declare molar_mass_raw > 0".format(element_id),
                    "path": "$.elements.molar_mass_raw",
                }
            )
            continue
        if atomic_number is not None and int(atomic_number) <= 0:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_element_entry",
                    "message": "element '{}' atomic_number must be null or >= 1".format(element_id),
                    "path": "$.elements.atomic_number",
                }
            )
            continue
        element_id_seen.add(element_id)
        element_mass_by_id[element_id] = int(molar_mass_raw)
        element_rows.append(
            {
                "element_id": element_id,
                "atomic_number": None if atomic_number is None else int(atomic_number),
                "molar_mass_raw": int(molar_mass_raw),
                "charge_default": None if entry.get("charge_default") is None else int(entry.get("charge_default", 0) or 0),
                "base_energy_content_raw": None
                if entry.get("base_energy_content_raw") is None
                else int(entry.get("base_energy_content_raw", 0) or 0),
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    element_rows = sorted(element_rows, key=lambda row: str(row.get("element_id", "")))
    element_ids = set(str(row.get("element_id", "")).strip() for row in element_rows)

    compound_rows: List[dict] = []
    compound_id_seen = set()
    for entry in sorted(compound_rows_raw, key=lambda row: str((row or {}).get("compound_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_compound_entry",
                    "message": "compound entry must be object",
                    "path": "$.compounds",
                }
            )
            continue
        compound_id = str(entry.get("compound_id", "")).strip()
        if not compound_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_compound_entry",
                    "message": "compound_id is missing",
                    "path": "$.compounds.compound_id",
                }
            )
            continue
        if compound_id in compound_id_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_compound_id",
                    "message": "duplicate compound_id '{}'".format(compound_id),
                    "path": "$.compounds.compound_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="compound",
            payload=entry,
            path="data/registries/compound_registry.json#{}".format(compound_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        raw_composition = dict(entry.get("composition") or {})
        normalized_composition: Dict[str, int] = {}
        missing_element_refs = []
        for element_id in sorted(raw_composition.keys()):
            token = str(element_id).strip()
            if not token:
                continue
            ratio = int(raw_composition.get(element_id, 0) or 0)
            if ratio <= 0:
                continue
            if token not in element_ids:
                missing_element_refs.append(token)
                continue
            normalized_composition[token] = int(ratio)
        if missing_element_refs:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "compound '{}' references unknown elements: {}".format(
                        compound_id,
                        ",".join(sorted(set(missing_element_refs))),
                    ),
                    "path": "$.compounds.composition",
                }
            )
            continue
        if not normalized_composition:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "compound '{}' requires at least one composition component".format(compound_id),
                    "path": "$.compounds.composition",
                }
            )
            continue
        molar_mass_mode = str(entry.get("molar_mass_mode", "derived")).strip() or "derived"
        declared_molar_mass_raw = int(entry.get("molar_mass_raw", 0) or 0)
        derived_molar_mass_raw = 0
        for element_id, ratio in sorted(normalized_composition.items()):
            derived_molar_mass_raw += int(ratio) * int(element_mass_by_id.get(element_id, 0))
        if derived_molar_mass_raw <= 0:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "compound '{}' derived molar mass is invalid".format(compound_id),
                    "path": "$.compounds",
                }
            )
            continue
        if molar_mass_mode == "declared" and declared_molar_mass_raw > 0:
            molar_mass_raw = int(declared_molar_mass_raw)
        else:
            molar_mass_raw = int(derived_molar_mass_raw)
            molar_mass_mode = "derived"
        mass_fraction_map: Dict[str, int] = {}
        assigned = 0
        element_tokens = sorted(normalized_composition.keys())
        for idx, element_id in enumerate(element_tokens):
            ratio = int(normalized_composition.get(element_id, 0))
            component_mass = int(ratio) * int(element_mass_by_id.get(element_id, 0))
            if idx < len(element_tokens) - 1:
                value_raw = _round_div_away_from_zero(component_mass * fixed_scale, molar_mass_raw)
                assigned += int(value_raw)
                mass_fraction_map[element_id] = int(value_raw)
            else:
                mass_fraction_map[element_id] = int(fixed_scale - assigned)
        if sum(int(value) for value in mass_fraction_map.values()) != fixed_scale:
            errors.append(
                {
                    "code": "refuse.material.mass_fraction_mismatch",
                    "message": "compound '{}' mass fractions failed fixed-point normalization".format(compound_id),
                    "path": "$.compounds.composition",
                }
            )
            continue
        compound_id_seen.add(compound_id)
        compound_rows.append(
            {
                "compound_id": compound_id,
                "composition": dict(normalized_composition),
                "molar_mass_mode": str(molar_mass_mode),
                "molar_mass_raw": int(molar_mass_raw),
                "mass_fractions_raw": dict(mass_fraction_map),
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    compound_rows = sorted(compound_rows, key=lambda row: str(row.get("compound_id", "")))
    compound_ids = set(str(row.get("compound_id", "")).strip() for row in compound_rows)

    mixture_rows: List[dict] = []
    mixture_id_seen = set()
    for entry in sorted(mixture_rows_raw, key=lambda row: str((row or {}).get("mixture_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_mixture_entry",
                    "message": "mixture entry must be object",
                    "path": "$.mixtures",
                }
            )
            continue
        mixture_id = str(entry.get("mixture_id", "")).strip()
        if not mixture_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_mixture_entry",
                    "message": "mixture_id is missing",
                    "path": "$.mixtures.mixture_id",
                }
            )
            continue
        if mixture_id in mixture_id_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_mixture_id",
                    "message": "duplicate mixture_id '{}'".format(mixture_id),
                    "path": "$.mixtures.mixture_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="mixture",
            payload=entry,
            path="data/registries/mixture_registry.json#{}".format(mixture_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        raw_components = dict(entry.get("components") or {})
        normalized_components: Dict[str, int] = {}
        for component_id in sorted(raw_components.keys()):
            token = str(component_id).strip()
            if not token:
                continue
            value_raw = int(raw_components.get(component_id, 0) or 0)
            if value_raw <= 0:
                continue
            normalized_components[token] = int(value_raw)
        if not normalized_components:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "mixture '{}' must include at least one positive component".format(mixture_id),
                    "path": "$.mixtures.components",
                }
            )
            continue
        mass_fraction_sum_raw = sum(int(value) for value in normalized_components.values())
        if abs(int(mass_fraction_sum_raw) - int(fixed_scale)) > int(fixed_tolerance):
            errors.append(
                {
                    "code": "refuse.material.mass_fraction_mismatch",
                    "message": "mixture '{}' mass fractions sum {} but expected {}".format(
                        mixture_id,
                        int(mass_fraction_sum_raw),
                        int(fixed_scale),
                    ),
                    "path": "$.mixtures.components",
                }
            )
            continue
        mixture_id_seen.add(mixture_id)
        mixture_rows.append(
            {
                "mixture_id": mixture_id,
                "components": dict(normalized_components),
                "mass_fraction_sum_raw": int(mass_fraction_sum_raw),
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    mixture_rows = sorted(mixture_rows, key=lambda row: str(row.get("mixture_id", "")))
    mixture_ids = set(str(row.get("mixture_id", "")).strip() for row in mixture_rows)

    quality_rows: List[dict] = []
    quality_id_seen = set()
    for entry in sorted(quality_rows_raw, key=lambda row: str((row or {}).get("quality_distribution_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quality_distribution_entry",
                    "message": "quality distribution entry must be object",
                    "path": "$.quality_distribution_models",
                }
            )
            continue
        quality_distribution_model_id = str(entry.get("quality_distribution_model_id", "")).strip()
        if not quality_distribution_model_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_quality_distribution_entry",
                    "message": "quality_distribution_model_id is missing",
                    "path": "$.quality_distribution_models.quality_distribution_model_id",
                }
            )
            continue
        if quality_distribution_model_id in quality_id_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_quality_distribution_id",
                    "message": "duplicate quality_distribution_model_id '{}'".format(quality_distribution_model_id),
                    "path": "$.quality_distribution_models.quality_distribution_model_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="quality_distribution",
            payload=entry,
            path="data/registries/quality_distribution_registry.json#{}".format(quality_distribution_model_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        quality_id_seen.add(quality_distribution_model_id)
        quality_rows.append(
            {
                "quality_distribution_model_id": quality_distribution_model_id,
                "description": str(entry.get("description", "")).strip(),
                "parameters": dict(entry.get("parameters") or {}),
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    quality_rows = sorted(quality_rows, key=lambda row: str(row.get("quality_distribution_model_id", "")))
    quality_ids = set(str(row.get("quality_distribution_model_id", "")).strip() for row in quality_rows)

    material_rows: List[dict] = []
    material_id_seen = set()
    for entry in sorted(material_rows_raw, key=lambda row: str((row or {}).get("material_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_material_class_entry",
                    "message": "material class entry must be object",
                    "path": "$.materials",
                }
            )
            continue
        material_id = str(entry.get("material_id", "")).strip()
        if not material_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_material_class_entry",
                    "message": "material_id is missing",
                    "path": "$.materials.material_id",
                }
            )
            continue
        if material_id in material_id_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_material_id",
                    "message": "duplicate material_id '{}'".format(material_id),
                    "path": "$.materials.material_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="material_class",
            payload=entry,
            path="data/registries/material_class_registry.json#{}".format(material_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        base_type = str(entry.get("base_type", "")).strip()
        base_ref_id = str(entry.get("base_ref_id", "")).strip()
        missing_ref = False
        if base_type == "element" and base_ref_id not in element_ids:
            missing_ref = True
        elif base_type == "compound" and base_ref_id not in compound_ids:
            missing_ref = True
        elif base_type == "mixture" and base_ref_id not in mixture_ids:
            missing_ref = True
        if missing_ref:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "material '{}' base_ref_id '{}' not found for base_type '{}'".format(
                        material_id,
                        base_ref_id,
                        base_type,
                    ),
                    "path": "$.materials.base_ref_id",
                }
            )
            continue

        def _normalize_property(field_name: str, expected_dimension_id: str = "") -> dict:
            row = entry.get(field_name)
            if not isinstance(row, dict):
                return {}
            unit_id = str(row.get("unit_id", "")).strip()
            dimension_id = str(row.get("dimension_id", "")).strip()
            value_raw = int(row.get("value_raw", 0) or 0)
            if not unit_id or not dimension_id:
                return {}
            if dimension_id not in dimension_ids:
                return {}
            unit_dimension_id = str(unit_dimension_by_id.get(unit_id, "")).strip()
            if not unit_dimension_id or unit_dimension_id != dimension_id:
                return {}
            if expected_dimension_id and dimension_id != expected_dimension_id:
                return {}
            return {
                "value_raw": int(value_raw),
                "dimension_id": dimension_id,
                "unit_id": unit_id,
            }

        density = _normalize_property("density", expected_dimension_id="dim.density")
        specific_energy = _normalize_property("specific_energy", expected_dimension_id="dim.specific_energy")
        conductivity = entry.get("conductivity")
        heat_capacity = entry.get("heat_capacity")
        conductivity_row = None if conductivity is None else _normalize_property("conductivity")
        heat_capacity_row = None if heat_capacity is None else _normalize_property("heat_capacity")

        if not density or not specific_energy or (conductivity is not None and conductivity_row is None) or (heat_capacity is not None and heat_capacity_row is None):
            errors.append(
                {
                    "code": "refuse.material.dimension_mismatch",
                    "message": "material '{}' property dimensions or units are invalid".format(material_id),
                    "path": "$.materials",
                }
            )
            continue

        quality_distribution_model_id = entry.get("quality_distribution_model_id")
        quality_distribution_token = None if quality_distribution_model_id is None else str(quality_distribution_model_id).strip()
        if quality_distribution_token and quality_distribution_token not in quality_ids:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "material '{}' references unknown quality_distribution_model_id '{}'".format(
                        material_id,
                        quality_distribution_token,
                    ),
                    "path": "$.materials.quality_distribution_model_id",
                }
            )
            continue

        material_id_seen.add(material_id)
        material_rows.append(
            {
                "material_id": material_id,
                "base_type": base_type,
                "base_ref_id": base_ref_id,
                "density": dict(density),
                "specific_energy": dict(specific_energy),
                "conductivity": None if conductivity is None else dict(conductivity_row or {}),
                "heat_capacity": None if heat_capacity is None else dict(heat_capacity_row or {}),
                "phase_tags": sorted(set(str(item).strip() for item in list(entry.get("phase_tags") or []) if str(item).strip())),
                "quality_distribution_model_id": quality_distribution_token,
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "deprecated": bool(entry.get("deprecated", False)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    material_rows = sorted(material_rows, key=lambda row: str(row.get("material_id", "")))
    material_ids = set(str(row.get("material_id", "")).strip() for row in material_rows)

    for mixture_row in mixture_rows:
        mixture_id = str(mixture_row.get("mixture_id", "")).strip() or "<unknown>"
        components = dict(mixture_row.get("components") or {})
        missing_component_refs = []
        for component_id in sorted(components.keys()):
            token = str(component_id).strip()
            if not token:
                continue
            if token in compound_ids or token in material_ids:
                continue
            missing_component_refs.append(token)
        if missing_component_refs:
            errors.append(
                {
                    "code": "refuse.material.invalid_composition",
                    "message": "mixture '{}' references unknown component ids: {}".format(
                        mixture_id,
                        ",".join(sorted(set(missing_component_refs))),
                    ),
                    "path": "$.mixtures.components",
                }
            )

    return element_rows, compound_rows, mixture_rows, material_rows, quality_rows, errors


def _materials_structure_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _part_class_record, part_class_rows_raw, part_class_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/part_class_registry.json",
        expected_schema_id="dominium.registry.part_class_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="part_classes",
    )
    if part_class_load_errors:
        return [], [], [], part_class_load_errors

    _connection_type_record, connection_type_rows_raw, connection_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/connection_type_registry.json",
        expected_schema_id="dominium.registry.connection_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="connection_types",
    )
    if connection_type_load_errors:
        return [], [], [], connection_type_load_errors

    _blueprint_record, blueprint_rows_raw, blueprint_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/blueprint_registry.json",
        expected_schema_id="dominium.registry.blueprint_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="blueprints",
    )
    if blueprint_load_errors:
        return [], [], [], blueprint_load_errors

    part_class_rows: List[dict] = []
    part_class_ids = set()
    for entry in sorted(part_class_rows_raw, key=lambda row: str((row or {}).get("part_class_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_part_class_entry",
                    "message": "part class entry must be object",
                    "path": "$.part_classes",
                }
            )
            continue
        part_class_id = str(entry.get("part_class_id", "")).strip()
        if not part_class_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_part_class_entry",
                    "message": "part_class_id is missing",
                    "path": "$.part_classes.part_class_id",
                }
            )
            continue
        if part_class_id in part_class_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_part_class_id",
                    "message": "duplicate part_class_id '{}'".format(part_class_id),
                    "path": "$.part_classes.part_class_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="part_class",
            payload=entry,
            path="data/registries/part_class_registry.json#{}".format(part_class_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        part_class_ids.add(part_class_id)
        part_class_rows.append(
            {
                "schema_version": "1.0.0",
                "part_class_id": part_class_id,
                "description": str(entry.get("description", "")).strip(),
                "default_material_class": None
                if entry.get("default_material_class") is None
                else str(entry.get("default_material_class", "")).strip(),
                "default_shape_tag": None
                if entry.get("default_shape_tag") is None
                else str(entry.get("default_shape_tag", "")).strip(),
                "failure_mode_tags": sorted(
                    set(str(item).strip() for item in list(entry.get("failure_mode_tags") or []) if str(item).strip())
                ),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    part_class_rows = sorted(part_class_rows, key=lambda row: str(row.get("part_class_id", "")))

    connection_type_rows: List[dict] = []
    connection_type_ids = set()
    for entry in sorted(connection_type_rows_raw, key=lambda row: str((row or {}).get("connection_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_connection_type_entry",
                    "message": "connection type entry must be object",
                    "path": "$.connection_types",
                }
            )
            continue
        connection_type_id = str(entry.get("connection_type_id", "")).strip()
        if not connection_type_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_connection_type_entry",
                    "message": "connection_type_id is missing",
                    "path": "$.connection_types.connection_type_id",
                }
            )
            continue
        if connection_type_id in connection_type_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_connection_type_id",
                    "message": "duplicate connection_type_id '{}'".format(connection_type_id),
                    "path": "$.connection_types.connection_type_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="connection_type",
            payload=entry,
            path="data/registries/connection_type_registry.json#{}".format(connection_type_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        requires_part_classes = sorted(
            set(str(item).strip() for item in list(entry.get("requires_part_classes") or []) if str(item).strip())
        )
        missing_part_classes = sorted(set(requires_part_classes) - set(part_class_ids))
        if missing_part_classes:
            errors.append(
                {
                    "code": "refuse.registry_compile.connection_type_part_class_missing",
                    "message": "connection type '{}' references unknown part classes: {}".format(
                        connection_type_id,
                        ",".join(missing_part_classes),
                    ),
                    "path": "$.connection_types.requires_part_classes",
                }
            )
            continue
        connection_type_ids.add(connection_type_id)
        connection_type_rows.append(
            {
                "schema_version": "1.0.0",
                "connection_type_id": connection_type_id,
                "description": str(entry.get("description", "")).strip(),
                "requires_part_classes": list(requires_part_classes),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    connection_type_rows = sorted(connection_type_rows, key=lambda row: str(row.get("connection_type_id", "")))

    blueprint_rows: List[dict] = []
    blueprint_ids = set()
    for entry in sorted(blueprint_rows_raw, key=lambda row: str((row or {}).get("blueprint_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_blueprint_registry_entry",
                    "message": "blueprint registry entry must be object",
                    "path": "$.blueprints",
                }
            )
            continue
        blueprint_id = str(entry.get("blueprint_id", "")).strip()
        blueprint_path = str(entry.get("blueprint_path", "")).strip()
        if not blueprint_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_blueprint_registry_entry",
                    "message": "blueprint_id is missing",
                    "path": "$.blueprints.blueprint_id",
                }
            )
            continue
        if blueprint_id in blueprint_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_blueprint_id",
                    "message": "duplicate blueprint_id '{}'".format(blueprint_id),
                    "path": "$.blueprints.blueprint_id",
                }
            )
            continue
        if not blueprint_path:
            errors.append(
                {
                    "code": "refuse.registry_compile.blueprint_path_missing",
                    "message": "blueprint '{}' is missing blueprint_path".format(blueprint_id),
                    "path": "$.blueprints.blueprint_path",
                }
            )
            continue
        blueprint_abs = os.path.join(repo_root, blueprint_path.replace("/", os.sep))
        if not os.path.isfile(blueprint_abs):
            errors.append(
                {
                    "code": "refuse.registry_compile.blueprint_path_missing",
                    "message": "blueprint '{}' path '{}' does not exist".format(blueprint_id, blueprint_path),
                    "path": "$.blueprints.blueprint_path",
                }
            )
            continue
        blueprint_payload, blueprint_payload_err = _read_json_payload(blueprint_abs)
        if blueprint_payload_err:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_blueprint_payload",
                    "message": "blueprint '{}' payload is invalid JSON".format(blueprint_id),
                    "path": "$.blueprints.blueprint_path",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="blueprint",
            payload=blueprint_payload,
            path="{}#{}".format(_norm(blueprint_path), blueprint_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        payload_blueprint_id = str(blueprint_payload.get("blueprint_id", "")).strip()
        if payload_blueprint_id != blueprint_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.blueprint_id_mismatch",
                    "message": "blueprint payload id '{}' does not match registry id '{}'".format(
                        payload_blueprint_id,
                        blueprint_id,
                    ),
                    "path": "$.blueprints.blueprint_id",
                }
            )
            continue
        blueprint_ids.add(blueprint_id)
        blueprint_rows.append(
            {
                "blueprint_id": blueprint_id,
                "description": str(entry.get("description", "")).strip()
                or str(blueprint_payload.get("description", "")).strip(),
                "blueprint_path": _norm(blueprint_path),
                "tags": sorted(set(str(item).strip() for item in list(entry.get("tags") or []) if str(item).strip())),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    blueprint_rows = sorted(blueprint_rows, key=lambda row: str(row.get("blueprint_id", "")))

    return part_class_rows, connection_type_rows, blueprint_rows, errors


def _logistics_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _routing_rule_record, routing_rule_rows_raw, routing_rule_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/logistics_routing_rule_registry.json",
        expected_schema_id="dominium.registry.logistics_routing_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="routing_rules",
    )
    if routing_rule_load_errors:
        return [], [], routing_rule_load_errors

    _graph_record, graph_rows_raw, graph_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/logistics_graph_registry.json",
        expected_schema_id="dominium.registry.logistics_graph_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="graphs",
    )
    if graph_load_errors:
        return [], [], graph_load_errors

    routing_rule_rows: List[dict] = []
    routing_rule_ids = set()
    for entry in sorted(routing_rule_rows_raw, key=lambda row: str((row or {}).get("rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_routing_rule_entry",
                    "message": "routing rule entry must be object",
                    "path": "$.routing_rules",
                }
            )
            continue
        rule_id = str(entry.get("rule_id", "")).strip()
        if not rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_routing_rule_entry",
                    "message": "routing rule entry missing rule_id",
                    "path": "$.routing_rules.rule_id",
                }
            )
            continue
        if rule_id in routing_rule_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_routing_rule_id",
                    "message": "duplicate routing rule id '{}'".format(rule_id),
                    "path": "$.routing_rules.rule_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="routing_rule",
            payload=entry,
            path="data/registries/logistics_routing_rule_registry.json#{}".format(rule_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        routing_rule_ids.add(rule_id)
        routing_rule_rows.append(
            {
                "schema_version": "1.0.0",
                "rule_id": rule_id,
                "description": str(entry.get("description", "")).strip(),
                "tie_break_policy": str(entry.get("tie_break_policy", "")).strip(),
                "allow_multi_hop": bool(entry.get("allow_multi_hop", False)),
                "constraints": dict(entry.get("constraints") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    routing_rule_rows = sorted(routing_rule_rows, key=lambda row: str(row.get("rule_id", "")))

    graph_rows: List[dict] = []
    graph_ids = set()
    for entry in sorted(graph_rows_raw, key=lambda row: str((row or {}).get("graph_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_logistics_graph_entry",
                    "message": "logistics graph entry must be object",
                    "path": "$.graphs",
                }
            )
            continue
        graph_id = str(entry.get("graph_id", "")).strip()
        if not graph_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_logistics_graph_entry",
                    "message": "logistics graph entry missing graph_id",
                    "path": "$.graphs.graph_id",
                }
            )
            continue
        if graph_id in graph_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_logistics_graph_id",
                    "message": "duplicate logistics graph id '{}'".format(graph_id),
                    "path": "$.graphs.graph_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="logistics_graph",
            payload=entry,
            path="data/registries/logistics_graph_registry.json#{}".format(graph_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        routing_rule_id = str(entry.get("deterministic_routing_rule_id", "")).strip()
        if routing_rule_id and routing_rule_id not in routing_rule_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_logistics_graph_entry",
                    "message": "logistics graph '{}' references unknown routing rule '{}'".format(
                        graph_id,
                        routing_rule_id,
                    ),
                    "path": "$.graphs.deterministic_routing_rule_id",
                }
            )
            continue
        graph_ids.add(graph_id)
        graph_rows.append(dict(entry))
    graph_rows = sorted(graph_rows, key=lambda row: str(row.get("graph_id", "")))

    return routing_rule_rows, graph_rows, errors


def _construction_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _event_type_record, event_type_rows_raw, event_type_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/provenance_event_type_registry.json",
        expected_schema_id="dominium.registry.provenance_event_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="event_types",
    )
    if event_type_load_errors:
        return [], [], event_type_load_errors

    _construction_policy_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/construction_policy_registry.json",
        expected_schema_id="dominium.registry.construction_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], policy_load_errors

    event_type_rows: List[dict] = []
    event_type_ids = set()
    for entry in sorted(event_type_rows_raw, key=lambda row: str((row or {}).get("event_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_provenance_event_type_entry",
                    "message": "provenance event type entry must be object",
                    "path": "$.event_types",
                }
            )
            continue
        event_type_id = str(entry.get("event_type_id", "")).strip()
        if not event_type_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_provenance_event_type_entry",
                    "message": "provenance event type entry missing event_type_id",
                    "path": "$.event_types.event_type_id",
                }
            )
            continue
        if event_type_id in event_type_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_provenance_event_type_id",
                    "message": "duplicate provenance event_type_id '{}'".format(event_type_id),
                    "path": "$.event_types.event_type_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="event_type_registry",
            payload=entry,
            path="data/registries/provenance_event_type_registry.json#{}".format(event_type_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        event_type_ids.add(event_type_id)
        event_type_rows.append(
            {
                "schema_version": "1.0.0",
                "event_type_id": event_type_id,
                "description": str(entry.get("description", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    event_type_rows = sorted(event_type_rows, key=lambda row: str(row.get("event_type_id", "")))

    policy_rows: List[dict] = []
    policy_ids = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_construction_policy_entry",
                    "message": "construction policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        if not policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_construction_policy_entry",
                    "message": "construction policy entry missing policy_id",
                    "path": "$.policies.policy_id",
                }
            )
            continue
        if policy_id in policy_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_construction_policy_id",
                    "message": "duplicate construction policy_id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="construction_policy",
            payload=entry,
            path="data/registries/construction_policy_registry.json#{}".format(policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        max_parallel_steps = int(_as_int(entry.get("max_parallel_steps", 1), 1))
        if max_parallel_steps < 1:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_construction_policy_entry",
                    "message": "construction policy '{}' max_parallel_steps must be >= 1".format(policy_id),
                    "path": "$.policies.max_parallel_steps",
                }
            )
            continue
        policy_ids.add(policy_id)
        policy_rows.append(
            {
                "schema_version": "1.0.0",
                "policy_id": policy_id,
                "default_step_duration_ticks": (
                    dict(entry.get("default_step_duration_ticks") or {})
                    if isinstance(entry.get("default_step_duration_ticks"), dict)
                    else int(_as_int(entry.get("default_step_duration_ticks", 0), 0))
                ),
                "allow_parallel_steps": bool(entry.get("allow_parallel_steps", False)),
                "max_parallel_steps": int(max_parallel_steps),
                "deterministic_scheduling_rule_id": str(entry.get("deterministic_scheduling_rule_id", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    policy_rows = sorted(policy_rows, key=lambda row: str(row.get("policy_id", "")))

    return event_type_rows, policy_rows, errors


def _maintenance_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _failure_mode_record, failure_mode_rows_raw, failure_mode_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/failure_mode_registry.json",
        expected_schema_id="dominium.registry.failure_mode_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="failure_modes",
    )
    if failure_mode_load_errors:
        return [], [], [], failure_mode_load_errors

    _maintenance_policy_record, maintenance_policy_rows_raw, maintenance_policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/maintenance_policy_registry.json",
        expected_schema_id="dominium.registry.maintenance_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if maintenance_policy_load_errors:
        return [], [], [], maintenance_policy_load_errors

    _backlog_rule_record, backlog_rule_rows_raw, backlog_rule_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/backlog_growth_rule_registry.json",
        expected_schema_id="dominium.registry.backlog_growth_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="rules",
    )
    if backlog_rule_load_errors:
        return [], [], [], backlog_rule_load_errors

    failure_mode_rows: List[dict] = []
    failure_mode_ids = set()
    for entry in sorted(failure_mode_rows_raw, key=lambda row: str((row or {}).get("failure_mode_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_failure_mode_entry",
                    "message": "failure mode entry must be object",
                    "path": "$.failure_modes",
                }
            )
            continue
        failure_mode_id = str(entry.get("failure_mode_id", "")).strip()
        if not failure_mode_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_failure_mode_entry",
                    "message": "failure mode entry missing failure_mode_id",
                    "path": "$.failure_modes.failure_mode_id",
                }
            )
            continue
        if failure_mode_id in failure_mode_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_failure_mode_id",
                    "message": "duplicate failure mode_id '{}'".format(failure_mode_id),
                    "path": "$.failure_modes.failure_mode_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="failure_mode",
            payload=entry,
            path="data/registries/failure_mode_registry.json#{}".format(failure_mode_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        failure_mode_ids.add(failure_mode_id)
        failure_mode_rows.append(
            {
                "schema_version": "1.0.0",
                "failure_mode_id": failure_mode_id,
                "description": str(entry.get("description", "")).strip(),
                "applies_to_part_classes": _sorted_unique_strings(entry.get("applies_to_part_classes")),
                "hazard_inputs": _sorted_unique_strings(entry.get("hazard_inputs")),
                "base_hazard_rate_per_tick": int(max(0, _as_int(entry.get("base_hazard_rate_per_tick", 0), 0))),
                "modifiers": dict(entry.get("modifiers") or {}),
                "failure_event_type_id": str(entry.get("failure_event_type_id", "")).strip(),
                "maintenance_effect_model_id": str(entry.get("maintenance_effect_model_id", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    failure_mode_rows = sorted(failure_mode_rows, key=lambda row: str(row.get("failure_mode_id", "")))

    backlog_rule_rows: List[dict] = []
    backlog_rule_ids = set()
    for entry in sorted(backlog_rule_rows_raw, key=lambda row: str((row or {}).get("rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_backlog_growth_rule_entry",
                    "message": "backlog growth rule entry must be object",
                    "path": "$.rules",
                }
            )
            continue
        rule_id = str(entry.get("rule_id", "")).strip()
        if not rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_backlog_growth_rule_entry",
                    "message": "backlog growth rule entry missing rule_id",
                    "path": "$.rules.rule_id",
                }
            )
            continue
        if rule_id in backlog_rule_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_backlog_growth_rule_id",
                    "message": "duplicate backlog growth rule_id '{}'".format(rule_id),
                    "path": "$.rules.rule_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="backlog_growth_rule",
            payload=entry,
            path="data/registries/backlog_growth_rule_registry.json#{}".format(rule_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        backlog_rule_ids.add(rule_id)
        thresholds = []
        for threshold in sorted(
            (item for item in list(entry.get("thresholds") or []) if isinstance(item, dict)),
            key=lambda item: (_as_int(item.get("at_backlog", 0), 0), _as_int(item.get("increment_per_tick", 0), 0)),
        ):
            thresholds.append(
                {
                    "at_backlog": int(max(0, _as_int(threshold.get("at_backlog", 0), 0))),
                    "increment_per_tick": int(max(0, _as_int(threshold.get("increment_per_tick", 0), 0))),
                }
            )
        backlog_rule_rows.append(
            {
                "schema_version": "1.0.0",
                "rule_id": rule_id,
                "description": str(entry.get("description", "")).strip(),
                "model_kind": str(entry.get("model_kind", "linear")).strip() or "linear",
                "base_increment_per_tick": int(max(0, _as_int(entry.get("base_increment_per_tick", 0), 0))),
                "thresholds": thresholds,
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    backlog_rule_rows = sorted(backlog_rule_rows, key=lambda row: str(row.get("rule_id", "")))

    maintenance_policy_rows: List[dict] = []
    maintenance_policy_ids = set()
    for entry in sorted(maintenance_policy_rows_raw, key=lambda row: str((row or {}).get("maintenance_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_maintenance_policy_entry",
                    "message": "maintenance policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("maintenance_policy_id", "")).strip()
        if not policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_maintenance_policy_entry",
                    "message": "maintenance policy entry missing maintenance_policy_id",
                    "path": "$.policies.maintenance_policy_id",
                }
            )
            continue
        if policy_id in maintenance_policy_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_maintenance_policy_id",
                    "message": "duplicate maintenance policy_id '{}'".format(policy_id),
                    "path": "$.policies.maintenance_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="maintenance_policy",
            payload=entry,
            path="data/registries/maintenance_policy_registry.json#{}".format(policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        backlog_growth_rule_id = str(entry.get("backlog_growth_rule_id", "")).strip()
        if backlog_growth_rule_id and backlog_growth_rule_id not in backlog_rule_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_maintenance_policy_entry",
                    "message": "maintenance policy '{}' references unknown backlog_growth_rule_id '{}'".format(
                        policy_id,
                        backlog_growth_rule_id,
                    ),
                    "path": "$.policies.backlog_growth_rule_id",
                }
            )
            continue
        maintenance_policy_ids.add(policy_id)
        maintenance_policy_rows.append(
            {
                "schema_version": "1.0.0",
                "maintenance_policy_id": policy_id,
                "description": str(entry.get("description", "")).strip(),
                "inspection_interval_ticks": int(max(0, _as_int(entry.get("inspection_interval_ticks", 0), 0))),
                "maintenance_interval_ticks": int(max(0, _as_int(entry.get("maintenance_interval_ticks", 0), 0))),
                "backlog_growth_rule_id": backlog_growth_rule_id,
                "max_backlog": int(max(0, _as_int(entry.get("max_backlog", 0), 0))),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    maintenance_policy_rows = sorted(maintenance_policy_rows, key=lambda row: str(row.get("maintenance_policy_id", "")))

    return failure_mode_rows, maintenance_policy_rows, backlog_rule_rows, errors


def _commitment_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _commitment_record, commitment_rows_raw, commitment_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/commitment_type_registry.json",
        expected_schema_id="dominium.registry.commitment_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="commitment_types",
    )
    if commitment_load_errors:
        return [], [], commitment_load_errors

    _strictness_record, strictness_rows_raw, strictness_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/causality_strictness_registry.json",
        expected_schema_id="dominium.registry.causality_strictness_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="strictness_levels",
    )
    if strictness_load_errors:
        return [], [], strictness_load_errors

    strictness_rows: List[dict] = []
    strictness_ids = set()
    for entry in sorted(strictness_rows_raw, key=lambda row: str((row or {}).get("causality_strictness_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_causality_strictness_entry",
                    "message": "causality strictness entry must be object",
                    "path": "$.strictness_levels",
                }
            )
            continue
        strictness_id = str(entry.get("causality_strictness_id", "")).strip()
        if not strictness_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_causality_strictness_entry",
                    "message": "causality strictness entry missing causality_strictness_id",
                    "path": "$.strictness_levels.causality_strictness_id",
                }
            )
            continue
        if strictness_id in strictness_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_causality_strictness_id",
                    "message": "duplicate causality_strictness_id '{}'".format(strictness_id),
                    "path": "$.strictness_levels.causality_strictness_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="causality_strictness",
            payload=entry,
            path="data/registries/causality_strictness_registry.json#{}".format(strictness_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        level = str(entry.get("level", "")).strip()
        if level not in ("C0", "C1", "C2"):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_causality_strictness_entry",
                    "message": "causality strictness '{}' has unsupported level '{}'".format(strictness_id, level),
                    "path": "$.strictness_levels.level",
                }
            )
            continue
        strictness_ids.add(strictness_id)
        strictness_rows.append(
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": strictness_id,
                "level": level,
                "description": str(entry.get("description", "")).strip(),
                "major_change_requires_commitment": bool(entry.get("major_change_requires_commitment", False)),
                "event_required_for_macro_change": bool(entry.get("event_required_for_macro_change", True)),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    strictness_rows = sorted(strictness_rows, key=lambda row: str(row.get("causality_strictness_id", "")))

    commitment_rows: List[dict] = []
    commitment_type_ids = set()
    for entry in sorted(commitment_rows_raw, key=lambda row: str((row or {}).get("commitment_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_commitment_type_entry",
                    "message": "commitment type entry must be object",
                    "path": "$.commitment_types",
                }
            )
            continue
        commitment_type_id = str(entry.get("commitment_type_id", "")).strip()
        if not commitment_type_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_commitment_type_entry",
                    "message": "commitment type entry missing commitment_type_id",
                    "path": "$.commitment_types.commitment_type_id",
                }
            )
            continue
        if commitment_type_id in commitment_type_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_commitment_type_id",
                    "message": "duplicate commitment_type_id '{}'".format(commitment_type_id),
                    "path": "$.commitment_types.commitment_type_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="commitment_type",
            payload=entry,
            path="data/registries/commitment_type_registry.json#{}".format(commitment_type_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        strictness_requirements = _sorted_unique_strings(entry.get("strictness_requirements") or [])
        unknown_strictness = [token for token in strictness_requirements if token not in strictness_ids]
        if unknown_strictness:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_commitment_type_entry",
                    "message": "commitment type '{}' references unknown strictness id(s): {}".format(
                        commitment_type_id,
                        ",".join(unknown_strictness),
                    ),
                    "path": "$.commitment_types.strictness_requirements",
                }
            )
            continue
        commitment_type_ids.add(commitment_type_id)
        commitment_rows.append(
            {
                "schema_version": "1.0.0",
                "commitment_type_id": commitment_type_id,
                "description": str(entry.get("description", "")).strip(),
                "required_entitlements": _sorted_unique_strings(entry.get("required_entitlements") or []),
                "produces_event_type_ids": _sorted_unique_strings(entry.get("produces_event_type_ids") or []),
                "strictness_requirements": list(strictness_requirements),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    commitment_rows = sorted(commitment_rows, key=lambda row: str(row.get("commitment_type_id", "")))

    return commitment_rows, strictness_rows, errors


def _universe_physics_registry_rows(
    repo_root: str,
    schema_root: str,
    contributions: List[dict] | None = None,
    known_contract_set_ids: List[str] | None = None,
    known_budget_envelope_ids: List[str] | None = None,
    known_arbitration_policy_ids: List[str] | None = None,
    known_inspection_cache_policy_ids: List[str] | None = None,
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _time_record, time_rows_raw, time_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/time_model_registry.json",
        expected_schema_id="dominium.registry.time_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="time_models",
    )
    if time_load_errors:
        return [], [], [], [], [], time_load_errors

    _precision_record, precision_rows_raw, precision_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/numeric_precision_policy_registry.json",
        expected_schema_id="dominium.registry.numeric_precision_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="precision_policies",
    )
    if precision_load_errors:
        return [], [], [], [], [], precision_load_errors

    _taxonomy_record, taxonomy_rows_raw, taxonomy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/tier_taxonomy_registry.json",
        expected_schema_id="dominium.registry.tier_taxonomy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="taxonomies",
    )
    if taxonomy_load_errors:
        return [], [], [], [], [], taxonomy_load_errors

    _boundary_record, boundary_rows_raw, boundary_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/boundary_model_registry.json",
        expected_schema_id="dominium.registry.boundary_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="boundary_models",
    )
    if boundary_load_errors:
        return [], [], [], [], [], boundary_load_errors

    _profile_record, profile_rows_raw, profile_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/universe_physics_profile_registry.json",
        expected_schema_id="dominium.registry.universe_physics_profile_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="physics_profiles",
    )
    if profile_load_errors:
        return [], [], [], [], [], profile_load_errors

    contributed_profile_rows: List[dict] = []
    for row in sorted(
        [item for item in (contributions or []) if isinstance(item, dict)],
        key=lambda item: (str(item.get("id", "")), str(item.get("pack_id", ""))),
    ):
        if str(row.get("contrib_type", "")) != "registry_entries":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_universe_physics_profile_entry",
                    "message": err,
                    "path": "$.physics_profiles",
                }
            )
            continue
        if str(payload.get("entry_type", "")).strip() != "universe_physics_profile":
            continue
        profile_payload = payload.get("profile")
        if not isinstance(profile_payload, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_universe_physics_profile_entry",
                    "message": "registry_entries contribution '{}' must include object field profile".format(
                        str(row.get("id", ""))
                    ),
                    "path": "$.physics_profiles",
                }
            )
            continue
        contribution_id = str(row.get("id", "")).strip()
        profile_id = str(profile_payload.get("physics_profile_id", "")).strip()
        if contribution_id and profile_id and contribution_id != profile_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.universe_physics_profile_id_mismatch",
                    "message": "physics profile id '{}' does not match contribution id '{}'".format(
                        profile_id,
                        contribution_id,
                    ),
                    "path": "$.physics_profiles.physics_profile_id",
                }
            )
            continue
        contributed_profile_rows.append(dict(profile_payload))

    time_rows: List[dict] = []
    time_seen = set()
    for entry in sorted(time_rows_raw, key=lambda row: str((row or {}).get("time_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_time_model_entry",
                    "message": "time model entry must be object",
                    "path": "$.time_models",
                }
            )
            continue
        time_model_id = str(entry.get("time_model_id", "")).strip()
        if not time_model_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_time_model_entry",
                    "message": "time model id is missing",
                    "path": "$.time_models.time_model_id",
                }
            )
            continue
        if time_model_id in time_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_time_model_id",
                    "message": "duplicate time_model_id '{}'".format(time_model_id),
                    "path": "$.time_models.time_model_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="time_model",
            payload=entry,
            path="data/registries/time_model_registry.json#{}".format(time_model_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        time_seen.add(time_model_id)
        time_rows.append(dict(entry))
    time_rows = sorted(time_rows, key=lambda row: str(row.get("time_model_id", "")))

    precision_rows: List[dict] = []
    precision_seen = set()
    for entry in sorted(precision_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_numeric_precision_policy_entry",
                    "message": "numeric precision policy entry must be object",
                    "path": "$.precision_policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        if not policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_numeric_precision_policy_entry",
                    "message": "numeric precision policy id is missing",
                    "path": "$.precision_policies.policy_id",
                }
            )
            continue
        if policy_id in precision_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_numeric_precision_policy_id",
                    "message": "duplicate policy_id '{}'".format(policy_id),
                    "path": "$.precision_policies.policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="numeric_precision_policy",
            payload=entry,
            path="data/registries/numeric_precision_policy_registry.json#{}".format(policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        precision_seen.add(policy_id)
        precision_rows.append(dict(entry))
    precision_rows = sorted(precision_rows, key=lambda row: str(row.get("policy_id", "")))

    taxonomy_rows: List[dict] = []
    taxonomy_seen = set()
    for entry in sorted(taxonomy_rows_raw, key=lambda row: str((row or {}).get("taxonomy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_tier_taxonomy_entry",
                    "message": "tier taxonomy entry must be object",
                    "path": "$.taxonomies",
                }
            )
            continue
        taxonomy_id = str(entry.get("taxonomy_id", "")).strip()
        if not taxonomy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_tier_taxonomy_entry",
                    "message": "tier taxonomy id is missing",
                    "path": "$.taxonomies.taxonomy_id",
                }
            )
            continue
        if taxonomy_id in taxonomy_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_tier_taxonomy_id",
                    "message": "duplicate taxonomy_id '{}'".format(taxonomy_id),
                    "path": "$.taxonomies.taxonomy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="tier_taxonomy",
            payload=entry,
            path="data/registries/tier_taxonomy_registry.json#{}".format(taxonomy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        taxonomy_seen.add(taxonomy_id)
        taxonomy_rows.append(dict(entry))
    taxonomy_rows = sorted(taxonomy_rows, key=lambda row: str(row.get("taxonomy_id", "")))

    boundary_rows: List[dict] = []
    boundary_seen = set()
    for entry in sorted(boundary_rows_raw, key=lambda row: str((row or {}).get("boundary_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_boundary_model_entry",
                    "message": "boundary model entry must be object",
                    "path": "$.boundary_models",
                }
            )
            continue
        boundary_model_id = str(entry.get("boundary_model_id", "")).strip()
        if not boundary_model_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_boundary_model_entry",
                    "message": "boundary model id is missing",
                    "path": "$.boundary_models.boundary_model_id",
                }
            )
            continue
        if boundary_model_id in boundary_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_boundary_model_id",
                    "message": "duplicate boundary_model_id '{}'".format(boundary_model_id),
                    "path": "$.boundary_models.boundary_model_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="boundary_model",
            payload=entry,
            path="data/registries/boundary_model_registry.json#{}".format(boundary_model_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        boundary_seen.add(boundary_model_id)
        boundary_rows.append(dict(entry))
    boundary_rows = sorted(boundary_rows, key=lambda row: str(row.get("boundary_model_id", "")))

    time_model_ids = set(str(row.get("time_model_id", "")).strip() for row in time_rows)
    precision_policy_ids = set(str(row.get("policy_id", "")).strip() for row in precision_rows)
    taxonomy_ids = set(str(row.get("taxonomy_id", "")).strip() for row in taxonomy_rows)
    boundary_model_ids = set(str(row.get("boundary_model_id", "")).strip() for row in boundary_rows)
    contract_set_ids = set(str(item).strip() for item in (known_contract_set_ids or []) if str(item).strip())
    budget_envelope_ids = set(str(item).strip() for item in (known_budget_envelope_ids or []) if str(item).strip())
    arbitration_policy_ids = set(str(item).strip() for item in (known_arbitration_policy_ids or []) if str(item).strip())
    inspection_cache_policy_ids = set(
        str(item).strip() for item in (known_inspection_cache_policy_ids or []) if str(item).strip()
    )

    profile_rows: List[dict] = []
    profile_seen = set()
    profile_rows_input = list(profile_rows_raw) + list(contributed_profile_rows)
    for entry in sorted(profile_rows_input, key=lambda row: str((row or {}).get("physics_profile_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_universe_physics_profile_entry",
                    "message": "universe physics profile entry must be object",
                    "path": "$.physics_profiles",
                }
            )
            continue
        physics_profile_id = str(entry.get("physics_profile_id", "")).strip()
        if not physics_profile_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_universe_physics_profile_entry",
                    "message": "physics profile id is missing",
                    "path": "$.physics_profiles.physics_profile_id",
                }
            )
            continue
        if physics_profile_id in profile_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_universe_physics_profile_id",
                    "message": "duplicate physics_profile_id '{}'".format(physics_profile_id),
                    "path": "$.physics_profiles.physics_profile_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="universe_physics_profile",
            payload=entry,
            path="data/registries/universe_physics_profile_registry.json#{}".format(physics_profile_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        missing_refs: List[str] = []
        if str(entry.get("time_model_id", "")).strip() not in time_model_ids:
            missing_refs.append("time_model_id={}".format(str(entry.get("time_model_id", "")).strip()))
        if str(entry.get("numeric_precision_policy_id", "")).strip() not in precision_policy_ids:
            missing_refs.append(
                "numeric_precision_policy_id={}".format(str(entry.get("numeric_precision_policy_id", "")).strip())
            )
        if str(entry.get("tier_taxonomy_id", "")).strip() not in taxonomy_ids:
            missing_refs.append("tier_taxonomy_id={}".format(str(entry.get("tier_taxonomy_id", "")).strip()))
        if str(entry.get("boundary_model_id", "")).strip() not in boundary_model_ids:
            missing_refs.append("boundary_model_id={}".format(str(entry.get("boundary_model_id", "")).strip()))
        if contract_set_ids and str(entry.get("conservation_contract_set_id", "")).strip() not in contract_set_ids:
            missing_refs.append(
                "conservation_contract_set_id={}".format(str(entry.get("conservation_contract_set_id", "")).strip())
            )
        if budget_envelope_ids and str(entry.get("budget_envelope_id", "")).strip() not in budget_envelope_ids:
            missing_refs.append("budget_envelope_id={}".format(str(entry.get("budget_envelope_id", "")).strip()))
        if arbitration_policy_ids and str(entry.get("arbitration_policy_id", "")).strip() not in arbitration_policy_ids:
            missing_refs.append(
                "arbitration_policy_id={}".format(str(entry.get("arbitration_policy_id", "")).strip())
            )
        if (
            inspection_cache_policy_ids
            and str(entry.get("inspection_cache_policy_id", "")).strip() not in inspection_cache_policy_ids
        ):
            missing_refs.append(
                "inspection_cache_policy_id={}".format(str(entry.get("inspection_cache_policy_id", "")).strip())
            )
        if missing_refs:
            errors.append(
                {
                    "code": "refuse.registry_compile.universe_physics_profile_reference_missing",
                    "message": "physics profile '{}' references unknown ids: {}".format(
                        physics_profile_id,
                        ",".join(sorted(missing_refs)),
                    ),
                    "path": "$.physics_profiles",
                }
            )
            continue

        profile_seen.add(physics_profile_id)
        profile_rows.append(dict(entry))
    profile_rows = sorted(profile_rows, key=lambda row: str(row.get("physics_profile_id", "")))

    return profile_rows, time_rows, precision_rows, taxonomy_rows, boundary_rows, errors


def _transition_policy_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _policy_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/transition_policy_registry.json",
        expected_schema_id="dominium.registry.transition_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], policy_load_errors

    _arb_record, arb_rows_raw, arb_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/arbitration_rule_registry.json",
        expected_schema_id="dominium.registry.arbitration_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="rules",
    )
    if arb_load_errors:
        return [], [], arb_load_errors

    arbitration_rule_rows: List[dict] = []
    arbitration_rule_seen = set()
    for entry in sorted(arb_rows_raw, key=lambda row: str((row or {}).get("rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_arbitration_rule_entry",
                    "message": "arbitration rule entry must be object",
                    "path": "$.rules",
                }
            )
            continue
        rule_id = str(entry.get("rule_id", "")).strip()
        description = str(entry.get("description", "")).strip()
        extensions = entry.get("extensions")
        if not rule_id or not description or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_arbitration_rule_entry",
                    "message": "arbitration rule entry missing required fields",
                    "path": "$.rules",
                }
            )
            continue
        if rule_id in arbitration_rule_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_arbitration_rule_id",
                    "message": "duplicate arbitration rule_id '{}'".format(rule_id),
                    "path": "$.rules.rule_id",
                }
            )
            continue
        arbitration_rule_seen.add(rule_id)
        arbitration_rule_rows.append(
            {
                "rule_id": rule_id,
                "description": description,
                "extensions": dict(extensions),
            }
        )
    arbitration_rule_rows = sorted(arbitration_rule_rows, key=lambda row: str(row.get("rule_id", "")))
    arbitration_rule_ids = set(str(row.get("rule_id", "")).strip() for row in arbitration_rule_rows)

    transition_policy_rows: List[dict] = []
    transition_policy_seen = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("transition_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_transition_policy_entry",
                    "message": "transition policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        transition_policy_id = str(entry.get("transition_policy_id", "")).strip()
        if not transition_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_transition_policy_entry",
                    "message": "transition policy id is missing",
                    "path": "$.policies.transition_policy_id",
                }
            )
            continue
        if transition_policy_id in transition_policy_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_transition_policy_id",
                    "message": "duplicate transition_policy_id '{}'".format(transition_policy_id),
                    "path": "$.policies.transition_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="transition_policy",
            payload=entry,
            path="data/registries/transition_policy_registry.json#{}".format(transition_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        arbitration_rule_id = str(entry.get("arbitration_rule_id", "")).strip()
        if arbitration_rule_id not in arbitration_rule_ids:
            errors.append(
                {
                    "code": "refuse.registry_compile.transition_policy_arbitration_rule_missing",
                    "message": "transition policy '{}' references unknown arbitration rule '{}'".format(
                        transition_policy_id,
                        arbitration_rule_id or "<empty>",
                    ),
                    "path": "$.policies.arbitration_rule_id",
                }
            )
            continue
        transition_policy_seen.add(transition_policy_id)
        transition_policy_rows.append(
            {
                "schema_version": str(entry.get("schema_version", "")).strip(),
                "transition_policy_id": transition_policy_id,
                "description": str(entry.get("description", "")).strip(),
                "max_micro_regions": int(entry.get("max_micro_regions", 0) or 0),
                "max_micro_entities": int(entry.get("max_micro_entities", 0) or 0),
                "hysteresis_rules": dict(entry.get("hysteresis_rules") or {}),
                "arbitration_rule_id": arbitration_rule_id,
                "degrade_order": [str(item).strip() for item in list(entry.get("degrade_order") or []) if str(item).strip()],
                "refuse_thresholds": dict(entry.get("refuse_thresholds") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
    transition_policy_rows = sorted(
        transition_policy_rows, key=lambda row: str(row.get("transition_policy_id", ""))
    )
    return transition_policy_rows, arbitration_rule_rows, errors


def _performance_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _envelope_record, envelope_rows_raw, envelope_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/budget_envelope_registry.json",
        expected_schema_id="dominium.registry.budget_envelope_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="envelopes",
    )
    if envelope_load_errors:
        return [], [], [], envelope_load_errors

    _arbitration_record, arbitration_rows_raw, arbitration_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/arbitration_policy_registry.json",
        expected_schema_id="dominium.registry.arbitration_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if arbitration_load_errors:
        return [], [], [], arbitration_load_errors

    _inspection_record, inspection_rows_raw, inspection_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/inspection_cache_policy_registry.json",
        expected_schema_id="dominium.registry.inspection_cache_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if inspection_load_errors:
        return [], [], [], inspection_load_errors

    budget_envelope_rows: List[dict] = []
    envelope_seen = set()
    for entry in sorted(envelope_rows_raw, key=lambda row: str((row or {}).get("envelope_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_budget_envelope_entry",
                    "message": "budget envelope entry must be object",
                    "path": "$.envelopes",
                }
            )
            continue
        envelope_id = str(entry.get("envelope_id", "")).strip()
        if not envelope_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_budget_envelope_entry",
                    "message": "budget envelope id is missing",
                    "path": "$.envelopes.envelope_id",
                }
            )
            continue
        if envelope_id in envelope_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_budget_envelope_id",
                    "message": "duplicate envelope_id '{}'".format(envelope_id),
                    "path": "$.envelopes.envelope_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="budget_envelope",
            payload=entry,
            path="data/registries/budget_envelope_registry.json#{}".format(envelope_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        envelope_seen.add(envelope_id)
        budget_envelope_rows.append(dict(entry))
    budget_envelope_rows = sorted(budget_envelope_rows, key=lambda row: str(row.get("envelope_id", "")))

    arbitration_policy_rows: List[dict] = []
    arbitration_seen = set()
    for entry in sorted(arbitration_rows_raw, key=lambda row: str((row or {}).get("arbitration_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_arbitration_policy_entry",
                    "message": "arbitration policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        arbitration_policy_id = str(entry.get("arbitration_policy_id", "")).strip()
        if not arbitration_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_arbitration_policy_entry",
                    "message": "arbitration policy id is missing",
                    "path": "$.policies.arbitration_policy_id",
                }
            )
            continue
        if arbitration_policy_id in arbitration_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_arbitration_policy_id",
                    "message": "duplicate arbitration_policy_id '{}'".format(arbitration_policy_id),
                    "path": "$.policies.arbitration_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="arbitration_policy",
            payload=entry,
            path="data/registries/arbitration_policy_registry.json#{}".format(arbitration_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        arbitration_seen.add(arbitration_policy_id)
        arbitration_policy_rows.append(dict(entry))
    arbitration_policy_rows = sorted(
        arbitration_policy_rows,
        key=lambda row: str(row.get("arbitration_policy_id", "")),
    )

    inspection_cache_policy_rows: List[dict] = []
    inspection_seen = set()
    for entry in sorted(inspection_rows_raw, key=lambda row: str((row or {}).get("cache_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_inspection_cache_policy_entry",
                    "message": "inspection cache policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        cache_policy_id = str(entry.get("cache_policy_id", "")).strip()
        if not cache_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_inspection_cache_policy_entry",
                    "message": "inspection cache policy id is missing",
                    "path": "$.policies.cache_policy_id",
                }
            )
            continue
        if cache_policy_id in inspection_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_inspection_cache_policy_id",
                    "message": "duplicate cache_policy_id '{}'".format(cache_policy_id),
                    "path": "$.policies.cache_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="inspection_cache_policy",
            payload=entry,
            path="data/registries/inspection_cache_policy_registry.json#{}".format(cache_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        inspection_seen.add(cache_policy_id)
        inspection_cache_policy_rows.append(dict(entry))
    inspection_cache_policy_rows = sorted(
        inspection_cache_policy_rows,
        key=lambda row: str(row.get("cache_policy_id", "")),
    )

    return budget_envelope_rows, arbitration_policy_rows, inspection_cache_policy_rows, errors


def _inspection_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict]]:
    errors: List[dict] = []
    _inspection_record, section_rows_raw, section_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/inspection_section_registry.json",
        expected_schema_id="dominium.registry.inspection_section_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="sections",
    )
    if section_load_errors:
        return [], section_load_errors

    section_rows: List[dict] = []
    section_seen = set()
    for entry in sorted(section_rows_raw, key=lambda row: str((row or {}).get("section_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_inspection_section_entry",
                    "message": "inspection section entry must be object",
                    "path": "$.sections",
                }
            )
            continue
        section_id = str(entry.get("section_id", "")).strip()
        if not section_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_inspection_section_entry",
                    "message": "inspection section id is missing",
                    "path": "$.sections.section_id",
                }
            )
            continue
        if section_id in section_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_inspection_section_id",
                    "message": "duplicate section_id '{}'".format(section_id),
                    "path": "$.sections.section_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="inspection_section",
            payload=entry,
            path="data/registries/inspection_section_registry.json#{}".format(section_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        section_seen.add(section_id)
        section_rows.append(dict(entry))

    section_rows = sorted(section_rows, key=lambda row: str(row.get("section_id", "")))
    return section_rows, errors


def _time_control_registry_rows(
    repo_root: str,
    schema_root: str,
    known_time_model_ids: List[str] | None = None,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _dt_rule_record, dt_rule_rows_raw, dt_rule_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/dt_quantization_rule_registry.json",
        expected_schema_id="dominium.registry.dt_quantization_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="rules",
    )
    if dt_rule_load_errors:
        return [], [], [], dt_rule_load_errors

    _compaction_record, compaction_rows_raw, compaction_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/compaction_policy_registry.json",
        expected_schema_id="dominium.registry.compaction_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if compaction_load_errors:
        return [], [], [], compaction_load_errors

    _time_control_record, time_control_rows_raw, time_control_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/time_control_policy_registry.json",
        expected_schema_id="dominium.registry.time_control_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if time_control_load_errors:
        return [], [], [], time_control_load_errors

    dt_rule_rows: List[dict] = []
    dt_rule_seen = set()
    for entry in sorted(dt_rule_rows_raw, key=lambda row: str((row or {}).get("dt_rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_dt_quantization_rule_entry",
                    "message": "dt quantization rule entry must be object",
                    "path": "$.rules",
                }
            )
            continue
        dt_rule_id = str(entry.get("dt_rule_id", "")).strip()
        if not dt_rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_dt_quantization_rule_entry",
                    "message": "dt quantization rule id is missing",
                    "path": "$.rules.dt_rule_id",
                }
            )
            continue
        if dt_rule_id in dt_rule_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_dt_quantization_rule_id",
                    "message": "duplicate dt_rule_id '{}'".format(dt_rule_id),
                    "path": "$.rules.dt_rule_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="dt_quantization_rule",
            payload=entry,
            path="data/registries/dt_quantization_rule_registry.json#{}".format(dt_rule_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        allowed_dt_values = []
        for raw_value in list(entry.get("allowed_dt_values") or []):
            try:
                value = int(raw_value)
            except (TypeError, ValueError):
                continue
            if value > 0:
                allowed_dt_values.append(value)
        allowed_dt_values = sorted(set(allowed_dt_values))
        default_dt = int(entry.get("default_dt", 0) or 0)
        if default_dt not in set(allowed_dt_values):
            errors.append(
                {
                    "code": "refuse.registry_compile.dt_quantization_default_not_allowed",
                    "message": "dt rule '{}' default_dt must be present in allowed_dt_values".format(dt_rule_id),
                    "path": "$.rules.default_dt",
                }
            )
            continue
        dt_rule_seen.add(dt_rule_id)
        normalized_entry = dict(entry)
        normalized_entry["allowed_dt_values"] = list(allowed_dt_values)
        dt_rule_rows.append(normalized_entry)
    dt_rule_rows = sorted(dt_rule_rows, key=lambda row: str(row.get("dt_rule_id", "")))

    compaction_rows: List[dict] = []
    compaction_seen = set()
    for entry in sorted(compaction_rows_raw, key=lambda row: str((row or {}).get("compaction_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_compaction_policy_entry",
                    "message": "compaction policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        compaction_policy_id = str(entry.get("compaction_policy_id", "")).strip()
        if not compaction_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_compaction_policy_entry",
                    "message": "compaction policy id is missing",
                    "path": "$.policies.compaction_policy_id",
                }
            )
            continue
        if compaction_policy_id in compaction_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_compaction_policy_id",
                    "message": "duplicate compaction_policy_id '{}'".format(compaction_policy_id),
                    "path": "$.policies.compaction_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="compaction_policy",
            payload=entry,
            path="data/registries/compaction_policy_registry.json#{}".format(compaction_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        rules = dict(entry.get("rules") or {})
        if int(rules.get("keep_every_nth_checkpoint", 0) or 0) < 1:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_compaction_policy_entry",
                    "message": "compaction policy '{}' requires keep_every_nth_checkpoint >= 1".format(compaction_policy_id),
                    "path": "$.policies.rules.keep_every_nth_checkpoint",
                }
            )
            continue
        compaction_seen.add(compaction_policy_id)
        compaction_rows.append(dict(entry))
    compaction_rows = sorted(compaction_rows, key=lambda row: str(row.get("compaction_policy_id", "")))

    dt_rule_ids = set(str(row.get("dt_rule_id", "")).strip() for row in dt_rule_rows)
    compaction_policy_ids = set(str(row.get("compaction_policy_id", "")).strip() for row in compaction_rows)
    known_time_models = set(str(item).strip() for item in (known_time_model_ids or []) if str(item).strip())

    time_control_rows: List[dict] = []
    time_control_seen = set()
    for entry in sorted(time_control_rows_raw, key=lambda row: str((row or {}).get("time_control_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_time_control_policy_entry",
                    "message": "time control policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        time_control_policy_id = str(entry.get("time_control_policy_id", "")).strip()
        if not time_control_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_time_control_policy_entry",
                    "message": "time control policy id is missing",
                    "path": "$.policies.time_control_policy_id",
                }
            )
            continue
        if time_control_policy_id in time_control_seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_time_control_policy_id",
                    "message": "duplicate time_control_policy_id '{}'".format(time_control_policy_id),
                    "path": "$.policies.time_control_policy_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="time_control_policy",
            payload=entry,
            path="data/registries/time_control_policy_registry.json#{}".format(time_control_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        missing_refs = []
        dt_rule_id = str(entry.get("dt_quantization_rule_id", "")).strip()
        if dt_rule_id not in dt_rule_ids:
            missing_refs.append("dt_quantization_rule_id={}".format(dt_rule_id))
        compaction_policy_id = str(entry.get("compaction_policy_id", "")).strip()
        if compaction_policy_id not in compaction_policy_ids:
            missing_refs.append("compaction_policy_id={}".format(compaction_policy_id))
        allowed_rate_range = dict(entry.get("allowed_rate_range") or {})
        min_rate = int(allowed_rate_range.get("min", 0) or 0)
        max_rate = int(allowed_rate_range.get("max", 0) or 0)
        if min_rate > max_rate:
            missing_refs.append("allowed_rate_range=min_gt_max")
        extensions = dict(entry.get("extensions") or {})
        allowed_time_model_ids = sorted(
            set(str(item).strip() for item in (extensions.get("allowed_time_model_ids") or []) if str(item).strip())
        )
        if known_time_models and allowed_time_model_ids:
            for time_model_id in allowed_time_model_ids:
                if time_model_id not in known_time_models:
                    missing_refs.append("allowed_time_model_ids={}".format(time_model_id))
        if missing_refs:
            errors.append(
                {
                    "code": "refuse.registry_compile.time_control_policy_reference_missing",
                    "message": "time control policy '{}' references unknown ids: {}".format(
                        time_control_policy_id,
                        ",".join(sorted(set(missing_refs))),
                    ),
                    "path": "$.policies",
                }
            )
            continue
        time_control_seen.add(time_control_policy_id)
        time_control_rows.append(dict(entry))
    time_control_rows = sorted(time_control_rows, key=lambda row: str(row.get("time_control_policy_id", "")))

    return time_control_rows, dt_rule_rows, compaction_rows, errors


def _body_shape_registry_rows(repo_root: str) -> Tuple[List[dict], List[dict]]:
    _body_record, body_rows_raw, load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/body_shape_registry.json",
        expected_schema_id="dominium.registry.body_shape_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="shape_types",
    )
    if load_errors:
        return [], load_errors

    errors: List[dict] = []
    rows: List[dict] = []
    seen = set()
    for entry in sorted(body_rows_raw, key=lambda row: str((row or {}).get("shape_type", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_body_shape_entry",
                    "message": "body shape entry must be object",
                    "path": "$.shape_types",
                }
            )
            continue
        shape_type = str(entry.get("shape_type", "")).strip()
        required_parameters = entry.get("required_parameters")
        parameter_constraints = entry.get("parameter_constraints")
        extensions = entry.get("extensions")
        if (
            shape_type not in ("capsule", "aabb", "convex_hull")
            or not isinstance(required_parameters, list)
            or not isinstance(parameter_constraints, dict)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_body_shape_entry",
                    "message": "body shape '{}' missing required fields".format(shape_type or "<missing>"),
                    "path": "$.shape_types",
                }
            )
            continue
        if shape_type in seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_body_shape_type",
                    "message": "duplicate body shape_type '{}'".format(shape_type),
                    "path": "$.shape_types.shape_type",
                }
            )
            continue
        seen.add(shape_type)
        constraints_row: Dict[str, dict] = {}
        for key in sorted(parameter_constraints.keys()):
            value = parameter_constraints.get(key)
            if isinstance(value, dict):
                constraints_row[str(key)] = dict(value)
        rows.append(
            {
                "shape_type": shape_type,
                "required_parameters": _sorted_unique_strings(required_parameters),
                "parameter_constraints": constraints_row,
                "supports_dynamic": bool(entry.get("supports_dynamic", True)),
                "supports_ghost": bool(entry.get("supports_ghost", True)),
                "notes": str(entry.get("notes", "")).strip(),
                "extensions": dict(extensions),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("shape_type", ""))), errors


def _view_mode_registry_rows(repo_root: str) -> Tuple[List[dict], List[dict]]:
    _view_record, view_rows_raw, load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/view_mode_registry.json",
        expected_schema_id="dominium.registry.view_mode_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="view_modes",
    )
    if load_errors:
        return [], load_errors

    errors: List[dict] = []
    rows: List[dict] = []
    seen = set()
    allowed_policy_values = {"lockstep", "authoritative", "hybrid"}
    for entry in sorted(view_rows_raw, key=lambda row: str((row or {}).get("view_mode_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_view_mode_entry",
                    "message": "view mode entry must be object",
                    "path": "$.view_modes",
                }
            )
            continue
        view_mode_id = str(entry.get("view_mode_id", "")).strip()
        allowed_lens_ids = entry.get("allowed_lens_ids")
        allowed_in_policies = entry.get("allowed_in_policies")
        required_entitlements = entry.get("required_entitlements")
        extensions = entry.get("extensions")
        if (
            not view_mode_id
            or not isinstance(allowed_lens_ids, list)
            or not isinstance(allowed_in_policies, list)
            or not isinstance(required_entitlements, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_view_mode_entry",
                    "message": "view mode '{}' missing required fields".format(view_mode_id or "<missing>"),
                    "path": "$.view_modes",
                }
            )
            continue
        if view_mode_id in seen:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_view_mode_id",
                    "message": "duplicate view_mode_id '{}'".format(view_mode_id),
                    "path": "$.view_modes.view_mode_id",
                }
            )
            continue
        policy_tokens = _sorted_unique_strings(allowed_in_policies)
        unknown_policies = [token for token in policy_tokens if token not in allowed_policy_values]
        if unknown_policies:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_view_mode_policy",
                    "message": "view mode '{}' references unknown policy tags: {}".format(
                        view_mode_id,
                        ",".join(sorted(unknown_policies)),
                    ),
                    "path": "$.view_modes.allowed_in_policies",
                }
            )
            continue
        seen.add(view_mode_id)
        watermark_policy_id = entry.get("watermark_policy_id")
        if watermark_policy_id is not None:
            watermark_policy_id = str(watermark_policy_id).strip() or None
        rows.append(
            {
                "view_mode_id": view_mode_id,
                "description": str(entry.get("description", "")).strip(),
                "allowed_lens_ids": _sorted_unique_strings(allowed_lens_ids),
                "requires_embodiment": bool(entry.get("requires_embodiment", False)),
                "allowed_in_policies": policy_tokens,
                "required_entitlements": _sorted_unique_strings(required_entitlements),
                "watermark_policy_id": watermark_policy_id,
                "extensions": dict(extensions),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("view_mode_id", ""))), errors


def _diegetic_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _calib_record, calibration_rows_raw, calibration_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/calibration_model_registry.json",
        expected_schema_id="dominium.registry.calibration_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="calibration_models",
    )
    if calibration_load_errors:
        return [], [], calibration_load_errors

    calibration_rows: List[dict] = []
    calibration_model_id_set = set()
    for entry in sorted(calibration_rows_raw, key=lambda row: str((row or {}).get("calibration_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_calibration_model_entry",
                    "message": "calibration model entry must be object",
                    "path": "$.calibration_models",
                }
            )
            continue
        calibration_model_id = str(entry.get("calibration_model_id", "")).strip()
        if not calibration_model_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_calibration_model_entry",
                    "message": "calibration model entry missing calibration_model_id",
                    "path": "$.calibration_models.calibration_model_id",
                }
            )
            continue
        if calibration_model_id in calibration_model_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_calibration_model_id",
                    "message": "duplicate calibration_model_id '{}'".format(calibration_model_id),
                    "path": "$.calibration_models.calibration_model_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="calibration_model",
            payload=schema_payload,
            path="data/registries/calibration_model_registry.json#{}".format(calibration_model_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        parameters = entry.get("parameters")
        if not isinstance(parameters, dict):
            parameters = {}
        calibration_rows.append(
            {
                "calibration_model_id": calibration_model_id,
                "description": str(entry.get("description", "")).strip(),
                "model_kind": str(entry.get("model_kind", "")).strip(),
                "parameters": dict((str(key), parameters[key]) for key in sorted(parameters.keys())),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        calibration_model_id_set.add(calibration_model_id)
    calibration_rows = sorted(calibration_rows, key=lambda row: str(row.get("calibration_model_id", "")))

    _instrument_record, instrument_rows_raw, instrument_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/instrument_type_registry.json",
        expected_schema_id="dominium.registry.instrument_type_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="instrument_types",
    )
    if instrument_load_errors:
        return [], [], instrument_load_errors

    instrument_rows: List[dict] = []
    instrument_type_id_set = set()
    for entry in sorted(instrument_rows_raw, key=lambda row: str((row or {}).get("instrument_type_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_instrument_type_entry",
                    "message": "instrument type entry must be object",
                    "path": "$.instrument_types",
                }
            )
            continue
        instrument_type_id = str(entry.get("instrument_type_id", "")).strip()
        if not instrument_type_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_instrument_type_entry",
                    "message": "instrument type entry missing instrument_type_id",
                    "path": "$.instrument_types.instrument_type_id",
                }
            )
            continue
        if instrument_type_id in instrument_type_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_instrument_type_id",
                    "message": "duplicate instrument_type_id '{}'".format(instrument_type_id),
                    "path": "$.instrument_types.instrument_type_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="instrument_type",
            payload=schema_payload,
            path="data/registries/instrument_type_registry.json#{}".format(instrument_type_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        calibration_model_id = entry.get("calibration_model_id")
        calibration_model_token = None
        if calibration_model_id is not None:
            calibration_model_token = str(calibration_model_id).strip() or None
        if calibration_model_token and calibration_model_token not in calibration_model_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.instrument_calibration_model_missing",
                    "message": "instrument type '{}' references unknown calibration_model_id '{}'".format(
                        instrument_type_id,
                        calibration_model_token,
                    ),
                    "path": "$.instrument_types.calibration_model_id",
                }
            )
            continue
        instrument_rows.append(
            {
                "instrument_type_id": instrument_type_id,
                "description": str(entry.get("description", "")).strip(),
                "required_channels_in": _sorted_unique_strings(list(entry.get("required_channels_in") or [])),
                "produced_channels_out": _sorted_unique_strings(list(entry.get("produced_channels_out") or [])),
                "update_process_id": str(entry.get("update_process_id", "")).strip(),
                "calibration_model_id": calibration_model_token,
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        instrument_type_id_set.add(instrument_type_id)
    instrument_rows = sorted(instrument_rows, key=lambda row: str(row.get("instrument_type_id", "")))
    return instrument_rows, calibration_rows, errors


def _representation_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _render_record, render_rows_raw, render_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/render_proxy_registry.json",
        expected_schema_id="dominium.registry.render_proxy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="render_proxies",
    )
    if render_load_errors:
        return [], [], [], [], [], [], [], [], render_load_errors

    render_proxy_rows: List[dict] = []
    render_proxy_id_set = set()
    for entry in sorted(render_rows_raw, key=lambda row: str((row or {}).get("render_proxy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_render_proxy_entry",
                    "message": "render proxy entry must be object",
                    "path": "$.render_proxies",
                }
            )
            continue
        render_proxy_id = str(entry.get("render_proxy_id", "")).strip()
        if not render_proxy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_render_proxy_entry",
                    "message": "render proxy entry missing render_proxy_id",
                    "path": "$.render_proxies.render_proxy_id",
                }
            )
            continue
        if render_proxy_id in render_proxy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_render_proxy_id",
                    "message": "duplicate render_proxy_id '{}'".format(render_proxy_id),
                    "path": "$.render_proxies.render_proxy_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="render_proxy",
            payload=schema_payload,
            path="data/registries/render_proxy_registry.json#{}".format(render_proxy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        bounds_override = entry.get("bounds_override")
        if isinstance(bounds_override, dict):
            bounds_row = {
                "x_mm": int(bounds_override.get("x_mm", 0) or 0),
                "y_mm": int(bounds_override.get("y_mm", 0) or 0),
                "z_mm": int(bounds_override.get("z_mm", 0) or 0),
            }
        else:
            bounds_row = None
        lod_set_ref = entry.get("lod_set_ref")
        if lod_set_ref is not None:
            lod_set_ref = str(lod_set_ref).strip() or None
        render_proxy_rows.append(
            {
                "render_proxy_id": render_proxy_id,
                "supported_body_shapes": _sorted_unique_strings(list(entry.get("supported_body_shapes") or [])),
                "mesh_ref": str(entry.get("mesh_ref", "")).strip(),
                "material_ref": str(entry.get("material_ref", "")).strip(),
                "lod_set_ref": lod_set_ref,
                "bounds_override": bounds_row,
                "attachments_allowed": _sorted_unique_strings(list(entry.get("attachments_allowed") or [])),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        render_proxy_id_set.add(render_proxy_id)
    render_proxy_rows = sorted(render_proxy_rows, key=lambda row: str(row.get("render_proxy_id", "")))

    _cosmetic_record, cosmetic_rows_raw, cosmetic_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/cosmetic_registry.json",
        expected_schema_id="dominium.registry.cosmetic_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="cosmetics",
    )
    if cosmetic_load_errors:
        return [], [], [], [], [], [], [], [], cosmetic_load_errors

    cosmetic_rows: List[dict] = []
    cosmetic_id_set = set()
    for entry in sorted(cosmetic_rows_raw, key=lambda row: str((row or {}).get("cosmetic_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cosmetic_entry",
                    "message": "cosmetic entry must be object",
                    "path": "$.cosmetics",
                }
            )
            continue
        cosmetic_id = str(entry.get("cosmetic_id", "")).strip()
        render_proxy_id = str(entry.get("render_proxy_id", "")).strip()
        attachments = entry.get("attachments")
        tags = entry.get("tags")
        extensions = entry.get("extensions")
        if (
            not cosmetic_id
            or not render_proxy_id
            or not isinstance(attachments, list)
            or not isinstance(tags, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cosmetic_entry",
                    "message": "cosmetic entry missing required fields",
                    "path": "$.cosmetics",
                }
            )
            continue
        if cosmetic_id in cosmetic_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_cosmetic_id",
                    "message": "duplicate cosmetic_id '{}'".format(cosmetic_id),
                    "path": "$.cosmetics.cosmetic_id",
                }
            )
            continue
        if render_proxy_id not in render_proxy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.cosmetic_render_proxy_missing",
                    "message": "cosmetic '{}' references unknown render_proxy_id '{}'".format(
                        cosmetic_id,
                        render_proxy_id,
                    ),
                    "path": "$.cosmetics.render_proxy_id",
                }
            )
            continue
        mesh_ref_override = entry.get("mesh_ref_override")
        if mesh_ref_override is not None:
            mesh_ref_override = str(mesh_ref_override).strip() or None
        material_ref_override = entry.get("material_ref_override")
        if material_ref_override is not None:
            material_ref_override = str(material_ref_override).strip() or None
        cosmetic_rows.append(
            {
                "cosmetic_id": cosmetic_id,
                "render_proxy_id": render_proxy_id,
                "mesh_ref_override": mesh_ref_override,
                "material_ref_override": material_ref_override,
                "attachments": _sorted_unique_strings(attachments),
                "tags": _sorted_unique_strings(tags),
                "extensions": dict(extensions),
            }
        )
        cosmetic_id_set.add(cosmetic_id)
    cosmetic_rows = sorted(cosmetic_rows, key=lambda row: str(row.get("cosmetic_id", "")))

    _policy_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/cosmetic_policy_registry.json",
        expected_schema_id="dominium.registry.cosmetic_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], [], [], [], [], [], [], policy_load_errors

    cosmetic_policy_rows: List[dict] = []
    policy_id_set = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cosmetic_policy_entry",
                    "message": "cosmetic policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        allowed_cosmetic_ids = entry.get("allowed_cosmetic_ids")
        allowed_pack_ids = entry.get("allowed_pack_ids")
        refusal_codes = entry.get("refusal_codes")
        extensions = entry.get("extensions")
        if (
            not policy_id
            or not isinstance(allowed_cosmetic_ids, list)
            or not isinstance(allowed_pack_ids, list)
            or not isinstance(refusal_codes, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cosmetic_policy_entry",
                    "message": "cosmetic policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        if policy_id in policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_cosmetic_policy_id",
                    "message": "duplicate cosmetic policy_id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue
        allow_unsigned_packs = bool(entry.get("allow_unsigned_packs", False))
        require_signed_packs = bool(entry.get("require_signed_packs", False))
        if allow_unsigned_packs and require_signed_packs:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_cosmetic_policy_signing",
                    "message": "cosmetic policy '{}' cannot allow unsigned and require signed packs simultaneously".format(
                        policy_id
                    ),
                    "path": "$.policies",
                }
            )
            continue
        allowed_cosmetics = _sorted_unique_strings(allowed_cosmetic_ids)
        unknown_cosmetics = [token for token in allowed_cosmetics if token not in cosmetic_id_set]
        if unknown_cosmetics:
            errors.append(
                {
                    "code": "refuse.registry_compile.cosmetic_policy_cosmetic_missing",
                    "message": "cosmetic policy '{}' references unknown cosmetic ids: {}".format(
                        policy_id,
                        ",".join(sorted(unknown_cosmetics)),
                    ),
                    "path": "$.policies.allowed_cosmetic_ids",
                }
            )
            continue
        cosmetic_policy_rows.append(
            {
                "policy_id": policy_id,
                "description": str(entry.get("description", "")).strip(),
                "allow_unsigned_packs": allow_unsigned_packs,
                "require_signed_packs": require_signed_packs,
                "allowed_cosmetic_ids": allowed_cosmetics,
                "allowed_pack_ids": _sorted_unique_strings(allowed_pack_ids),
                "refusal_codes": _sorted_unique_strings(refusal_codes),
                "extensions": dict(extensions),
            }
        )
        policy_id_set.add(policy_id)
    cosmetic_policy_rows = sorted(cosmetic_policy_rows, key=lambda row: str(row.get("policy_id", "")))

    _primitive_record, primitive_rows_raw, primitive_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/render_primitive_registry.json",
        expected_schema_id="dominium.registry.render_primitive_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="primitives",
    )
    if primitive_load_errors:
        return [], [], [], [], [], [], [], [], primitive_load_errors

    render_primitive_rows: List[dict] = []
    render_primitive_id_set = set()
    for entry in sorted(primitive_rows_raw, key=lambda row: str((row or {}).get("primitive_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_render_primitive_entry",
                    "message": "render primitive entry must be object",
                    "path": "$.primitives",
                }
            )
            continue
        primitive_id = str(entry.get("primitive_id", "")).strip()
        if not primitive_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_render_primitive_entry",
                    "message": "render primitive entry missing primitive_id",
                    "path": "$.primitives.primitive_id",
                }
            )
            continue
        if primitive_id in render_primitive_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_render_primitive_id",
                    "message": "duplicate render primitive id '{}'".format(primitive_id),
                    "path": "$.primitives.primitive_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="render_primitive",
            payload=schema_payload,
            path="data/registries/render_primitive_registry.json#{}".format(primitive_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        render_primitive_rows.append(
            {
                "primitive_id": primitive_id,
                "primitive_type": str(entry.get("primitive_type", "")).strip(),
                "parameters": dict(entry.get("parameters") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        render_primitive_id_set.add(primitive_id)
    render_primitive_rows = sorted(render_primitive_rows, key=lambda row: str(row.get("primitive_id", "")))

    _template_record, template_rows_raw, template_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/procedural_material_template_registry.json",
        expected_schema_id="dominium.registry.procedural_material_template_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="material_templates",
    )
    if template_load_errors:
        return [], [], [], [], [], [], [], [], template_load_errors

    material_template_rows: List[dict] = []
    material_template_id_set = set()
    for entry in sorted(template_rows_raw, key=lambda row: str((row or {}).get("template_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_material_template_entry",
                    "message": "material template entry must be object",
                    "path": "$.material_templates",
                }
            )
            continue
        template_id = str(entry.get("template_id", "")).strip()
        if not template_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_material_template_entry",
                    "message": "material template entry missing template_id",
                    "path": "$.material_templates.template_id",
                }
            )
            continue
        if template_id in material_template_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_material_template_id",
                    "message": "duplicate material template id '{}'".format(template_id),
                    "path": "$.material_templates.template_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="material_template",
            payload=schema_payload,
            path="data/registries/procedural_material_template_registry.json#{}".format(template_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        material_template_rows.append(
            {
                "template_id": template_id,
                "base_color_rule": dict(entry.get("base_color_rule") or {}),
                "roughness_rule": dict(entry.get("roughness_rule") or {}),
                "metallic_rule": dict(entry.get("metallic_rule") or {}),
                "emission_rule": dict(entry.get("emission_rule") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        material_template_id_set.add(template_id)
    material_template_rows = sorted(material_template_rows, key=lambda row: str(row.get("template_id", "")))

    _label_record, label_rows_raw, label_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/label_policy_registry.json",
        expected_schema_id="dominium.registry.label_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="label_policies",
    )
    if label_load_errors:
        return [], [], [], [], [], [], [], [], label_load_errors

    label_policy_rows: List[dict] = []
    label_policy_id_set = set()
    for entry in sorted(label_rows_raw, key=lambda row: str((row or {}).get("label_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_label_policy_entry",
                    "message": "label policy entry must be object",
                    "path": "$.label_policies",
                }
            )
            continue
        label_policy_id = str(entry.get("label_policy_id", "")).strip()
        label_source = str(entry.get("label_source", "")).strip()
        if (
            not label_policy_id
            or label_source not in ("none", "semantic_id", "entity_id", "faction_tag", "custom")
            or not isinstance(entry.get("show_label"), bool)
            or not isinstance(entry.get("extensions"), dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_label_policy_entry",
                    "message": "label policy entry missing required fields",
                    "path": "$.label_policies",
                }
            )
            continue
        if label_policy_id in label_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_label_policy_id",
                    "message": "duplicate label policy id '{}'".format(label_policy_id),
                    "path": "$.label_policies.label_policy_id",
                }
            )
            continue
        label_policy_rows.append(
            {
                "label_policy_id": label_policy_id,
                "show_label": bool(entry.get("show_label", False)),
                "label_source": label_source,
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        label_policy_id_set.add(label_policy_id)
    label_policy_rows = sorted(label_policy_rows, key=lambda row: str(row.get("label_policy_id", "")))

    _lod_record, lod_rows_raw, lod_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/lod_policy_registry.json",
        expected_schema_id="dominium.registry.lod_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="lod_policies",
    )
    if lod_load_errors:
        return [], [], [], [], [], [], [], [], lod_load_errors

    lod_policy_rows: List[dict] = []
    lod_policy_id_set = set()
    for entry in sorted(lod_rows_raw, key=lambda row: str((row or {}).get("lod_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_lod_policy_entry",
                    "message": "lod policy entry must be object",
                    "path": "$.lod_policies",
                }
            )
            continue
        lod_policy_id = str(entry.get("lod_policy_id", "")).strip()
        bands = entry.get("distance_bands_mm")
        if (
            not lod_policy_id
            or not isinstance(bands, list)
            or not isinstance(entry.get("default_hint"), str)
            or not isinstance(entry.get("extensions"), dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_lod_policy_entry",
                    "message": "lod policy entry missing required fields",
                    "path": "$.lod_policies",
                }
            )
            continue
        if lod_policy_id in lod_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_lod_policy_id",
                    "message": "duplicate lod policy id '{}'".format(lod_policy_id),
                    "path": "$.lod_policies.lod_policy_id",
                }
            )
            continue
        normalized_bands = []
        valid_bands = True
        for value in bands:
            try:
                numeric = int(value)
            except (TypeError, ValueError):
                valid_bands = False
                break
            if numeric < 0:
                valid_bands = False
                break
            normalized_bands.append(numeric)
        if not valid_bands:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_lod_policy_entry",
                    "message": "lod policy '{}' has invalid distance_bands_mm".format(lod_policy_id),
                    "path": "$.lod_policies.distance_bands_mm",
                }
            )
            continue
        lod_policy_rows.append(
            {
                "lod_policy_id": lod_policy_id,
                "distance_bands_mm": sorted(set(normalized_bands)),
                "default_hint": str(entry.get("default_hint", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        lod_policy_id_set.add(lod_policy_id)
    lod_policy_rows = sorted(lod_policy_rows, key=lambda row: str(row.get("lod_policy_id", "")))

    _representation_rule_record, rule_rows_raw, rule_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/representation_rule_registry.json",
        expected_schema_id="dominium.registry.representation_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="representation_rules",
    )
    if rule_load_errors:
        return [], [], [], [], [], [], [], [], rule_load_errors

    representation_rule_rows: List[dict] = []
    representation_rule_id_set = set()
    for entry in sorted(rule_rows_raw, key=lambda row: str((row or {}).get("rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_representation_rule_entry",
                    "message": "representation rule entry must be object",
                    "path": "$.representation_rules",
                }
            )
            continue
        rule_id = str(entry.get("rule_id", "")).strip()
        if not rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_representation_rule_entry",
                    "message": "representation rule entry missing rule_id",
                    "path": "$.representation_rules.rule_id",
                }
            )
            continue
        if rule_id in representation_rule_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_representation_rule_id",
                    "message": "duplicate representation rule id '{}'".format(rule_id),
                    "path": "$.representation_rules.rule_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="representation_rule",
            payload=schema_payload,
            path="data/registries/representation_rule_registry.json#{}".format(rule_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        match_row = dict(entry.get("match") or {})
        output_row = dict(entry.get("output") or {})
        primitive_id = str(output_row.get("primitive_id", "")).strip()
        template_id = str(output_row.get("procedural_material_template_id", "")).strip()
        label_policy_id = str(output_row.get("label_policy_id", "")).strip()
        lod_policy_id = str(output_row.get("lod_policy_id", "")).strip()
        if primitive_id not in render_primitive_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.representation_rule_primitive_missing",
                    "message": "representation rule '{}' references unknown primitive '{}'".format(
                        rule_id,
                        primitive_id,
                    ),
                    "path": "$.representation_rules.output.primitive_id",
                }
            )
            continue
        if template_id not in material_template_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.representation_rule_template_missing",
                    "message": "representation rule '{}' references unknown template '{}'".format(
                        rule_id,
                        template_id,
                    ),
                    "path": "$.representation_rules.output.procedural_material_template_id",
                }
            )
            continue
        if label_policy_id not in label_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.representation_rule_label_policy_missing",
                    "message": "representation rule '{}' references unknown label policy '{}'".format(
                        rule_id,
                        label_policy_id,
                    ),
                    "path": "$.representation_rules.output.label_policy_id",
                }
            )
            continue
        if lod_policy_id not in lod_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.representation_rule_lod_policy_missing",
                    "message": "representation rule '{}' references unknown lod policy '{}'".format(
                        rule_id,
                        lod_policy_id,
                    ),
                    "path": "$.representation_rules.output.lod_policy_id",
                }
            )
            continue
        representation_rule_rows.append(
            {
                "rule_id": rule_id,
                "match": {
                    "entity_kind": match_row.get("entity_kind"),
                    "material_tag": match_row.get("material_tag"),
                    "domain_id": match_row.get("domain_id"),
                    "faction_id": match_row.get("faction_id"),
                    "view_mode_id": match_row.get("view_mode_id"),
                    "body_shape": match_row.get("body_shape"),
                },
                "output": {
                    "primitive_id": primitive_id,
                    "procedural_material_template_id": template_id,
                    "label_policy_id": label_policy_id,
                    "lod_policy_id": lod_policy_id,
                },
                "priority": int(entry.get("priority", 0) or 0),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        representation_rule_id_set.add(rule_id)
    representation_rule_rows = sorted(
        representation_rule_rows,
        key=lambda row: (int(row.get("priority", 0) or 0) * -1, str(row.get("rule_id", ""))),
    )

    return (
        render_proxy_rows,
        cosmetic_rows,
        cosmetic_policy_rows,
        render_primitive_rows,
        material_template_rows,
        label_policy_rows,
        lod_policy_rows,
        representation_rule_rows,
        errors,
    )


def _network_policy_rows(
    repo_root: str,
    known_law_profile_ids: List[str],
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []
    law_profile_id_set = set(str(item).strip() for item in (known_law_profile_ids or []) if str(item).strip())

    _modules_record, module_rows_raw, module_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/anti_cheat_module_registry.json",
        expected_schema_id="dominium.registry.anti_cheat_module_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="modules",
    )
    if module_load_errors:
        return [], [], [], [], [], [], [], module_load_errors

    anti_cheat_module_rows: List[dict] = []
    module_id_set = set()
    for entry in sorted(module_rows_raw, key=lambda row: str((row or {}).get("module_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_anti_cheat_module_entry",
                    "message": "anti-cheat module entry must be object",
                    "path": "$.modules",
                }
            )
            continue
        module_id = str(entry.get("module_id", "")).strip()
        if not module_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_anti_cheat_module_entry",
                    "message": "anti-cheat module entry missing module_id",
                    "path": "$.modules.module_id",
                }
            )
            continue
        if module_id in module_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_anti_cheat_module_id",
                    "message": "duplicate anti-cheat module_id '{}'".format(module_id),
                    "path": "$.modules.module_id",
                }
            )
            continue
        inputs = entry.get("inputs")
        outputs = entry.get("outputs")
        extensions = entry.get("extensions")
        if not isinstance(inputs, list) or not isinstance(outputs, list) or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_anti_cheat_module_entry",
                    "message": "anti-cheat module '{}' missing required list/object fields".format(module_id),
                    "path": "$.modules",
                }
            )
            continue
        module_id_set.add(module_id)
        anti_cheat_module_rows.append(
            {
                "module_id": module_id,
                "description": str(entry.get("description", "")).strip(),
                "inputs": _sorted_unique_strings(inputs),
                "outputs": _sorted_unique_strings(outputs),
                "determinism_notes": str(entry.get("determinism_notes", "")).strip(),
                "extensions": dict(extensions),
            }
        )
    anti_cheat_module_rows = sorted(anti_cheat_module_rows, key=lambda row: str(row.get("module_id", "")))

    _policies_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/anti_cheat_policy_registry.json",
        expected_schema_id="dominium.registry.anti_cheat_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], [], [], [], [], [], policy_load_errors

    anti_cheat_policy_rows: List[dict] = []
    anti_cheat_policy_id_set = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_anti_cheat_policy_entry",
                    "message": "anti-cheat policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        modules_enabled = entry.get("modules_enabled")
        default_actions = entry.get("default_actions")
        extensions = entry.get("extensions")
        if (
            not policy_id
            or not isinstance(modules_enabled, list)
            or not isinstance(default_actions, dict)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_anti_cheat_policy_entry",
                    "message": "anti-cheat policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        module_ids = _sorted_unique_strings(modules_enabled)
        unknown_modules = [module_id for module_id in module_ids if module_id not in module_id_set]
        if unknown_modules:
            errors.append(
                {
                    "code": "refuse.registry_compile.anti_cheat_policy_module_missing",
                    "message": "anti-cheat policy '{}' references unknown module ids: {}".format(
                        policy_id,
                        ",".join(sorted(unknown_modules)),
                    ),
                    "path": "$.policies.modules_enabled",
                }
            )
            continue
        action_rows: Dict[str, str] = {}
        valid_actions = {"audit", "refuse", "terminate", "throttle", "require_attestation"}
        action_error = False
        for module_id in sorted(default_actions.keys()):
            action = str(default_actions.get(module_id, "")).strip()
            module_id_token = str(module_id).strip()
            if module_id_token not in module_id_set:
                errors.append(
                    {
                        "code": "refuse.registry_compile.anti_cheat_policy_module_missing",
                        "message": "anti-cheat policy '{}' default_actions references unknown module '{}'".format(
                            policy_id,
                            module_id_token,
                        ),
                        "path": "$.policies.default_actions",
                    }
                )
                action_error = True
                continue
            if module_id_token not in module_ids:
                errors.append(
                    {
                        "code": "refuse.registry_compile.anti_cheat_policy_action_unmapped",
                        "message": "anti-cheat policy '{}' default_actions contains module '{}' not listed in modules_enabled".format(
                            policy_id,
                            module_id_token,
                        ),
                        "path": "$.policies.default_actions",
                    }
                )
                action_error = True
                continue
            if action not in valid_actions:
                errors.append(
                    {
                        "code": "refuse.registry_compile.anti_cheat_policy_action_invalid",
                        "message": "anti-cheat policy '{}' default action '{}' is invalid".format(
                            policy_id,
                            action,
                        ),
                        "path": "$.policies.default_actions",
                    }
                )
                action_error = True
                continue
            action_rows[module_id_token] = action
        if action_error:
            continue

        anti_cheat_policy_rows.append(
            {
                "policy_id": policy_id,
                "human_name": str(entry.get("human_name", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "modules_enabled": module_ids,
                "default_actions": dict((key, action_rows[key]) for key in sorted(action_rows.keys())),
                "allowed_in_singleplayer": bool(entry.get("allowed_in_singleplayer", False)),
                "allowed_in_private_server": bool(entry.get("allowed_in_private_server", False)),
                "required_for_ranked": bool(entry.get("required_for_ranked", False)),
                "extensions": dict(extensions),
            }
        )
        anti_cheat_policy_id_set.add(policy_id)
    anti_cheat_policy_rows = sorted(anti_cheat_policy_rows, key=lambda row: str(row.get("policy_id", "")))

    _strategies_record, strategy_rows_raw, strategy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/net_resync_strategy_registry.json",
        expected_schema_id="dominium.registry.net_resync_strategy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="strategies",
    )
    if strategy_load_errors:
        return [], [], [], [], [], [], [], strategy_load_errors

    net_resync_strategy_rows: List[dict] = []
    resync_strategy_id_set = set()
    for entry in sorted(strategy_rows_raw, key=lambda row: str((row or {}).get("strategy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_resync_strategy_entry",
                    "message": "net resync strategy entry must be object",
                    "path": "$.strategies",
                }
            )
            continue
        strategy_id = str(entry.get("strategy_id", "")).strip()
        supported_policies = entry.get("supported_policies")
        steps = entry.get("steps")
        refusal_codes = entry.get("refusal_codes")
        extensions = entry.get("extensions")
        if (
            not strategy_id
            or not isinstance(supported_policies, list)
            or not isinstance(steps, list)
            or not isinstance(refusal_codes, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_resync_strategy_entry",
                    "message": "net resync strategy entry missing required fields",
                    "path": "$.strategies",
                }
            )
            continue
        if strategy_id in resync_strategy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_net_resync_strategy_id",
                    "message": "duplicate net resync strategy_id '{}'".format(strategy_id),
                    "path": "$.strategies.strategy_id",
                }
            )
            continue
        resync_strategy_id_set.add(strategy_id)
        net_resync_strategy_rows.append(
            {
                "strategy_id": strategy_id,
                "description": str(entry.get("description", "")).strip(),
                "supported_policies": _sorted_unique_strings(supported_policies),
                "steps": _sorted_unique_strings(steps),
                "refusal_codes": _sorted_unique_strings(refusal_codes),
                "extensions": dict(extensions),
            }
        )
    net_resync_strategy_rows = sorted(net_resync_strategy_rows, key=lambda row: str(row.get("strategy_id", "")))

    _replication_record, replication_rows_raw, replication_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/net_replication_policy_registry.json",
        expected_schema_id="dominium.registry.net_replication_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if replication_load_errors:
        return [], [], [], [], [], [], [], replication_load_errors

    net_replication_policy_rows: List[dict] = []
    replication_policy_id_set = set()
    for entry in sorted(replication_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_replication_policy_entry",
                    "message": "net replication policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        required_features = entry.get("required_features")
        resync_strategy_id = str(entry.get("resync_strategy_id", "")).strip()
        extensions = entry.get("extensions")
        if (
            not policy_id
            or not isinstance(required_features, list)
            or not resync_strategy_id
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_replication_policy_entry",
                    "message": "net replication policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        if policy_id in replication_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_net_replication_policy_id",
                    "message": "duplicate net replication policy_id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue
        if resync_strategy_id not in resync_strategy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_replication_resync_missing",
                    "message": "net replication policy '{}' references missing resync strategy '{}'".format(
                        policy_id,
                        resync_strategy_id,
                    ),
                    "path": "$.policies.resync_strategy_id",
                }
            )
            continue
        replication_policy_id_set.add(policy_id)
        net_replication_policy_rows.append(
            {
                "policy_id": policy_id,
                "human_name": str(entry.get("human_name", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "required_features": _sorted_unique_strings(required_features),
                "allowed_in_singleplayer": bool(entry.get("allowed_in_singleplayer", False)),
                "allowed_in_private_server": bool(entry.get("allowed_in_private_server", False)),
                "allowed_in_ranked": bool(entry.get("allowed_in_ranked", False)),
                "deterministic_ordering_rule_id": str(entry.get("deterministic_ordering_rule_id", "")).strip(),
                "resync_strategy_id": resync_strategy_id,
                "extensions": dict(extensions),
            }
        )
    net_replication_policy_rows = sorted(net_replication_policy_rows, key=lambda row: str(row.get("policy_id", "")))

    for entry in net_resync_strategy_rows:
        for policy_id in entry.get("supported_policies") or []:
            if str(policy_id) not in replication_policy_id_set:
                errors.append(
                    {
                        "code": "refuse.registry_compile.net_resync_supported_policy_missing",
                        "message": "resync strategy '{}' references unknown net policy '{}'".format(
                            str(entry.get("strategy_id", "")),
                            str(policy_id),
                        ),
                        "path": "$.strategies.supported_policies",
                    }
                )

    _server_policies_record, server_policy_rows_raw, server_policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/net_server_policy_registry.json",
        expected_schema_id="dominium.registry.net_server_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if server_policy_load_errors:
        return [], [], [], [], [], [], [], server_policy_load_errors

    net_server_policy_rows: List[dict] = []
    server_policy_id_set = set()
    for entry in sorted(server_policy_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_server_policy_entry",
                    "message": "net server policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        allowed_replication_ids = entry.get("allowed_replication_policy_ids")
        allowed_anti_cheat_ids = entry.get("allowed_anti_cheat_policy_ids")
        allowed_law_profile_ids = entry.get("allowed_law_profile_ids")
        required_anti_cheat_policy_id = str(entry.get("required_anti_cheat_policy_id", "")).strip()
        securex_policy_id = str(entry.get("securex_policy_id", "")).strip()
        extensions = entry.get("extensions")
        if (
            not policy_id
            or not isinstance(allowed_replication_ids, list)
            or not isinstance(allowed_anti_cheat_ids, list)
            or not isinstance(allowed_law_profile_ids, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_net_server_policy_entry",
                    "message": "net server policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        if policy_id in server_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_net_server_policy_id",
                    "message": "duplicate net server policy_id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue

        allowed_replication_rows = _sorted_unique_strings(allowed_replication_ids)
        allowed_anti_cheat_rows = _sorted_unique_strings(allowed_anti_cheat_ids)
        allowed_law_rows = _sorted_unique_strings(allowed_law_profile_ids)

        unknown_replication = [token for token in allowed_replication_rows if token not in replication_policy_id_set]
        if unknown_replication:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_replication_missing",
                    "message": "net server policy '{}' references unknown replication policies: {}".format(
                        policy_id,
                        ",".join(unknown_replication),
                    ),
                    "path": "$.policies.allowed_replication_policy_ids",
                }
            )
            continue

        unknown_anti_cheat = [token for token in allowed_anti_cheat_rows if token and token not in anti_cheat_policy_id_set]
        if unknown_anti_cheat:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_anti_cheat_missing",
                    "message": "net server policy '{}' references unknown anti-cheat policies: {}".format(
                        policy_id,
                        ",".join(unknown_anti_cheat),
                    ),
                    "path": "$.policies.allowed_anti_cheat_policy_ids",
                }
            )
            continue
        if required_anti_cheat_policy_id and required_anti_cheat_policy_id not in allowed_anti_cheat_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_required_anti_cheat_unmapped",
                    "message": "net server policy '{}' required anti-cheat policy must be included in allowed_anti_cheat_policy_ids".format(
                        policy_id
                    ),
                    "path": "$.policies.required_anti_cheat_policy_id",
                }
            )
            continue
        unknown_law = [token for token in allowed_law_rows if token not in law_profile_id_set]
        if unknown_law:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_law_profile_missing",
                    "message": "net server policy '{}' references unknown law profiles: {}".format(
                        policy_id,
                        ",".join(unknown_law),
                    ),
                    "path": "$.policies.allowed_law_profile_ids",
                }
            )
            continue
        if not allowed_law_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_law_profile_missing",
                    "message": "net server policy '{}' must declare at least one allowed_law_profile_id".format(policy_id),
                    "path": "$.policies.allowed_law_profile_ids",
                }
            )
            continue

        server_policy_id_set.add(policy_id)
        net_server_policy_rows.append(
            {
                "policy_id": policy_id,
                "human_name": str(entry.get("human_name", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "allowed_replication_policy_ids": allowed_replication_rows,
                "allowed_anti_cheat_policy_ids": allowed_anti_cheat_rows,
                "required_anti_cheat_policy_id": required_anti_cheat_policy_id,
                "securex_require_signed": bool(entry.get("securex_require_signed", False)),
                "securex_policy_id": securex_policy_id,
                "allowed_law_profile_ids": allowed_law_rows,
                "extensions": dict(extensions),
            }
        )
    net_server_policy_rows = sorted(net_server_policy_rows, key=lambda row: str(row.get("policy_id", "")))

    _securex_record, securex_rows_raw, securex_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/securex_policy_registry.json",
        expected_schema_id="dominium.registry.securex_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if securex_load_errors:
        return [], [], [], [], [], [], [], securex_load_errors

    securex_policy_rows: List[dict] = []
    securex_policy_id_set = set()
    allowed_signature_status = {
        "official",
        "signed",
        "verified",
        "unsigned",
        "classroom-restricted",
        "revoked",
    }
    for entry in sorted(securex_rows_raw, key=lambda row: str((row or {}).get("securex_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_securex_policy_entry",
                    "message": "securex policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        securex_policy_id = str(entry.get("securex_policy_id", "")).strip()
        required_signature_status = entry.get("required_signature_status")
        allowed_pack_publishers = entry.get("allowed_pack_publishers")
        refusal_codes = entry.get("refusal_codes")
        extensions = entry.get("extensions")
        if (
            not securex_policy_id
            or not isinstance(required_signature_status, list)
            or not isinstance(allowed_pack_publishers, list)
            or not isinstance(refusal_codes, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_securex_policy_entry",
                    "message": "securex policy entry missing required fields",
                    "path": "$.policies",
                }
            )
            continue
        if securex_policy_id in securex_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_securex_policy_id",
                    "message": "duplicate securex policy id '{}'".format(securex_policy_id),
                    "path": "$.policies.securex_policy_id",
                }
            )
            continue
        signature_status_rows = _sorted_unique_strings(required_signature_status)
        if not signature_status_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_securex_policy_entry",
                    "message": "securex policy '{}' must declare at least one required_signature_status value".format(
                        securex_policy_id
                    ),
                    "path": "$.policies.required_signature_status",
                }
            )
            continue
        unknown_status_rows = [
            token for token in signature_status_rows if token not in allowed_signature_status
        ]
        if unknown_status_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.securex_policy_signature_status_invalid",
                    "message": "securex policy '{}' includes unknown signature status values: {}".format(
                        securex_policy_id,
                        ",".join(sorted(unknown_status_rows)),
                    ),
                    "path": "$.policies.required_signature_status",
                }
            )
            continue

        allow_unsigned = bool(entry.get("allow_unsigned", False))
        allow_classroom_restricted = bool(entry.get("allow_classroom_restricted", False))
        if (not allow_unsigned) and "unsigned" in signature_status_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.securex_policy_unsigned_conflict",
                    "message": "securex policy '{}' disallows unsigned packs but required_signature_status includes 'unsigned'".format(
                        securex_policy_id
                    ),
                    "path": "$.policies.required_signature_status",
                }
            )
            continue
        if (not allow_classroom_restricted) and "classroom-restricted" in signature_status_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.securex_policy_classroom_conflict",
                    "message": "securex policy '{}' disallows classroom-restricted packs but required_signature_status includes that value".format(
                        securex_policy_id
                    ),
                    "path": "$.policies.required_signature_status",
                }
            )
            continue

        securex_policy_rows.append(
            {
                "securex_policy_id": securex_policy_id,
                "description": str(entry.get("description", "")).strip(),
                "required_signature_status": signature_status_rows,
                "allow_unsigned": allow_unsigned,
                "allow_classroom_restricted": allow_classroom_restricted,
                "allowed_pack_publishers": _sorted_unique_strings(allowed_pack_publishers),
                "signature_verification_required": bool(entry.get("signature_verification_required", False)),
                "refusal_codes": _sorted_unique_strings(refusal_codes),
                "extensions": dict(extensions),
            }
        )
        securex_policy_id_set.add(securex_policy_id)
    securex_policy_rows = sorted(securex_policy_rows, key=lambda row: str(row.get("securex_policy_id", "")))

    for entry in net_server_policy_rows:
        securex_policy_id = str(entry.get("securex_policy_id", "")).strip()
        if securex_policy_id and securex_policy_id not in securex_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.net_server_policy_securex_missing",
                    "message": "net server policy '{}' references unknown securex policy '{}'".format(
                        str(entry.get("policy_id", "")),
                        securex_policy_id,
                    ),
                    "path": "$.policies.securex_policy_id",
                }
            )

    _server_profile_record, server_profile_rows_raw, server_profile_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/server_profile_registry.json",
        expected_schema_id="dominium.registry.server_profile_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="profiles",
    )
    if server_profile_load_errors:
        return [], [], [], [], [], [], [], server_profile_load_errors

    server_profile_rows: List[dict] = []
    server_profile_id_set = set()
    for entry in sorted(server_profile_rows_raw, key=lambda row: str((row or {}).get("server_profile_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_server_profile_entry",
                    "message": "server profile entry must be object",
                    "path": "$.profiles",
                }
            )
            continue
        server_profile_id = str(entry.get("server_profile_id", "")).strip()
        allowed_replication_policy_ids = entry.get("allowed_replication_policy_ids")
        required_replication_policy_ids = entry.get("required_replication_policy_ids")
        allowed_law_profile_ids = entry.get("allowed_law_profile_ids")
        allowed_entitlements = entry.get("allowed_entitlements")
        disallowed_entitlements = entry.get("disallowed_entitlements")
        extensions = entry.get("extensions")
        if (
            not server_profile_id
            or not isinstance(allowed_replication_policy_ids, list)
            or not isinstance(required_replication_policy_ids, list)
            or not isinstance(allowed_law_profile_ids, list)
            or not isinstance(allowed_entitlements, list)
            or not isinstance(disallowed_entitlements, list)
            or not isinstance(extensions, dict)
        ):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_server_profile_entry",
                    "message": "server profile entry missing required fields",
                    "path": "$.profiles",
                }
            )
            continue
        if server_profile_id in server_profile_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_server_profile_id",
                    "message": "duplicate server profile id '{}'".format(server_profile_id),
                    "path": "$.profiles.server_profile_id",
                }
            )
            continue

        allowed_replication_rows = _sorted_unique_strings(allowed_replication_policy_ids)
        required_replication_rows = _sorted_unique_strings(required_replication_policy_ids)
        allowed_law_rows = _sorted_unique_strings(allowed_law_profile_ids)
        allowed_entitlement_rows = _sorted_unique_strings(allowed_entitlements)
        disallowed_entitlement_rows = _sorted_unique_strings(disallowed_entitlements)
        anti_cheat_policy_id = str(entry.get("anti_cheat_policy_id", "")).strip()
        securex_policy_id = str(entry.get("securex_policy_id", "")).strip()
        epistemic_policy_id_default = str(entry.get("epistemic_policy_id_default", "")).strip()
        required_law_profile_raw = entry.get("required_law_profile_id")
        required_law_profile_id = (
            str(required_law_profile_raw).strip()
            if required_law_profile_raw not in (None, "")
            else ""
        )
        snapshot_policy_raw = entry.get("snapshot_policy_id")
        snapshot_policy_id = str(snapshot_policy_raw).strip() if snapshot_policy_raw not in (None, "") else ""
        resync_policy_raw = entry.get("resync_policy_id")
        resync_policy_id = str(resync_policy_raw).strip() if resync_policy_raw not in (None, "") else ""

        if not allowed_replication_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_replication_missing",
                    "message": "server profile '{}' must declare at least one allowed replication policy".format(
                        server_profile_id
                    ),
                    "path": "$.profiles.allowed_replication_policy_ids",
                }
            )
            continue
        unknown_replication = [token for token in allowed_replication_rows if token not in replication_policy_id_set]
        if unknown_replication:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_replication_unknown",
                    "message": "server profile '{}' references unknown replication policies: {}".format(
                        server_profile_id,
                        ",".join(sorted(unknown_replication)),
                    ),
                    "path": "$.profiles.allowed_replication_policy_ids",
                }
            )
            continue
        required_not_allowed = [token for token in required_replication_rows if token not in allowed_replication_rows]
        if required_not_allowed:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_required_replication_unmapped",
                    "message": "server profile '{}' required replication policies are not part of allowed list: {}".format(
                        server_profile_id,
                        ",".join(sorted(required_not_allowed)),
                    ),
                    "path": "$.profiles.required_replication_policy_ids",
                }
            )
            continue
        if anti_cheat_policy_id not in anti_cheat_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_anti_cheat_missing",
                    "message": "server profile '{}' references unknown anti-cheat policy '{}'".format(
                        server_profile_id,
                        anti_cheat_policy_id or "<empty>",
                    ),
                    "path": "$.profiles.anti_cheat_policy_id",
                }
            )
            continue
        if securex_policy_id not in securex_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_securex_missing",
                    "message": "server profile '{}' references unknown securex policy '{}'".format(
                        server_profile_id,
                        securex_policy_id or "<empty>",
                    ),
                    "path": "$.profiles.securex_policy_id",
                }
            )
            continue
        if not epistemic_policy_id_default:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_epistemic_policy_missing",
                    "message": "server profile '{}' must declare epistemic_policy_id_default".format(server_profile_id),
                    "path": "$.profiles.epistemic_policy_id_default",
                }
            )
            continue
        if not allowed_law_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_law_profile_missing",
                    "message": "server profile '{}' must declare at least one allowed_law_profile_id".format(
                        server_profile_id
                    ),
                    "path": "$.profiles.allowed_law_profile_ids",
                }
            )
            continue
        unknown_law = [token for token in allowed_law_rows if token not in law_profile_id_set]
        if unknown_law:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_law_profile_unknown",
                    "message": "server profile '{}' references unknown law profiles: {}".format(
                        server_profile_id,
                        ",".join(sorted(unknown_law)),
                    ),
                    "path": "$.profiles.allowed_law_profile_ids",
                }
            )
            continue
        if required_law_profile_id and required_law_profile_id not in allowed_law_rows:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_required_law_unmapped",
                    "message": "server profile '{}' required law profile must be included in allowed_law_profile_ids".format(
                        server_profile_id
                    ),
                    "path": "$.profiles.required_law_profile_id",
                }
            )
            continue
        if resync_policy_id and resync_policy_id not in resync_strategy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_resync_policy_missing",
                    "message": "server profile '{}' references unknown resync policy '{}'".format(
                        server_profile_id,
                        resync_policy_id,
                    ),
                    "path": "$.profiles.resync_policy_id",
                }
            )
            continue
        legacy_server_policy_id = str(extensions.get("legacy_server_policy_id", "")).strip()
        if legacy_server_policy_id and legacy_server_policy_id not in server_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.server_profile_legacy_policy_unknown",
                    "message": "server profile '{}' references unknown legacy server policy '{}'".format(
                        server_profile_id,
                        legacy_server_policy_id,
                    ),
                    "path": "$.profiles.extensions.legacy_server_policy_id",
                }
            )
            continue

        server_profile_rows.append(
            {
                "server_profile_id": server_profile_id,
                "description": str(entry.get("description", "")).strip(),
                "allowed_replication_policy_ids": allowed_replication_rows,
                "required_replication_policy_ids": required_replication_rows,
                "anti_cheat_policy_id": anti_cheat_policy_id,
                "securex_policy_id": securex_policy_id,
                "epistemic_policy_id_default": epistemic_policy_id_default,
                "allowed_law_profile_ids": allowed_law_rows,
                "required_law_profile_id": required_law_profile_id if required_law_profile_id else None,
                "allowed_entitlements": allowed_entitlement_rows,
                "disallowed_entitlements": disallowed_entitlement_rows,
                "snapshot_policy_id": snapshot_policy_id if snapshot_policy_id else None,
                "resync_policy_id": resync_policy_id if resync_policy_id else None,
                "extensions": dict(extensions),
            }
        )
        server_profile_id_set.add(server_profile_id)
    server_profile_rows = sorted(server_profile_rows, key=lambda row: str(row.get("server_profile_id", "")))

    return (
        net_replication_policy_rows,
        net_resync_strategy_rows,
        net_server_policy_rows,
        anti_cheat_policy_rows,
        anti_cheat_module_rows,
        securex_policy_rows,
        server_profile_rows,
        errors,
    )


def _hybrid_policy_rows(
    repo_root: str,
    schema_root: str,
    known_replication_policy_ids: List[str],
    net_server_policy_rows: List[dict],
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []
    replication_policy_id_set = set(str(item).strip() for item in (known_replication_policy_ids or []) if str(item).strip())

    if "policy.net.srz_hybrid" not in replication_policy_id_set:
        errors.append(
            {
                "code": "refuse.registry_compile.srz_hybrid_policy_missing",
                "message": "net replication registry must declare policy.net.srz_hybrid before compiling shard/perception registries",
                "path": "$.policies.policy_id",
            }
        )

    _shard_map_record, shard_map_rows_raw, shard_map_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/shard_map_registry.json",
        expected_schema_id="dominium.registry.shard_map_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="shard_maps",
    )
    if shard_map_load_errors:
        return [], [], shard_map_load_errors

    shard_map_rows: List[dict] = []
    shard_map_id_set = set()
    for entry in sorted(shard_map_rows_raw, key=lambda row: str((row or {}).get("shard_map_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_shard_map_entry",
                    "message": "shard map entry must be object",
                    "path": "$.shard_maps",
                }
            )
            continue
        shard_map_id = str(entry.get("shard_map_id", "")).strip()
        if not shard_map_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_shard_map_entry",
                    "message": "shard map entry missing shard_map_id",
                    "path": "$.shard_maps.shard_map_id",
                }
            )
            continue
        if shard_map_id in shard_map_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_shard_map_id",
                    "message": "duplicate shard_map_id '{}'".format(shard_map_id),
                    "path": "$.shard_maps.shard_map_id",
                }
            )
            continue
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="shard_map",
            payload=dict(entry),
            path="data/registries/shard_map_registry.json#{}".format(shard_map_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        shard_rows = list(entry.get("shards") or [])
        shard_ids = []
        for shard_row in shard_rows:
            if not isinstance(shard_row, dict):
                continue
            token = str(shard_row.get("shard_id", "")).strip()
            if token:
                shard_ids.append(token)
        if len(set(shard_ids)) != len(shard_ids):
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_shard_id",
                    "message": "shard_map '{}' contains duplicate shard_id values".format(shard_map_id),
                    "path": "$.shard_maps.shards",
                }
            )
            continue

        shard_map_rows.append(
            {
                "shard_map_id": shard_map_id,
                "shards": sorted(
                    (dict(item) for item in shard_rows if isinstance(item, dict)),
                    key=lambda row: (str(row.get("priority", "")), str(row.get("shard_id", ""))),
                ),
                "routing_rule_id": str(entry.get("routing_rule_id", "")).strip(),
                "version_introduced": str(entry.get("version_introduced", "")).strip(),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        shard_map_id_set.add(shard_map_id)
    shard_map_rows = sorted(shard_map_rows, key=lambda row: str(row.get("shard_map_id", "")))

    _perception_record, perception_rows_raw, perception_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/perception_interest_policy_registry.json",
        expected_schema_id="dominium.registry.perception_interest_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if perception_load_errors:
        return [], [], perception_load_errors

    perception_rows: List[dict] = []
    perception_policy_id_set = set()
    for entry in sorted(perception_rows_raw, key=lambda row: str((row or {}).get("policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_perception_interest_policy_entry",
                    "message": "perception interest policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        policy_id = str(entry.get("policy_id", "")).strip()
        if not policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_perception_interest_policy_entry",
                    "message": "perception interest policy entry missing policy_id",
                    "path": "$.policies.policy_id",
                }
            )
            continue
        if policy_id in perception_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_perception_interest_policy_id",
                    "message": "duplicate perception interest policy_id '{}'".format(policy_id),
                    "path": "$.policies.policy_id",
                }
            )
            continue
        distance_bands = entry.get("distance_bands")
        lens_visibility_rules = entry.get("lens_visibility_rules")
        extensions = entry.get("extensions")
        if not isinstance(distance_bands, list) or not isinstance(lens_visibility_rules, list) or not isinstance(extensions, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_perception_interest_policy_entry",
                    "message": "perception interest policy '{}' missing required list/object fields".format(policy_id),
                    "path": "$.policies",
                }
            )
            continue
        perception_rows.append(
            {
                "policy_id": policy_id,
                "human_name": str(entry.get("human_name", "")).strip(),
                "description": str(entry.get("description", "")).strip(),
                "max_objects_per_tick": int(entry.get("max_objects_per_tick", 0) or 0),
                "distance_bands": sorted(
                    (dict(item) for item in distance_bands if isinstance(item, dict)),
                    key=lambda row: (float(row.get("max_distance", 0.0) or 0.0), str(row.get("band_id", ""))),
                ),
                "lens_visibility_rules": sorted(
                    (dict(item) for item in lens_visibility_rules if isinstance(item, dict)),
                    key=lambda row: (str(row.get("lens_type", "")), float(row.get("max_objects_multiplier", 0.0) or 0.0)),
                ),
                "deterministic_ordering_rule_id": str(entry.get("deterministic_ordering_rule_id", "")).strip(),
                "bandwidth_budget_units": int(entry.get("bandwidth_budget_units", 0) or 0),
                "resync_window_ticks": int(entry.get("resync_window_ticks", 0) or 0),
                "extensions": dict(extensions),
            }
        )
        perception_policy_id_set.add(policy_id)
    perception_rows = sorted(perception_rows, key=lambda row: str(row.get("policy_id", "")))

    for server_policy in sorted(
        (dict(row) for row in (net_server_policy_rows or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("policy_id", "")),
    ):
        policy_id = str(server_policy.get("policy_id", "")).strip() or "<unknown>"
        allowed_replication = _sorted_unique_strings(server_policy.get("allowed_replication_policy_ids") or [])
        extensions = dict(server_policy.get("extensions") or {})
        shard_map_id = str(extensions.get("default_shard_map_id", "")).strip()
        perception_policy_id = str(extensions.get("perception_interest_policy_id", "")).strip()
        if "policy.net.srz_hybrid" in allowed_replication:
            if not shard_map_id:
                errors.append(
                    {
                        "code": "refuse.registry_compile.net_server_policy_shard_map_missing",
                        "message": "server policy '{}' allows policy.net.srz_hybrid but extensions.default_shard_map_id is missing".format(
                            policy_id
                        ),
                        "path": "$.policies.extensions.default_shard_map_id",
                    }
                )
            elif shard_map_id not in shard_map_id_set:
                errors.append(
                    {
                        "code": "refuse.registry_compile.net_server_policy_shard_map_unknown",
                        "message": "server policy '{}' references unknown shard_map_id '{}'".format(
                            policy_id,
                            shard_map_id,
                        ),
                        "path": "$.policies.extensions.default_shard_map_id",
                    }
                )
            if not perception_policy_id:
                errors.append(
                    {
                        "code": "refuse.registry_compile.net_server_policy_perception_policy_missing",
                        "message": "server policy '{}' allows policy.net.srz_hybrid but extensions.perception_interest_policy_id is missing".format(
                            policy_id
                        ),
                        "path": "$.policies.extensions.perception_interest_policy_id",
                    }
                )
            elif perception_policy_id not in perception_policy_id_set:
                errors.append(
                    {
                        "code": "refuse.registry_compile.net_server_policy_perception_policy_unknown",
                        "message": "server policy '{}' references unknown perception interest policy '{}'".format(
                            policy_id,
                            perception_policy_id,
                        ),
                        "path": "$.policies.extensions.perception_interest_policy_id",
                    }
                )
    return shard_map_rows, perception_rows, errors


def _epistemic_policy_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []
    _eviction_record, eviction_rows_raw, eviction_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/eviction_rule_registry.json",
        expected_schema_id="dominium.registry.eviction_rule_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="eviction_rules",
    )
    if eviction_load_errors:
        return [], [], [], [], eviction_load_errors

    eviction_rows: List[dict] = []
    eviction_rule_id_set = set()
    for entry in sorted(eviction_rows_raw, key=lambda row: str((row or {}).get("eviction_rule_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_eviction_rule_entry",
                    "message": "eviction rule entry must be object",
                    "path": "$.eviction_rules",
                }
            )
            continue
        eviction_rule_id = str(entry.get("eviction_rule_id", "")).strip()
        if not eviction_rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_eviction_rule_entry",
                    "message": "eviction rule entry missing eviction_rule_id",
                    "path": "$.eviction_rules.eviction_rule_id",
                }
            )
            continue
        if eviction_rule_id in eviction_rule_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_eviction_rule_id",
                    "message": "duplicate eviction_rule_id '{}'".format(eviction_rule_id),
                    "path": "$.eviction_rules.eviction_rule_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="eviction_rule",
            payload=schema_payload,
            path="data/registries/eviction_rule_registry.json#{}".format(eviction_rule_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        eviction_rows.append(
            {
                "eviction_rule_id": eviction_rule_id,
                "description": str(entry.get("description", "")).strip(),
                "algorithm_id": str(entry.get("algorithm_id", "")).strip(),
                "priority_by_channel": dict(entry.get("priority_by_channel") or {}),
                "priority_by_subject_kind": dict(entry.get("priority_by_subject_kind") or {}),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        eviction_rule_id_set.add(eviction_rule_id)
    eviction_rows = sorted(eviction_rows, key=lambda row: str(row.get("eviction_rule_id", "")))

    _decay_record, decay_rows_raw, decay_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/decay_model_registry.json",
        expected_schema_id="dominium.registry.decay_model_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="decay_models",
    )
    if decay_load_errors:
        return [], [], [], [], decay_load_errors

    decay_rows: List[dict] = []
    decay_model_id_set = set()
    for entry in sorted(decay_rows_raw, key=lambda row: str((row or {}).get("decay_model_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_decay_model_entry",
                    "message": "decay model entry must be object",
                    "path": "$.decay_models",
                }
            )
            continue
        decay_model_id = str(entry.get("decay_model_id", "")).strip()
        if not decay_model_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_decay_model_entry",
                    "message": "decay model entry missing decay_model_id",
                    "path": "$.decay_models.decay_model_id",
                }
            )
            continue
        if decay_model_id in decay_model_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_decay_model_id",
                    "message": "duplicate decay_model_id '{}'".format(decay_model_id),
                    "path": "$.decay_models.decay_model_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="decay_model",
            payload=schema_payload,
            path="data/registries/decay_model_registry.json#{}".format(decay_model_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        eviction_rule_id = str(entry.get("eviction_rule_id", "")).strip()
        if eviction_rule_id not in eviction_rule_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.decay_eviction_rule_missing",
                    "message": "decay model '{}' references unknown eviction_rule_id '{}'".format(
                        decay_model_id,
                        eviction_rule_id or "<empty>",
                    ),
                    "path": "$.decay_models.eviction_rule_id",
                }
            )
            continue
        decay_rows.append(
            {
                "decay_model_id": decay_model_id,
                "description": str(entry.get("description", "")).strip(),
                "ttl_rules": sorted(
                    (dict(row) for row in (entry.get("ttl_rules") or []) if isinstance(row, dict)),
                    key=lambda row: (
                        str(row.get("channel_id", "")),
                        str(row.get("subject_kind", "")),
                        str(row.get("rule_id", "")),
                        str(row.get("ttl_ticks", "")),
                    ),
                ),
                "refresh_rules": sorted(
                    (dict(row) for row in (entry.get("refresh_rules") or []) if isinstance(row, dict)),
                    key=lambda row: (
                        str(row.get("channel_id", "")),
                        str(row.get("subject_kind", "")),
                        str(row.get("rule_id", "")),
                        str(row.get("refresh_on_observed", "")),
                    ),
                ),
                "eviction_rule_id": eviction_rule_id,
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        decay_model_id_set.add(decay_model_id)
    decay_rows = sorted(decay_rows, key=lambda row: str(row.get("decay_model_id", "")))

    _retention_record, retention_rows_raw, retention_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/retention_policy_registry.json",
        expected_schema_id="dominium.registry.retention_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if retention_load_errors:
        return [], [], [], [], retention_load_errors

    retention_rows: List[dict] = []
    retention_policy_id_set = set()
    for entry in sorted(retention_rows_raw, key=lambda row: str((row or {}).get("retention_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_retention_policy_entry",
                    "message": "retention policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        retention_policy_id = str(entry.get("retention_policy_id", "")).strip()
        if not retention_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_retention_policy_entry",
                    "message": "retention policy entry missing retention_policy_id",
                    "path": "$.policies.retention_policy_id",
                }
            )
            continue
        if retention_policy_id in retention_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_retention_policy_id",
                    "message": "duplicate retention_policy_id '{}'".format(retention_policy_id),
                    "path": "$.policies.retention_policy_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="retention_policy",
            payload=schema_payload,
            path="data/registries/retention_policy_registry.json#{}".format(retention_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue
        decay_model_id = str(entry.get("decay_model_id", "")).strip()
        if decay_model_id and decay_model_id not in decay_model_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.retention_decay_model_missing",
                    "message": "retention policy '{}' references unknown decay_model_id '{}'".format(
                        retention_policy_id,
                        decay_model_id,
                    ),
                    "path": "$.policies.decay_model_id",
                }
            )
            continue
        eviction_rule_id = (
            str(entry.get("eviction_rule_id", "")).strip()
            or str(entry.get("deterministic_eviction_rule_id", "")).strip()
        )
        if not eviction_rule_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.retention_eviction_rule_missing",
                    "message": "retention policy '{}' must declare eviction_rule_id".format(retention_policy_id),
                    "path": "$.policies.eviction_rule_id",
                }
            )
            continue
        if eviction_rule_id not in eviction_rule_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.retention_eviction_rule_missing",
                    "message": "retention policy '{}' references unknown eviction_rule_id '{}'".format(
                        retention_policy_id,
                        eviction_rule_id,
                    ),
                    "path": "$.policies.eviction_rule_id",
                }
            )
            continue
        retention_rows.append(
            {
                "retention_policy_id": retention_policy_id,
                "memory_allowed": bool(entry.get("memory_allowed", False)),
                "max_memory_items": int(entry.get("max_memory_items", 0) or 0),
                "decay_model_id": decay_model_id if decay_model_id else None,
                "eviction_rule_id": eviction_rule_id,
                "deterministic_eviction_rule_id": eviction_rule_id,
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        retention_policy_id_set.add(retention_policy_id)
    retention_rows = sorted(retention_rows, key=lambda row: str(row.get("retention_policy_id", "")))

    _epistemic_record, policy_rows_raw, policy_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/epistemic_policy_registry.json",
        expected_schema_id="dominium.registry.epistemic_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if policy_load_errors:
        return [], [], [], [], policy_load_errors

    policy_rows: List[dict] = []
    epistemic_policy_id_set = set()
    for entry in sorted(policy_rows_raw, key=lambda row: str((row or {}).get("epistemic_policy_id", ""))):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_epistemic_policy_entry",
                    "message": "epistemic policy entry must be object",
                    "path": "$.policies",
                }
            )
            continue
        epistemic_policy_id = str(entry.get("epistemic_policy_id", "")).strip()
        if not epistemic_policy_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.invalid_epistemic_policy_entry",
                    "message": "epistemic policy entry missing epistemic_policy_id",
                    "path": "$.policies.epistemic_policy_id",
                }
            )
            continue
        if epistemic_policy_id in epistemic_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.duplicate_epistemic_policy_id",
                    "message": "duplicate epistemic_policy_id '{}'".format(epistemic_policy_id),
                    "path": "$.policies.epistemic_policy_id",
                }
            )
            continue
        schema_payload = dict(entry)
        schema_payload["schema_version"] = "1.0.0"
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="epistemic_policy",
            payload=schema_payload,
            path="data/registries/epistemic_policy_registry.json#{}".format(epistemic_policy_id),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        retention_policy_id = str(entry.get("retention_policy_id", "")).strip()
        if retention_policy_id not in retention_policy_id_set:
            errors.append(
                {
                    "code": "refuse.registry_compile.epistemic_retention_policy_missing",
                    "message": "epistemic policy '{}' references unknown retention_policy_id '{}'".format(
                        epistemic_policy_id,
                        retention_policy_id,
                    ),
                    "path": "$.policies.retention_policy_id",
                }
            )
            continue

        allowed_channels = _sorted_unique_strings(list(entry.get("allowed_observation_channels") or []))
        forbidden_channels = _sorted_unique_strings(list(entry.get("forbidden_channels") or []))
        channel_overlap = sorted(set(allowed_channels).intersection(set(forbidden_channels)))
        if channel_overlap:
            errors.append(
                {
                    "code": "refuse.registry_compile.epistemic_channel_conflict",
                    "message": "epistemic policy '{}' overlaps allowed and forbidden channels: {}".format(
                        epistemic_policy_id,
                        ",".join(channel_overlap),
                    ),
                    "path": "$.policies",
                }
            )
            continue

        precision_rows = []
        for item in sorted(
            (dict(row) for row in (entry.get("max_precision_rules") or []) if isinstance(row, dict)),
            key=lambda row: (
                str(row.get("channel_id", "")),
                int(row.get("max_distance_mm", 0) or 0),
                str(row.get("rule_id", "")),
            ),
        ):
            precision_rows.append(
                {
                    "rule_id": str(item.get("rule_id", "")).strip(),
                    "channel_id": str(item.get("channel_id", "")).strip(),
                    "max_distance_mm": int(item.get("max_distance_mm", 0) or 0),
                    "position_quantization_mm": int(item.get("position_quantization_mm", 1) or 1),
                    "orientation_quantization_mdeg": int(item.get("orientation_quantization_mdeg", 1) or 1),
                }
            )

        policy_rows.append(
            {
                "epistemic_policy_id": epistemic_policy_id,
                "description": str(entry.get("description", "")).strip(),
                "allowed_observation_channels": allowed_channels,
                "forbidden_channels": forbidden_channels,
                "retention_policy_id": retention_policy_id,
                "inference_policy_id": entry.get("inference_policy_id"),
                "max_precision_rules": precision_rows,
                "deterministic_filters": _sorted_unique_strings(list(entry.get("deterministic_filters") or [])),
                "extensions": dict(entry.get("extensions") or {}),
            }
        )
        epistemic_policy_id_set.add(epistemic_policy_id)
    policy_rows = sorted(policy_rows, key=lambda row: str(row.get("epistemic_policy_id", "")))
    return policy_rows, retention_rows, decay_rows, eviction_rows, errors


def _ui_rows(contrib: List[dict], schema_root: str) -> Tuple[List[dict], List[dict]]:
    selector_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[(?:\d+|\*)\])?(?:\.[A-Za-z_][A-Za-z0-9_]*(?:\[(?:\d+|\*)\])?)*$")

    def walk_widgets(widget: object) -> List[dict]:
        rows: List[dict] = []
        if not isinstance(widget, dict):
            return rows
        rows.append(widget)
        children = widget.get("children")
        if isinstance(children, list):
            for item in children:
                rows.extend(walk_widgets(item))
        return rows

    rows = []
    errors = []
    for row in contrib:
        if str(row.get("contrib_type", "")) != "ui_windows":
            continue
        payload, err = _payload_from_contribution(row)
        if err:
            errors.append({"code": "refuse.registry_compile.invalid_ui_payload", "message": err, "path": "$.windows"})
            continue
        window_id = str(row.get("id", "")).strip()
        schema_errors = _validate_schema_item(
            schema_root=schema_root,
            schema_name="ui_window",
            payload=payload,
            path=str(row.get("path", "")),
        )
        if schema_errors:
            errors.extend(schema_errors)
            continue

        payload_window_id = str(payload.get("window_id", "")).strip()
        if payload_window_id != window_id:
            errors.append(
                {
                    "code": "refuse.registry_compile.ui_window_id_mismatch",
                    "message": "ui window payload id '{}' does not match contribution id '{}'".format(
                        payload_window_id,
                        window_id,
                    ),
                    "path": "$.windows",
                }
            )
            continue

        for widget in walk_widgets(payload.get("widgets")):
            data_binding = widget.get("data_binding")
            if not isinstance(data_binding, dict):
                continue
            selector = str(data_binding.get("selector", "")).strip()
            if not selector_re.fullmatch(selector):
                errors.append(
                    {
                        "code": "refuse.registry_compile.invalid_ui_selector",
                        "message": "ui window '{}' has invalid selector '{}' in widget '{}'".format(
                            window_id,
                            selector,
                            str(widget.get("widget_id", "")),
                        ),
                        "path": "$.widgets",
                    }
                )
                continue
            if selector.startswith("truth_model"):
                errors.append(
                    {
                        "code": "refuse.registry_compile.truth_selector_forbidden",
                        "message": "ui window '{}' selector '{}' is forbidden (TruthModel access)".format(
                            window_id,
                            selector,
                        ),
                        "path": "$.widgets",
                    }
                )

        required_entitlements = payload.get("required_entitlements")
        rows.append(
            {
                "window_id": window_id,
                "title": str(payload.get("title", "")),
                "pack_id": str(row.get("pack_id", "")),
                "path": str(row.get("path", "")),
                "required_entitlements": sorted(set(str(item).strip() for item in required_entitlements if str(item).strip())),
                "required_lenses": sorted(
                    set(str(item).strip() for item in (payload.get("required_lenses") or []) if str(item).strip())
                ),
                "widgets": dict(payload.get("widgets") or {}),
            }
        )
    return sorted(rows, key=lambda item: (item["window_id"], item["pack_id"])), errors


def _finalize_registry_payload(payload: Dict[str, object]) -> Dict[str, object]:
    base = dict(payload)
    base["registry_hash"] = ""
    digest = canonical_sha256(base)
    payload["registry_hash"] = digest
    return payload


def _write_and_validate_registry(repo_root: str, schema_name: str, out_path: str, payload: Dict[str, object]) -> Tuple[str, Dict[str, object]]:
    validation = validate_instance(repo_root=repo_root, schema_name=schema_name, payload=payload, strict_top_level=True)
    if not bool(validation.get("valid", False)):
        return "", {
            "result": "refused",
            "errors": validation.get("errors", []),
        }
    _write_json(out_path, payload)
    return str(payload.get("registry_hash", "")), {"result": "complete"}


def compile_bundle(
    repo_root: str,
    bundle_id: str = DEFAULT_BUNDLE_ID,
    out_dir_rel: str = DEFAULT_REGISTRY_OUT_DIR_REL,
    lockfile_out_rel: str = DEFAULT_LOCKFILE_OUT_REL,
    packs_root_rel: str = "packs",
    schema_repo_root: str = "",
    use_cache: bool = True,
) -> Dict[str, object]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    out_dir = os.path.join(repo_root, out_dir_rel)
    lockfile_out = os.path.join(repo_root, lockfile_out_rel)
    _ensure_dir(out_dir)

    loaded = load_pack_set(repo_root=repo_root, packs_root_rel=packs_root_rel, schema_repo_root=schema_root)
    if loaded.get("result") != "complete":
        return loaded

    bundle = resolve_bundle_selection(
        bundle_id=bundle_id,
        packs=loaded.get("packs") or [],
        repo_root=repo_root,
        schema_repo_root=schema_root,
    )
    if bundle.get("result") != "complete":
        return bundle
    selected_pack_ids = list(bundle.get("selected_pack_ids") or [])

    resolved = resolve_packs(loaded.get("packs") or [], bundle_selection=selected_pack_ids)
    if resolved.get("result") != "complete":
        return resolved
    ordered_packs = list(resolved.get("ordered_pack_list") or [])

    contrib = parse_contributions(repo_root=repo_root, packs=ordered_packs)
    if contrib.get("result") != "complete":
        return contrib
    contributions = list(contrib.get("contributions") or [])

    key, input_manifest = build_cache_key(
        packs=ordered_packs,
        contributions=contributions,
        bundle_selection=selected_pack_ids,
        tool_version=COMPILER_VERSION,
    )

    if use_cache and cache_hit(repo_root, key):
        restored = restore_cache_entry(repo_root, key, out_dir=out_dir, lockfile_path=lockfile_out)
        if restored.get("result") == "complete":
            restored_lockfile_payload = {}
            restored_lockfile_error = "invalid json"
            try:
                restored_lockfile_payload = json.load(open(lockfile_out, "r", encoding="utf-8"))
                if isinstance(restored_lockfile_payload, dict):
                    restored_lockfile_error = ""
                else:
                    restored_lockfile_error = "invalid root object"
            except (OSError, ValueError):
                restored_lockfile_payload = {}
                restored_lockfile_error = "invalid json"
            if not restored_lockfile_error:
                lockfile_schema_status = validate_instance(
                    repo_root=schema_root,
                    schema_name="bundle_lockfile",
                    payload=restored_lockfile_payload,
                    strict_top_level=True,
                )
                lockfile_semantic_status = validate_lockfile_payload(restored_lockfile_payload)
                if bool(lockfile_schema_status.get("valid", False)) and lockfile_semantic_status.get("result") == "complete":
                    return {
                        "result": "complete",
                        "bundle_id": bundle_id,
                        "cache_key": key,
                        "cache_hit": True,
                        "out_dir": _norm(os.path.relpath(out_dir, repo_root)),
                        "lockfile_path": _norm(os.path.relpath(lockfile_out, repo_root)),
                        "ordered_pack_ids": [str(row.get("pack_id", "")) for row in ordered_packs],
                        "registry_hashes": dict(restored_lockfile_payload.get("registries") or {}),
                        "pack_lock_hash": str(restored_lockfile_payload.get("pack_lock_hash", "")),
                    }

    if not ordered_packs:
        null_result = write_null_boot_artifacts(
            repo_root=repo_root,
            out_dir_rel=out_dir_rel,
            lockfile_out_rel=lockfile_out_rel,
            bundle_id=str(bundle_id),
            schema_repo_root=schema_root,
        )
        if str(null_result.get("result", "")) != "complete":
            return null_result
        return {
            "result": "complete",
            "bundle_id": str(bundle_id),
            "cache_key": key,
            "cache_hit": False,
            "out_dir": _norm(os.path.relpath(out_dir, repo_root)),
            "lockfile_path": _norm(os.path.relpath(lockfile_out, repo_root)),
            "ordered_pack_ids": [],
            "registry_hashes": dict(null_result.get("registry_hashes") or {}),
            "pack_lock_hash": str(null_result.get("pack_lock_hash", "")),
        }

    generated_from = _generated_from_rows(ordered_packs)

    domain_rows, domain_errors = _domain_rows(contributions)
    law_rows, law_errors = _law_rows(contributions)
    experience_rows, experience_errors = _experience_rows(contributions)
    lens_rows, lens_errors = _lens_rows(contributions)
    activation_policy_rows, budget_policy_rows, fidelity_policy_rows, policy_errors = _policy_rows(
        contributions,
        schema_root=schema_root,
    )
    worldgen_constraints_rows, worldgen_constraints_errors = _worldgen_constraints_rows(
        contributions,
        schema_root=schema_root,
    )
    control_action_rows, controller_type_rows, control_registry_errors = _control_registry_rows(
        repo_root=repo_root,
    )
    interaction_action_rows, interaction_registry_errors = _interaction_registry_rows(
        repo_root=repo_root,
    )
    (
        surface_type_rows,
        tool_tag_rows,
        surface_visibility_policy_rows,
        action_surface_registry_errors,
    ) = _action_surface_registry_rows(
        repo_root=repo_root,
    )
    (
        governance_type_rows,
        diplomatic_state_rows,
        cohort_mapping_policy_rows,
        order_type_rows,
        role_rows,
        institution_type_rows,
        demography_policy_rows,
        death_model_rows,
        birth_model_rows,
        migration_model_rows,
        civilisation_registry_errors,
    ) = _civilisation_registry_rows(
        repo_root=repo_root,
    )
    (
        quantity_rows,
        exception_type_rows,
        conservation_contract_set_rows,
        conservation_registry_errors,
    ) = _conservation_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        base_dimension_rows,
        dimension_rows,
        unit_rows,
        quantity_type_rows,
        materials_dimension_registry_errors,
    ) = _materials_dimension_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        element_rows,
        compound_rows,
        mixture_rows,
        material_class_rows,
        quality_distribution_rows,
        material_taxonomy_registry_errors,
    ) = _material_taxonomy_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
        dimension_rows=dimension_rows,
        unit_rows=unit_rows,
    )
    (
        part_class_rows,
        connection_type_rows,
        blueprint_rows,
        material_structure_registry_errors,
    ) = _materials_structure_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        logistics_routing_rule_rows,
        logistics_graph_rows,
        logistics_registry_errors,
    ) = _logistics_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        provenance_event_type_rows,
        construction_policy_rows,
        construction_registry_errors,
    ) = _construction_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        failure_mode_rows,
        maintenance_policy_rows,
        backlog_growth_rule_rows,
        maintenance_registry_errors,
    ) = _maintenance_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        commitment_type_rows,
        causality_strictness_rows,
        commitment_registry_errors,
    ) = _commitment_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        budget_envelope_rows,
        arbitration_policy_rows,
        inspection_cache_policy_rows,
        performance_registry_errors,
    ) = _performance_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        inspection_section_rows,
        inspection_registry_errors,
    ) = _inspection_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        universe_physics_profile_rows,
        time_model_rows,
        numeric_precision_policy_rows,
        tier_taxonomy_rows,
        boundary_model_rows,
        universe_physics_registry_errors,
    ) = _universe_physics_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
        contributions=contributions,
        known_contract_set_ids=[str(row.get("contract_set_id", "")) for row in conservation_contract_set_rows],
        known_budget_envelope_ids=[str(row.get("envelope_id", "")) for row in budget_envelope_rows],
        known_arbitration_policy_ids=[str(row.get("arbitration_policy_id", "")) for row in arbitration_policy_rows],
        known_inspection_cache_policy_ids=[str(row.get("cache_policy_id", "")) for row in inspection_cache_policy_rows],
    )
    (
        transition_policy_rows,
        arbitration_rule_rows,
        transition_registry_errors,
    ) = _transition_policy_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    transition_reference_errors: List[dict] = []
    transition_policy_ids = set(
        str(row.get("transition_policy_id", "")).strip() for row in transition_policy_rows if str(row.get("transition_policy_id", "")).strip()
    )
    for taxonomy_row in tier_taxonomy_rows:
        taxonomy_id = str(taxonomy_row.get("taxonomy_id", "")).strip() or "<unknown>"
        tiers = set(str(item).strip() for item in list(taxonomy_row.get("tiers") or []) if str(item).strip())
        default_transition_policy_id = str(taxonomy_row.get("default_transition_policy_id", "")).strip()
        if default_transition_policy_id and default_transition_policy_id not in transition_policy_ids:
            transition_reference_errors.append(
                {
                    "code": "refuse.registry_compile.tier_taxonomy_transition_policy_missing",
                    "message": "tier taxonomy '{}' references unknown default_transition_policy_id '{}'".format(
                        taxonomy_id,
                        default_transition_policy_id,
                    ),
                    "path": "$.taxonomies.default_transition_policy_id",
                }
            )
        for transition_row in list(taxonomy_row.get("allowed_transitions") or []):
            if not isinstance(transition_row, dict):
                continue
            from_tier = str(transition_row.get("from_tier", "")).strip()
            to_tier = str(transition_row.get("to_tier", "")).strip()
            if from_tier and from_tier not in tiers:
                transition_reference_errors.append(
                    {
                        "code": "refuse.registry_compile.tier_taxonomy_transition_invalid",
                        "message": "tier taxonomy '{}' transition from_tier '{}' is not declared in tiers".format(
                            taxonomy_id,
                            from_tier,
                        ),
                        "path": "$.taxonomies.allowed_transitions.from_tier",
                    }
                )
            if to_tier and to_tier not in tiers:
                transition_reference_errors.append(
                    {
                        "code": "refuse.registry_compile.tier_taxonomy_transition_invalid",
                        "message": "tier taxonomy '{}' transition to_tier '{}' is not declared in tiers".format(
                            taxonomy_id,
                            to_tier,
                        ),
                        "path": "$.taxonomies.allowed_transitions.to_tier",
                    }
                )

    for profile_row in universe_physics_profile_rows:
        profile_id = str(profile_row.get("physics_profile_id", "")).strip() or "<unknown>"
        extensions = dict(profile_row.get("extensions") or {})
        allowed_policy_ids = sorted(
            set(str(item).strip() for item in list(extensions.get("allowed_transition_policy_ids") or []) if str(item).strip())
        )
        default_policy_id = str(extensions.get("default_transition_policy_id", "")).strip()
        for policy_id in allowed_policy_ids:
            if policy_id not in transition_policy_ids:
                transition_reference_errors.append(
                    {
                        "code": "refuse.registry_compile.physics_profile_transition_policy_missing",
                        "message": "physics profile '{}' references unknown allowed transition policy '{}'".format(
                            profile_id,
                            policy_id,
                        ),
                        "path": "$.physics_profiles.extensions.allowed_transition_policy_ids",
                    }
                )
        if default_policy_id and default_policy_id not in transition_policy_ids:
            transition_reference_errors.append(
                {
                    "code": "refuse.registry_compile.physics_profile_transition_policy_missing",
                    "message": "physics profile '{}' references unknown default transition policy '{}'".format(
                        profile_id,
                        default_policy_id,
                    ),
                    "path": "$.physics_profiles.extensions.default_transition_policy_id",
                }
            )
        if default_policy_id and allowed_policy_ids and default_policy_id not in set(allowed_policy_ids):
            transition_reference_errors.append(
                {
                    "code": "refuse.registry_compile.physics_profile_transition_policy_invalid",
                    "message": "physics profile '{}' default transition policy '{}' is not present in allowed_transition_policy_ids".format(
                        profile_id,
                        default_policy_id,
                    ),
                    "path": "$.physics_profiles.extensions.default_transition_policy_id",
                }
            )
    (
        time_control_policy_rows,
        dt_quantization_rule_rows,
        compaction_policy_rows,
        time_control_registry_errors,
    ) = _time_control_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
        known_time_model_ids=[str(row.get("time_model_id", "")) for row in time_model_rows],
    )
    body_shape_rows, body_shape_registry_errors = _body_shape_registry_rows(
        repo_root=repo_root,
    )
    view_mode_rows, view_mode_registry_errors = _view_mode_registry_rows(
        repo_root=repo_root,
    )
    (
        instrument_type_rows,
        calibration_model_rows,
        diegetic_registry_errors,
    ) = _diegetic_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        render_proxy_rows,
        cosmetic_rows,
        cosmetic_policy_rows,
        render_primitive_rows,
        material_template_rows,
        label_policy_rows,
        lod_policy_rows,
        representation_rule_rows,
        representation_registry_errors,
    ) = _representation_registry_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    (
        net_replication_policy_rows,
        net_resync_strategy_rows,
        net_server_policy_rows,
        anti_cheat_policy_rows,
        anti_cheat_module_rows,
        securex_policy_rows,
        server_profile_rows,
        net_registry_errors,
    ) = _network_policy_rows(
        repo_root=repo_root,
        known_law_profile_ids=[str(row.get("law_profile_id", "")) for row in law_rows if str(row.get("law_profile_id", ""))],
    )
    (
        shard_map_rows,
        perception_interest_policy_rows,
        hybrid_registry_errors,
    ) = _hybrid_policy_rows(
        repo_root=repo_root,
        schema_root=schema_root,
        known_replication_policy_ids=[str(row.get("policy_id", "")) for row in net_replication_policy_rows],
        net_server_policy_rows=net_server_policy_rows,
    )
    (
        epistemic_policy_rows,
        retention_policy_rows,
        decay_model_rows,
        eviction_rule_rows,
        epistemic_registry_errors,
    ) = _epistemic_policy_rows(
        repo_root=repo_root,
        schema_root=schema_root,
    )
    astronomy_rows, reference_frame_rows, site_rows, astronomy_errors = _astronomy_rows(
        contributions,
        schema_root=schema_root,
    )
    ephemeris_rows, terrain_tile_rows, real_data_errors = _real_data_rows(
        contributions,
        schema_root=schema_root,
    )
    ui_rows, ui_errors = _ui_rows(contributions, schema_root=schema_root)
    materials_reference_errors: List[dict] = []
    quantity_type_id_set = set(str(row.get("quantity_id", "")).strip() for row in quantity_type_rows if str(row.get("quantity_id", "")).strip())
    for contract_set_row in conservation_contract_set_rows:
        contract_set_id = str(contract_set_row.get("contract_set_id", "")).strip() or "<unknown>"
        for quantity_row in list(contract_set_row.get("quantities") or []):
            if not isinstance(quantity_row, dict):
                continue
            quantity_id = str(quantity_row.get("quantity_id", "")).strip()
            if quantity_id and quantity_id not in quantity_type_id_set:
                materials_reference_errors.append(
                    {
                        "code": "refuse.registry_compile.conservation_quantity_type_missing",
                        "message": "conservation contract '{}' references quantity_id '{}' missing from quantity_type_registry".format(
                            contract_set_id,
                            quantity_id,
                        ),
                        "path": "$.contract_sets.quantities.quantity_id",
                    }
                )
    all_errors = (
        domain_errors
        + law_errors
        + experience_errors
        + lens_errors
        + policy_errors
        + worldgen_constraints_errors
        + control_registry_errors
        + interaction_registry_errors
        + action_surface_registry_errors
        + civilisation_registry_errors
        + conservation_registry_errors
        + materials_dimension_registry_errors
        + material_taxonomy_registry_errors
        + material_structure_registry_errors
        + logistics_registry_errors
        + construction_registry_errors
        + maintenance_registry_errors
        + commitment_registry_errors
        + materials_reference_errors
        + performance_registry_errors
        + inspection_registry_errors
        + universe_physics_registry_errors
        + transition_registry_errors
        + transition_reference_errors
        + time_control_registry_errors
        + body_shape_registry_errors
        + view_mode_registry_errors
        + diegetic_registry_errors
        + representation_registry_errors
        + net_registry_errors
        + hybrid_registry_errors
        + epistemic_registry_errors
        + astronomy_errors
        + real_data_errors
        + ui_errors
    )
    if all_errors:
        return {
            "result": "refused",
            "errors": sorted(all_errors, key=lambda row: (row["code"], row["path"], row["message"])),
        }

    universe_physics_profile_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "physics_profiles": universe_physics_profile_rows,
        }
    )
    time_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "time_models": time_model_rows,
        }
    )
    time_control_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": time_control_policy_rows,
        }
    )
    dt_quantization_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "rules": dt_quantization_rule_rows,
        }
    )
    compaction_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": compaction_policy_rows,
        }
    )
    numeric_precision_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "precision_policies": numeric_precision_policy_rows,
        }
    )
    tier_taxonomy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "taxonomies": tier_taxonomy_rows,
        }
    )
    transition_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": transition_policy_rows,
        }
    )
    arbitration_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "rules": arbitration_rule_rows,
        }
    )
    budget_envelope_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "envelopes": budget_envelope_rows,
        }
    )
    arbitration_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": arbitration_policy_rows,
        }
    )
    inspection_cache_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": inspection_cache_policy_rows,
        }
    )
    inspection_section_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "sections": inspection_section_rows,
        }
    )
    boundary_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "boundary_models": boundary_model_rows,
        }
    )
    conservation_contract_set_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "contract_sets": conservation_contract_set_rows,
        }
    )
    quantity_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "quantities": quantity_rows,
        }
    )
    exception_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "exception_types": exception_type_rows,
        }
    )
    base_dimension_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "base_dimensions": base_dimension_rows,
        }
    )
    dimension_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "dimensions": dimension_rows,
        }
    )
    unit_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "units": unit_rows,
        }
    )
    quantity_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "quantity_types": quantity_type_rows,
        }
    )
    element_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "elements": element_rows,
        }
    )
    compound_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "compounds": compound_rows,
        }
    )
    mixture_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "mixtures": mixture_rows,
        }
    )
    material_class_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "materials": material_class_rows,
        }
    )
    quality_distribution_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "quality_distribution_models": quality_distribution_rows,
        }
    )
    part_class_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "part_classes": part_class_rows,
        }
    )
    connection_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "connection_types": connection_type_rows,
        }
    )
    blueprint_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "blueprints": blueprint_rows,
        }
    )
    logistics_routing_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "routing_rules": logistics_routing_rule_rows,
        }
    )
    logistics_graph_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "graphs": logistics_graph_rows,
        }
    )
    provenance_event_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "event_types": provenance_event_type_rows,
        }
    )
    construction_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": construction_policy_rows,
        }
    )
    failure_mode_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "failure_modes": failure_mode_rows,
        }
    )
    maintenance_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": maintenance_policy_rows,
        }
    )
    backlog_growth_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "rules": backlog_growth_rule_rows,
        }
    )
    commitment_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "commitment_types": commitment_type_rows,
        }
    )
    causality_strictness_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "strictness_levels": causality_strictness_rows,
        }
    )
    domain_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "domains": domain_rows,
        }
    )
    law_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "law_profiles": law_rows,
        }
    )
    experience_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "experience_profiles": experience_rows,
        }
    )
    lens_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "lenses": lens_rows,
        }
    )
    control_action_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "actions": control_action_rows,
        }
    )
    interaction_action_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "actions": interaction_action_rows,
        }
    )
    surface_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "surface_types": surface_type_rows,
        }
    )
    tool_tag_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "tool_tags": tool_tag_rows,
        }
    )
    surface_visibility_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": surface_visibility_policy_rows,
        }
    )
    controller_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "controller_types": controller_type_rows,
        }
    )
    governance_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "governance_types": governance_type_rows,
        }
    )
    diplomatic_state_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "states": diplomatic_state_rows,
        }
    )
    cohort_mapping_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": cohort_mapping_policy_rows,
        }
    )
    order_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "order_types": order_type_rows,
        }
    )
    role_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "roles": role_rows,
        }
    )
    institution_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "institution_types": institution_type_rows,
        }
    )
    demography_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": demography_policy_rows,
        }
    )
    death_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "death_models": death_model_rows,
        }
    )
    birth_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "birth_models": birth_model_rows,
        }
    )
    migration_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "migration_models": migration_model_rows,
        }
    )
    body_shape_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "shape_types": body_shape_rows,
        }
    )
    view_mode_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "view_modes": view_mode_rows,
        }
    )
    instrument_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "instrument_types": instrument_type_rows,
        }
    )
    calibration_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "calibration_models": calibration_model_rows,
        }
    )
    render_proxy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "render_proxies": render_proxy_rows,
        }
    )
    cosmetic_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "cosmetics": cosmetic_rows,
        }
    )
    cosmetic_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": cosmetic_policy_rows,
        }
    )
    render_primitive_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "primitives": render_primitive_rows,
        }
    )
    procedural_material_template_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "material_templates": material_template_rows,
        }
    )
    label_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "label_policies": label_policy_rows,
        }
    )
    lod_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "lod_policies": lod_policy_rows,
        }
    )
    representation_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "representation_rules": representation_rule_rows,
        }
    )
    net_replication_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": net_replication_policy_rows,
        }
    )
    net_resync_strategy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "strategies": net_resync_strategy_rows,
        }
    )
    net_server_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": net_server_policy_rows,
        }
    )
    shard_map_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "shard_maps": shard_map_rows,
        }
    )
    perception_interest_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": perception_interest_policy_rows,
        }
    )
    epistemic_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": epistemic_policy_rows,
        }
    )
    retention_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": retention_policy_rows,
        }
    )
    decay_model_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "decay_models": decay_model_rows,
        }
    )
    eviction_rule_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "eviction_rules": eviction_rule_rows,
        }
    )
    anti_cheat_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": anti_cheat_policy_rows,
        }
    )
    anti_cheat_module_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "modules": anti_cheat_module_rows,
        }
    )
    securex_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "policies": securex_policy_rows,
        }
    )
    server_profile_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "profiles": server_profile_rows,
        }
    )
    activation_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "activation_policies": activation_policy_rows,
        }
    )
    budget_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "budget_policies": budget_policy_rows,
        }
    )
    fidelity_policy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "fidelity_policies": fidelity_policy_rows,
        }
    )
    worldgen_constraints_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "constraints": worldgen_constraints_rows,
        }
    )
    astronomy_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "entries": astronomy_rows,
            "reference_frames": reference_frame_rows,
            "search_index": _search_index(astronomy_rows, "object_id"),
        }
    )
    site_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "sites": site_rows,
            "search_index": _search_index(site_rows, "site_id"),
        }
    )
    ephemeris_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "tables": ephemeris_rows,
        }
    )
    terrain_tile_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "tiles": terrain_tile_rows,
        }
    )
    ui_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "windows": ui_rows,
        }
    )

    registry_payloads = {
        "conservation_contract_set_registry": (
            "conservation_contract_set_registry",
            conservation_contract_set_payload,
        ),
        "quantity_registry": ("quantity_registry", quantity_payload),
        "exception_type_registry": ("exception_type_registry", exception_type_payload),
        "base_dimension_registry": ("base_dimension_registry", base_dimension_payload),
        "dimension_registry": ("dimension_registry", dimension_payload),
        "unit_registry": ("unit_registry", unit_payload),
        "quantity_type_registry": ("quantity_type_registry", quantity_type_payload),
        "element_registry": ("element_registry", element_payload),
        "compound_registry": ("compound_registry", compound_payload),
        "mixture_registry": ("mixture_registry", mixture_payload),
        "material_class_registry": ("material_class_registry", material_class_payload),
        "quality_distribution_registry": ("quality_distribution_registry", quality_distribution_payload),
        "part_class_registry": ("part_class_registry", part_class_payload),
        "connection_type_registry": ("connection_type_registry", connection_type_payload),
        "blueprint_registry": ("blueprint_registry", blueprint_payload),
        "logistics_routing_rule_registry": ("logistics_routing_rule_registry", logistics_routing_rule_payload),
        "logistics_graph_registry": ("logistics_graph_registry", logistics_graph_payload),
        "provenance_event_type_registry": ("provenance_event_type_registry", provenance_event_type_payload),
        "construction_policy_registry": ("construction_policy_registry", construction_policy_payload),
        "failure_mode_registry": ("failure_mode_registry", failure_mode_payload),
        "maintenance_policy_registry": ("maintenance_policy_registry", maintenance_policy_payload),
        "backlog_growth_rule_registry": ("backlog_growth_rule_registry", backlog_growth_rule_payload),
        "commitment_type_registry": ("commitment_type_registry", commitment_type_payload),
        "causality_strictness_registry": ("causality_strictness_registry", causality_strictness_payload),
        "universe_physics_profile_registry": ("universe_physics_profile_registry", universe_physics_profile_payload),
        "time_model_registry": ("time_model_registry", time_model_payload),
        "time_control_policy_registry": ("time_control_policy_registry", time_control_policy_payload),
        "dt_quantization_rule_registry": ("dt_quantization_rule_registry", dt_quantization_rule_payload),
        "compaction_policy_registry": ("compaction_policy_registry", compaction_policy_payload),
        "numeric_precision_policy_registry": ("numeric_precision_policy_registry", numeric_precision_policy_payload),
        "tier_taxonomy_registry": ("tier_taxonomy_registry", tier_taxonomy_payload),
        "transition_policy_registry": ("transition_policy_registry", transition_policy_payload),
        "arbitration_rule_registry": ("arbitration_rule_registry", arbitration_rule_payload),
        "budget_envelope_registry": ("budget_envelope_registry", budget_envelope_payload),
        "arbitration_policy_registry": ("arbitration_policy_registry", arbitration_policy_payload),
        "inspection_cache_policy_registry": ("inspection_cache_policy_registry", inspection_cache_policy_payload),
        "inspection_section_registry": ("inspection_section_registry", inspection_section_payload),
        "boundary_model_registry": ("boundary_model_registry", boundary_model_payload),
        "domain_registry": ("domain_registry", domain_payload),
        "law_registry": ("law_registry", law_payload),
        "experience_registry": ("experience_registry", experience_payload),
        "lens_registry": ("lens_registry", lens_payload),
        "control_action_registry": ("control_action_registry", control_action_payload),
        "interaction_action_registry": ("interaction_action_registry", interaction_action_payload),
        "surface_type_registry": ("surface_type_registry", surface_type_payload),
        "tool_tag_registry": ("tool_tag_registry", tool_tag_payload),
        "surface_visibility_policy_registry": (
            "surface_visibility_policy_registry",
            surface_visibility_policy_payload,
        ),
        "controller_type_registry": ("controller_type_registry", controller_type_payload),
        "governance_type_registry": ("governance_type_registry", governance_type_payload),
        "diplomatic_state_registry": ("diplomatic_state_registry", diplomatic_state_payload),
        "cohort_mapping_policy_registry": ("cohort_mapping_policy_registry", cohort_mapping_policy_payload),
        "order_type_registry": ("order_type_registry", order_type_payload),
        "role_registry": ("role_registry", role_payload),
        "institution_type_registry": ("institution_type_registry", institution_type_payload),
        "demography_policy_registry": ("demography_policy_registry", demography_policy_payload),
        "death_model_registry": ("death_model_registry", death_model_payload),
        "birth_model_registry": ("birth_model_registry", birth_model_payload),
        "migration_model_registry": ("migration_model_registry", migration_model_payload),
        "body_shape_registry": ("body_shape_registry", body_shape_payload),
        "view_mode_registry": ("view_mode_registry", view_mode_payload),
        "instrument_type_registry": ("instrument_type_registry", instrument_type_payload),
        "calibration_model_registry": ("calibration_model_registry", calibration_model_payload),
        "render_proxy_registry": ("render_proxy_registry", render_proxy_payload),
        "cosmetic_registry": ("cosmetic_registry", cosmetic_payload),
        "cosmetic_policy_registry": ("cosmetic_policy_registry", cosmetic_policy_payload),
        "render_primitive_registry": ("render_primitive_registry", render_primitive_payload),
        "procedural_material_template_registry": (
            "procedural_material_template_registry",
            procedural_material_template_payload,
        ),
        "label_policy_registry": ("label_policy_registry", label_policy_payload),
        "lod_policy_registry": ("lod_policy_registry", lod_policy_payload),
        "representation_rule_registry": ("representation_rule_registry", representation_rule_payload),
        "net_replication_policy_registry": ("net_replication_policy_registry", net_replication_policy_payload),
        "net_resync_strategy_registry": ("net_resync_strategy_registry", net_resync_strategy_payload),
        "net_server_policy_registry": ("net_server_policy_registry", net_server_policy_payload),
        "securex_policy_registry": ("securex_policy_registry", securex_policy_payload),
        "server_profile_registry": ("server_profile_registry", server_profile_payload),
        "shard_map_registry": ("shard_map_registry", shard_map_payload),
        "perception_interest_policy_registry": (
            "perception_interest_policy_registry",
            perception_interest_policy_payload,
        ),
        "epistemic_policy_registry": ("epistemic_policy_registry", epistemic_policy_payload),
        "retention_policy_registry": ("retention_policy_registry", retention_policy_payload),
        "decay_model_registry": ("decay_model_registry", decay_model_payload),
        "eviction_rule_registry": ("eviction_rule_registry", eviction_rule_payload),
        "anti_cheat_policy_registry": ("anti_cheat_policy_registry", anti_cheat_policy_payload),
        "anti_cheat_module_registry": ("anti_cheat_module_registry", anti_cheat_module_payload),
        "activation_policy_registry": ("activation_policy_registry", activation_policy_payload),
        "budget_policy_registry": ("budget_policy_registry", budget_policy_payload),
        "fidelity_policy_registry": ("fidelity_policy_registry", fidelity_policy_payload),
        "worldgen_constraints_registry": ("worldgen_constraints_registry", worldgen_constraints_payload),
        "astronomy_catalog_index": ("astronomy_catalog_index", astronomy_payload),
        "site_registry_index": ("site_registry_index", site_payload),
        "ephemeris_registry": ("ephemeris_registry", ephemeris_payload),
        "terrain_tile_registry": ("terrain_tile_registry", terrain_tile_payload),
        "ui_registry": ("ui_registry", ui_payload),
    }
    registry_hashes = {}
    output_files = []
    for registry_key in (
        "conservation_contract_set_registry",
        "quantity_registry",
        "exception_type_registry",
        "base_dimension_registry",
        "dimension_registry",
        "unit_registry",
        "quantity_type_registry",
        "element_registry",
        "compound_registry",
        "mixture_registry",
        "material_class_registry",
        "quality_distribution_registry",
        "part_class_registry",
        "connection_type_registry",
        "blueprint_registry",
        "logistics_routing_rule_registry",
        "logistics_graph_registry",
        "provenance_event_type_registry",
        "construction_policy_registry",
        "failure_mode_registry",
        "maintenance_policy_registry",
        "backlog_growth_rule_registry",
        "commitment_type_registry",
        "causality_strictness_registry",
        "universe_physics_profile_registry",
        "time_model_registry",
        "time_control_policy_registry",
        "dt_quantization_rule_registry",
        "compaction_policy_registry",
        "numeric_precision_policy_registry",
        "tier_taxonomy_registry",
        "transition_policy_registry",
        "arbitration_rule_registry",
        "budget_envelope_registry",
        "arbitration_policy_registry",
        "inspection_cache_policy_registry",
        "inspection_section_registry",
        "boundary_model_registry",
        "domain_registry",
        "law_registry",
        "experience_registry",
        "lens_registry",
        "control_action_registry",
        "interaction_action_registry",
        "surface_type_registry",
        "tool_tag_registry",
        "surface_visibility_policy_registry",
        "controller_type_registry",
        "governance_type_registry",
        "diplomatic_state_registry",
        "cohort_mapping_policy_registry",
        "order_type_registry",
        "role_registry",
        "institution_type_registry",
        "demography_policy_registry",
        "death_model_registry",
        "birth_model_registry",
        "migration_model_registry",
        "body_shape_registry",
        "view_mode_registry",
        "instrument_type_registry",
        "calibration_model_registry",
        "render_proxy_registry",
        "cosmetic_registry",
        "cosmetic_policy_registry",
        "render_primitive_registry",
        "procedural_material_template_registry",
        "label_policy_registry",
        "lod_policy_registry",
        "representation_rule_registry",
        "net_replication_policy_registry",
        "net_resync_strategy_registry",
        "net_server_policy_registry",
        "securex_policy_registry",
        "server_profile_registry",
        "shard_map_registry",
        "perception_interest_policy_registry",
        "epistemic_policy_registry",
        "retention_policy_registry",
        "decay_model_registry",
        "eviction_rule_registry",
        "anti_cheat_policy_registry",
        "anti_cheat_module_registry",
        "activation_policy_registry",
        "budget_policy_registry",
        "fidelity_policy_registry",
        "worldgen_constraints_registry",
        "astronomy_catalog_index",
        "site_registry_index",
        "ephemeris_registry",
        "terrain_tile_registry",
        "ui_registry",
    ):
        schema_name, payload = registry_payloads[registry_key]
        out_path = os.path.join(out_dir, REGISTRY_OUTPUT_FILENAMES[registry_key])
        digest, status = _write_and_validate_registry(schema_root, schema_name, out_path, payload)
        if status.get("result") != "complete":
            return {
                "result": "refused",
                "errors": status.get("errors", []),
            }
        registry_hashes[registry_key + "_hash"] = digest
        output_files.append(out_path)

    resolved_packs = [
        {
            "pack_id": str(row.get("pack_id", "")),
            "version": str(row.get("version", "")),
            "canonical_hash": str((row.get("manifest") or {}).get("canonical_hash", "")),
            "signature_status": str(row.get("signature_status", "")),
        }
        for row in ordered_packs
    ]
    pack_lock_hash = compute_pack_lock_hash(resolved_packs)
    lockfile_payload = {
        "lockfile_version": "1.0.0",
        "bundle_id": str(bundle_id),
        "resolved_packs": resolved_packs,
        "registries": {
            "conservation_contract_set_registry_hash": registry_hashes["conservation_contract_set_registry_hash"],
            "quantity_registry_hash": registry_hashes["quantity_registry_hash"],
            "exception_type_registry_hash": registry_hashes["exception_type_registry_hash"],
            "base_dimension_registry_hash": registry_hashes["base_dimension_registry_hash"],
            "dimension_registry_hash": registry_hashes["dimension_registry_hash"],
            "unit_registry_hash": registry_hashes["unit_registry_hash"],
            "quantity_type_registry_hash": registry_hashes["quantity_type_registry_hash"],
            "element_registry_hash": registry_hashes["element_registry_hash"],
            "compound_registry_hash": registry_hashes["compound_registry_hash"],
            "mixture_registry_hash": registry_hashes["mixture_registry_hash"],
            "material_class_registry_hash": registry_hashes["material_class_registry_hash"],
            "quality_distribution_registry_hash": registry_hashes["quality_distribution_registry_hash"],
            "part_class_registry_hash": registry_hashes["part_class_registry_hash"],
            "connection_type_registry_hash": registry_hashes["connection_type_registry_hash"],
            "blueprint_registry_hash": registry_hashes["blueprint_registry_hash"],
            "logistics_routing_rule_registry_hash": registry_hashes["logistics_routing_rule_registry_hash"],
            "logistics_graph_registry_hash": registry_hashes["logistics_graph_registry_hash"],
            "provenance_event_type_registry_hash": registry_hashes["provenance_event_type_registry_hash"],
            "construction_policy_registry_hash": registry_hashes["construction_policy_registry_hash"],
            "failure_mode_registry_hash": registry_hashes["failure_mode_registry_hash"],
            "maintenance_policy_registry_hash": registry_hashes["maintenance_policy_registry_hash"],
            "backlog_growth_rule_registry_hash": registry_hashes["backlog_growth_rule_registry_hash"],
            "commitment_type_registry_hash": registry_hashes["commitment_type_registry_hash"],
            "causality_strictness_registry_hash": registry_hashes["causality_strictness_registry_hash"],
            "universe_physics_profile_registry_hash": registry_hashes["universe_physics_profile_registry_hash"],
            "time_model_registry_hash": registry_hashes["time_model_registry_hash"],
            "time_control_policy_registry_hash": registry_hashes["time_control_policy_registry_hash"],
            "dt_quantization_rule_registry_hash": registry_hashes["dt_quantization_rule_registry_hash"],
            "compaction_policy_registry_hash": registry_hashes["compaction_policy_registry_hash"],
            "numeric_precision_policy_registry_hash": registry_hashes["numeric_precision_policy_registry_hash"],
            "tier_taxonomy_registry_hash": registry_hashes["tier_taxonomy_registry_hash"],
            "transition_policy_registry_hash": registry_hashes["transition_policy_registry_hash"],
            "arbitration_rule_registry_hash": registry_hashes["arbitration_rule_registry_hash"],
            "budget_envelope_registry_hash": registry_hashes["budget_envelope_registry_hash"],
            "arbitration_policy_registry_hash": registry_hashes["arbitration_policy_registry_hash"],
            "inspection_cache_policy_registry_hash": registry_hashes["inspection_cache_policy_registry_hash"],
            "inspection_section_registry_hash": registry_hashes["inspection_section_registry_hash"],
            "boundary_model_registry_hash": registry_hashes["boundary_model_registry_hash"],
            "domain_registry_hash": registry_hashes["domain_registry_hash"],
            "law_registry_hash": registry_hashes["law_registry_hash"],
            "experience_registry_hash": registry_hashes["experience_registry_hash"],
            "lens_registry_hash": registry_hashes["lens_registry_hash"],
            "control_action_registry_hash": registry_hashes["control_action_registry_hash"],
            "interaction_action_registry_hash": registry_hashes["interaction_action_registry_hash"],
            "surface_type_registry_hash": registry_hashes["surface_type_registry_hash"],
            "tool_tag_registry_hash": registry_hashes["tool_tag_registry_hash"],
            "surface_visibility_policy_registry_hash": registry_hashes[
                "surface_visibility_policy_registry_hash"
            ],
            "controller_type_registry_hash": registry_hashes["controller_type_registry_hash"],
            "governance_type_registry_hash": registry_hashes["governance_type_registry_hash"],
            "diplomatic_state_registry_hash": registry_hashes["diplomatic_state_registry_hash"],
            "cohort_mapping_policy_registry_hash": registry_hashes["cohort_mapping_policy_registry_hash"],
            "order_type_registry_hash": registry_hashes["order_type_registry_hash"],
            "role_registry_hash": registry_hashes["role_registry_hash"],
            "institution_type_registry_hash": registry_hashes["institution_type_registry_hash"],
            "demography_policy_registry_hash": registry_hashes["demography_policy_registry_hash"],
            "death_model_registry_hash": registry_hashes["death_model_registry_hash"],
            "birth_model_registry_hash": registry_hashes["birth_model_registry_hash"],
            "migration_model_registry_hash": registry_hashes["migration_model_registry_hash"],
            "body_shape_registry_hash": registry_hashes["body_shape_registry_hash"],
            "view_mode_registry_hash": registry_hashes["view_mode_registry_hash"],
            "instrument_type_registry_hash": registry_hashes["instrument_type_registry_hash"],
            "calibration_model_registry_hash": registry_hashes["calibration_model_registry_hash"],
            "render_proxy_registry_hash": registry_hashes["render_proxy_registry_hash"],
            "cosmetic_registry_hash": registry_hashes["cosmetic_registry_hash"],
            "cosmetic_policy_registry_hash": registry_hashes["cosmetic_policy_registry_hash"],
            "render_primitive_registry_hash": registry_hashes["render_primitive_registry_hash"],
            "procedural_material_template_registry_hash": registry_hashes["procedural_material_template_registry_hash"],
            "label_policy_registry_hash": registry_hashes["label_policy_registry_hash"],
            "lod_policy_registry_hash": registry_hashes["lod_policy_registry_hash"],
            "representation_rule_registry_hash": registry_hashes["representation_rule_registry_hash"],
            "net_replication_policy_registry_hash": registry_hashes["net_replication_policy_registry_hash"],
            "net_resync_strategy_registry_hash": registry_hashes["net_resync_strategy_registry_hash"],
            "net_server_policy_registry_hash": registry_hashes["net_server_policy_registry_hash"],
            "securex_policy_registry_hash": registry_hashes["securex_policy_registry_hash"],
            "server_profile_registry_hash": registry_hashes["server_profile_registry_hash"],
            "shard_map_registry_hash": registry_hashes["shard_map_registry_hash"],
            "perception_interest_policy_registry_hash": registry_hashes["perception_interest_policy_registry_hash"],
            "epistemic_policy_registry_hash": registry_hashes["epistemic_policy_registry_hash"],
            "retention_policy_registry_hash": registry_hashes["retention_policy_registry_hash"],
            "decay_model_registry_hash": registry_hashes["decay_model_registry_hash"],
            "eviction_rule_registry_hash": registry_hashes["eviction_rule_registry_hash"],
            "anti_cheat_policy_registry_hash": registry_hashes["anti_cheat_policy_registry_hash"],
            "anti_cheat_module_registry_hash": registry_hashes["anti_cheat_module_registry_hash"],
            "activation_policy_registry_hash": registry_hashes["activation_policy_registry_hash"],
            "budget_policy_registry_hash": registry_hashes["budget_policy_registry_hash"],
            "fidelity_policy_registry_hash": registry_hashes["fidelity_policy_registry_hash"],
            "worldgen_constraints_registry_hash": registry_hashes["worldgen_constraints_registry_hash"],
            "astronomy_catalog_index_hash": registry_hashes["astronomy_catalog_index_hash"],
            "site_registry_index_hash": registry_hashes["site_registry_index_hash"],
            "ephemeris_registry_hash": registry_hashes["ephemeris_registry_hash"],
            "terrain_tile_registry_hash": registry_hashes["terrain_tile_registry_hash"],
            "ui_registry_hash": registry_hashes["ui_registry_hash"],
        },
        "compatibility_version": DEFAULT_COMPATIBILITY_VERSION,
        "pack_lock_hash": pack_lock_hash,
    }
    lock_validation = validate_lockfile_payload(lockfile_payload)
    if lock_validation.get("result") != "complete":
        return lock_validation
    _write_json(lockfile_out, lockfile_payload)

    if use_cache:
        cache_row = store_cache_entry(
            repo_root=repo_root,
            key=key,
            input_manifest=input_manifest,
            out_dir=out_dir,
            output_files=output_files,
            lockfile_path=lockfile_out,
        )
        if cache_row.get("result") != "complete":
            return _refusal("refuse.cache_store.store_failed", "failed to store cache entry", "$.cache")

    return {
        "result": "complete",
        "bundle_id": str(bundle_id),
        "cache_key": key,
        "cache_hit": False,
        "out_dir": _norm(os.path.relpath(out_dir, repo_root)),
        "lockfile_path": _norm(os.path.relpath(lockfile_out, repo_root)),
        "ordered_pack_ids": [row["pack_id"] for row in resolved_packs],
        "registry_hashes": lockfile_payload["registries"],
        "pack_lock_hash": pack_lock_hash,
    }
