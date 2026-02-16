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


def _representation_registry_rows(
    repo_root: str,
    schema_root: str,
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    errors: List[dict] = []

    _render_record, render_rows_raw, render_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/render_proxy_registry.json",
        expected_schema_id="dominium.registry.render_proxy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="render_proxies",
    )
    if render_load_errors:
        return [], [], [], render_load_errors

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
        return [], [], [], cosmetic_load_errors

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
        return [], [], [], policy_load_errors

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
    return render_proxy_rows, cosmetic_rows, cosmetic_policy_rows, errors


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
) -> Tuple[List[dict], List[dict], List[dict]]:
    errors: List[dict] = []
    _retention_record, retention_rows_raw, retention_load_errors = _load_registry_record(
        repo_root=repo_root,
        registry_rel_path="data/registries/retention_policy_registry.json",
        expected_schema_id="dominium.registry.retention_policy_registry",
        expected_schema_version="1.0.0",
        expected_entry_key="policies",
    )
    if retention_load_errors:
        return [], [], retention_load_errors

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
        retention_rows.append(
            {
                "retention_policy_id": retention_policy_id,
                "memory_allowed": bool(entry.get("memory_allowed", False)),
                "max_memory_items": int(entry.get("max_memory_items", 0) or 0),
                "decay_model_id": entry.get("decay_model_id"),
                "deterministic_eviction_rule_id": str(entry.get("deterministic_eviction_rule_id", "")).strip(),
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
        return [], [], policy_load_errors

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
    return policy_rows, retention_rows, errors


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
            return {
                "result": "complete",
                "bundle_id": bundle_id,
                "cache_key": key,
                "cache_hit": True,
                "out_dir": _norm(os.path.relpath(out_dir, repo_root)),
                "lockfile_path": _norm(os.path.relpath(lockfile_out, repo_root)),
                "ordered_pack_ids": [str(row.get("pack_id", "")) for row in ordered_packs],
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
    body_shape_rows, body_shape_registry_errors = _body_shape_registry_rows(
        repo_root=repo_root,
    )
    view_mode_rows, view_mode_registry_errors = _view_mode_registry_rows(
        repo_root=repo_root,
    )
    (
        render_proxy_rows,
        cosmetic_rows,
        cosmetic_policy_rows,
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
    all_errors = (
        domain_errors
        + law_errors
        + experience_errors
        + lens_errors
        + policy_errors
        + worldgen_constraints_errors
        + control_registry_errors
        + body_shape_registry_errors
        + view_mode_registry_errors
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
    controller_type_payload = _finalize_registry_payload(
        {
            "format_version": REGISTRY_FORMAT_VERSION,
            "generated_from": generated_from,
            "controller_types": controller_type_rows,
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
        "domain_registry": ("domain_registry", domain_payload),
        "law_registry": ("law_registry", law_payload),
        "experience_registry": ("experience_registry", experience_payload),
        "lens_registry": ("lens_registry", lens_payload),
        "control_action_registry": ("control_action_registry", control_action_payload),
        "controller_type_registry": ("controller_type_registry", controller_type_payload),
        "body_shape_registry": ("body_shape_registry", body_shape_payload),
        "view_mode_registry": ("view_mode_registry", view_mode_payload),
        "render_proxy_registry": ("render_proxy_registry", render_proxy_payload),
        "cosmetic_registry": ("cosmetic_registry", cosmetic_payload),
        "cosmetic_policy_registry": ("cosmetic_policy_registry", cosmetic_policy_payload),
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
        "domain_registry",
        "law_registry",
        "experience_registry",
        "lens_registry",
        "control_action_registry",
        "controller_type_registry",
        "body_shape_registry",
        "view_mode_registry",
        "render_proxy_registry",
        "cosmetic_registry",
        "cosmetic_policy_registry",
        "net_replication_policy_registry",
        "net_resync_strategy_registry",
        "net_server_policy_registry",
        "securex_policy_registry",
        "server_profile_registry",
        "shard_map_registry",
        "perception_interest_policy_registry",
        "epistemic_policy_registry",
        "retention_policy_registry",
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
            "domain_registry_hash": registry_hashes["domain_registry_hash"],
            "law_registry_hash": registry_hashes["law_registry_hash"],
            "experience_registry_hash": registry_hashes["experience_registry_hash"],
            "lens_registry_hash": registry_hashes["lens_registry_hash"],
            "control_action_registry_hash": registry_hashes["control_action_registry_hash"],
            "controller_type_registry_hash": registry_hashes["controller_type_registry_hash"],
            "body_shape_registry_hash": registry_hashes["body_shape_registry_hash"],
            "view_mode_registry_hash": registry_hashes["view_mode_registry_hash"],
            "render_proxy_registry_hash": registry_hashes["render_proxy_registry_hash"],
            "cosmetic_registry_hash": registry_hashes["cosmetic_registry_hash"],
            "cosmetic_policy_registry_hash": registry_hashes["cosmetic_policy_registry_hash"],
            "net_replication_policy_registry_hash": registry_hashes["net_replication_policy_registry_hash"],
            "net_resync_strategy_registry_hash": registry_hashes["net_resync_strategy_registry_hash"],
            "net_server_policy_registry_hash": registry_hashes["net_server_policy_registry_hash"],
            "securex_policy_registry_hash": registry_hashes["securex_policy_registry_hash"],
            "server_profile_registry_hash": registry_hashes["server_profile_registry_hash"],
            "shard_map_registry_hash": registry_hashes["shard_map_registry_hash"],
            "perception_interest_policy_registry_hash": registry_hashes["perception_interest_policy_registry_hash"],
            "epistemic_policy_registry_hash": registry_hashes["epistemic_policy_registry_hash"],
            "retention_policy_registry_hash": registry_hashes["retention_policy_registry_hash"],
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
