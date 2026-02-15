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
        rows.append(
            {
                "law_profile_id": law_id,
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
    astronomy_rows, reference_frame_rows, site_rows, astronomy_errors = _astronomy_rows(
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
        + astronomy_errors
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
        "activation_policy_registry": ("activation_policy_registry", activation_policy_payload),
        "budget_policy_registry": ("budget_policy_registry", budget_policy_payload),
        "fidelity_policy_registry": ("fidelity_policy_registry", fidelity_policy_payload),
        "astronomy_catalog_index": ("astronomy_catalog_index", astronomy_payload),
        "site_registry_index": ("site_registry_index", site_payload),
        "ui_registry": ("ui_registry", ui_payload),
    }
    registry_hashes = {}
    output_files = []
    for registry_key in (
        "domain_registry",
        "law_registry",
        "experience_registry",
        "lens_registry",
        "activation_policy_registry",
        "budget_policy_registry",
        "fidelity_policy_registry",
        "astronomy_catalog_index",
        "site_registry_index",
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
            "activation_policy_registry_hash": registry_hashes["activation_policy_registry_hash"],
            "budget_policy_registry_hash": registry_hashes["budget_policy_registry_hash"],
            "fidelity_policy_registry_hash": registry_hashes["fidelity_policy_registry_hash"],
            "astronomy_catalog_index_hash": registry_hashes["astronomy_catalog_index_hash"],
            "site_registry_index_hash": registry_hashes["site_registry_index_hash"],
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
