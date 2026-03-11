"""Deterministic offline pack verification pipeline for Setup/Launcher."""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from src.compat.data_format_loader import stamp_artifact_metadata
from src.lib.provides import (
    REFUSAL_PROVIDES_AMBIGUOUS,
    REFUSAL_PROVIDES_MISSING_PROVIDER,
    infer_resolution_policy_id,
    normalize_provides_declarations,
    normalize_provides_resolutions,
    resolve_providers,
)
from src.compat.descriptor.descriptor_engine import build_product_descriptor
from src.geo import build_overlay_manifest, merge_overlay_view
from src.modding import DEFAULT_MOD_POLICY_ID, evaluate_mod_policy
from tools.compatx.core.semantic_contract_validator import (
    CONTRACT_FIELD_ORDER,
    build_default_universe_contract_bundle,
    bundle_hash,
    load_semantic_contract_registry,
    validate_universe_contract_bundle,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.pack_contrib.parser import parse_contributions
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.registry_compile.bundle_profile import resolve_bundle_selection
from tools.xstack.registry_compile.lockfile import compute_pack_lock_hash


PACK_COMPATIBILITY_REPORT_SCHEMA_NAME = "pack_compatibility_report"
PACK_LOCK_SCHEMA_NAME = "pack_lock"

REFUSAL_PACK_SCHEMA_INVALID = "refusal.pack.schema_invalid"
REFUSAL_PACK_CONTRACT_RANGE_MISMATCH = "refusal.pack.contract_range_mismatch"
REFUSAL_PACK_REGISTRY_MISSING = "refusal.pack.registry_missing"
REFUSAL_PACK_TRUST_DENIED = "refusal.pack.trust_denied"
REFUSAL_PACK_CONFLICT_IN_STRICT = "refusal.pack.conflict_in_strict"
REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH = "refusal.pack.protocol_range_mismatch"
REFUSAL_PACK_ENGINE_VERSION_MISMATCH = "refusal.pack.engine_version_mismatch"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _error(code: str, path: str, message: str, **extra) -> dict:
    row = {
        "code": str(code),
        "path": str(path),
        "message": str(message),
    }
    for key, value in sorted(extra.items(), key=lambda item: str(item[0])):
        row[str(key)] = value
    return row


def _normalized_refusal_code(code: object) -> str:
    token = str(code or "").strip()
    if token in {"refusal.pack.contract_mismatch"}:
        return REFUSAL_PACK_CONTRACT_RANGE_MISMATCH
    if token in {"refusal.pack.missing_registry"}:
        return REFUSAL_PACK_REGISTRY_MISSING
    if token in {
        "refuse.pack.manifest_invalid",
        "refuse.pack.manifest_parse_failed",
        "refusal.pack.compat_manifest_invalid",
    }:
        return REFUSAL_PACK_SCHEMA_INVALID
    if token == "refusal.mod.trust_denied":
        return REFUSAL_PACK_TRUST_DENIED
    if token == "refusal.overlay.conflict":
        return REFUSAL_PACK_CONFLICT_IN_STRICT
    return token


def _normalize_error_rows(rows: Sequence[Mapping[str, object]]) -> List[dict]:
    out: List[dict] = []
    for row in rows:
        row_map = _as_map(row)
        if not row_map:
            continue
        normalized = dict(row_map)
        normalized["code"] = _normalized_refusal_code(row_map.get("code", ""))
        out.append(normalized)
    return sorted(
        out,
        key=lambda item: (
            str(item.get("code", "")),
            str(item.get("path", "")),
            str(item.get("message", "")),
        ),
    )


def _version_tuple(token: str) -> Tuple[int, ...]:
    text = str(token or "").strip()
    if not text:
        return ()
    text = text.split("+", 1)[0]
    text = text.rsplit(".v", 1)[-1] if ".v" in text else text
    out: List[int] = []
    for part in text.replace("-", ".").split("."):
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            return ()
    return tuple(out)


def _token_satisfies_range(actual_token: str, range_row: Mapping[str, object]) -> bool:
    actual = str(actual_token or "").strip()
    row = _as_map(range_row)
    exact = str(row.get("exact_version", "")).strip()
    min_version = str(row.get("min_version", "")).strip()
    max_version = str(row.get("max_version", "")).strip()
    if exact:
        return actual == exact
    actual_tuple = _version_tuple(actual)
    min_tuple = _version_tuple(min_version)
    max_tuple = _version_tuple(max_version)
    if min_version and not min_tuple:
        return actual == min_version
    if max_version and not max_tuple:
        return actual == max_version
    if min_tuple and actual_tuple and actual_tuple < min_tuple:
        return False
    if max_tuple and actual_tuple and actual_tuple > max_tuple:
        return False
    if min_version and not actual_tuple:
        return actual == min_version
    if max_version and not actual_tuple:
        return actual == max_version
    return True


def _current_engine_semver(root: str) -> str:
    try:
        descriptor = build_product_descriptor(root, product_id="engine")
    except Exception:
        return "0.0.0"
    version = str(descriptor.get("product_version", "")).strip()
    return version.split("+", 1)[0] if version else "0.0.0"


def _engine_protocol_rows(root: str) -> Dict[str, List[str]]:
    try:
        descriptor = build_product_descriptor(root, product_id="engine")
    except Exception:
        return {}
    out: Dict[str, List[str]] = {}
    for row in _as_list(descriptor.get("protocol_versions_supported")):
        row_map = _as_map(row)
        protocol_id = str(row_map.get("protocol_id", "")).strip()
        if not protocol_id:
            continue
        versions = []
        for key in ("min_version", "max_version", "version"):
            token = str(row_map.get(key, "")).strip()
            if token:
                versions.append(token)
        out[protocol_id] = sorted(set(versions))
    return dict((key, out[key]) for key in sorted(out.keys()))


def _contract_rows_for_bundle(bundle_payload: Mapping[str, object]) -> Dict[str, str]:
    row = dict(bundle_payload or {})
    out: Dict[str, str] = {}
    for field_name, contract_id in CONTRACT_FIELD_ORDER:
        out[str(contract_id)] = str(row.get(field_name, "")).strip()
    return dict((key, out[key]) for key in sorted(out.keys()))


def _select_bundle(
    *,
    root: str,
    packs: Sequence[Mapping[str, object]],
    bundle_id: str,
    schema_root: str,
    bundles_root_rel: str,
) -> dict:
    token = str(bundle_id or "").strip()
    if not token:
        selected = sorted(str(row.get("pack_id", "")).strip() for row in packs if str(row.get("pack_id", "")).strip())
        return {
            "result": "complete",
            "bundle_id": "",
            "selected_pack_ids": selected,
            "selection_strategy": "all_packs_sorted",
            "optional_missing_pack_ids": [],
        }
    return resolve_bundle_selection(
        bundle_id=token,
        packs=list(packs),
        repo_root=root,
        schema_repo_root=schema_root,
    )


def _overlay_rows_from_contributions(contributions: Sequence[Mapping[str, object]]) -> Tuple[List[dict], List[dict], List[dict]]:
    layers: List[dict] = []
    patches: List[dict] = []
    warnings: List[dict] = []
    for row in contributions:
        row_map = _as_map(row)
        if str(row_map.get("contrib_type", "")).strip() != "registry_entries":
            continue
        payload = row_map.get("payload")
        payload_map = _as_map(payload)
        if payload_map.get("layer_id") and payload_map.get("layer_kind"):
            layers.append(dict(payload_map))
            continue
        patch_rows = []
        if isinstance(payload, list):
            patch_rows = list(payload)
        elif isinstance(payload_map.get("property_patches"), list):
            patch_rows = list(payload_map.get("property_patches") or [])
        if patch_rows:
            for patch in patch_rows:
                if isinstance(patch, Mapping):
                    patches.append(dict(patch))
            continue
        warnings.append(
            _error(
                "warn.pack.compat.overlay_payload_ignored",
                "$.contributions",
                "registry_entries payload was not recognized as overlay layer or property patch set",
                contribution_id=str(row_map.get("id", "")).strip(),
            )
        )
    return layers, patches, sorted(warnings, key=lambda item: (item["code"], item["path"], item["message"], str(item.get("contribution_id", ""))))


def _ordered_pack_rows(rows: Sequence[Mapping[str, object]]) -> List[dict]:
    out = []
    for row in rows:
        row_map = dict(row)
        manifest = dict(row_map.get("manifest") or {})
        out.append(
            {
                "pack_id": str(row_map.get("pack_id", "")).strip(),
                "pack_version": str(row_map.get("version", "")).strip(),
                "trust_level_id": str(row_map.get("trust_level_id", "")).strip(),
                "capability_ids": _sorted_tokens(row_map.get("capability_ids")),
                "canonical_hash": str(manifest.get("canonical_hash", row_map.get("canonical_hash", ""))).strip(),
                "compat_manifest_hash": str(row_map.get("compat_manifest_hash", "")).strip(),
                "trust_descriptor_hash": str(row_map.get("trust_descriptor_hash", "")).strip(),
                "capabilities_hash": str(row_map.get("capabilities_hash", "")).strip(),
                "signature_status": str(row_map.get("signature_status", "")).strip(),
                "degrade_mode_id": str(row_map.get("pack_degrade_mode_id", "")).strip(),
                "compat_manifest_path": str(row_map.get("compat_manifest_path", "")).strip(),
                "manifest_rel": str(row_map.get("manifest_rel", "")).strip(),
            }
        )
    return sorted(out, key=lambda item: (item["pack_id"], item["pack_version"]))


def build_verified_pack_lock(
    *,
    repo_root: str,
    bundle_id: str,
    instance_id: str = "",
    ordered_pack_list: Sequence[Mapping[str, object]],
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    engine_contract_bundle_hash: str,
    semantic_contract_registry_hash: str,
    resolution_policy_id: str = "",
    required_provides_ids: Sequence[str] | None = None,
    provides_declarations: Sequence[Mapping[str, object]] | None = None,
    provides_resolutions: Sequence[Mapping[str, object]] | None = None,
    provider_capability_ids: Sequence[str] | None = None,
) -> dict:
    ordered_rows = _ordered_pack_rows(ordered_pack_list)
    resolved_rows = [
        {
            "pack_id": row["pack_id"],
            "version": row["pack_version"],
            "canonical_hash": row["canonical_hash"],
            "signature_status": row["signature_status"],
            "trust_level_id": row["trust_level_id"],
            "capability_ids": list(row["capability_ids"]),
            "trust_descriptor_hash": row["trust_descriptor_hash"],
            "capabilities_hash": row["capabilities_hash"],
            "compat_manifest_hash": row["compat_manifest_hash"],
            "pack_degrade_mode_id": row["degrade_mode_id"],
        }
        for row in ordered_rows
    ]
    pack_lock_hash = compute_pack_lock_hash(resolved_rows)
    payload = {
        "schema_version": "1.0.0",
        "pack_lock_id": "pack_lock.verified.{}".format(str(bundle_id or "all_packs").strip() or "all_packs"),
        "ordered_pack_ids": [row["pack_id"] for row in ordered_rows],
        "ordered_pack_versions": [row["pack_version"] for row in ordered_rows],
        "pack_hashes": {row["pack_id"]: row["canonical_hash"] for row in ordered_rows},
        "pack_compat_hashes": {row["pack_id"]: row["compat_manifest_hash"] for row in ordered_rows},
        "mod_policy_id": str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
        "overlay_conflict_policy_id": str(overlay_conflict_policy_id).strip(),
        "resolution_policy_id": str(resolution_policy_id).strip(),
        "required_provides_ids": sorted({str(item).strip() for item in list(required_provides_ids or []) if str(item).strip()}),
        "provides_declarations": normalize_provides_declarations(list(provides_declarations or [])),
        "provides_resolutions": normalize_provides_resolutions(
            list(provides_resolutions or []),
            instance_id=str(instance_id or bundle_id or "").strip(),
            resolution_policy_id=str(resolution_policy_id).strip(),
        ),
        "provider_capability_ids": sorted({str(item).strip() for item in list(provider_capability_ids or []) if str(item).strip()}),
        "engine_contract_bundle_hash": str(engine_contract_bundle_hash).strip(),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash).strip(),
        "ordered_packs": resolved_rows,
        "source_pack_lock_hash": pack_lock_hash,
        "pack_lock_hash": pack_lock_hash,
        "deterministic_fingerprint": "",
        "extensions": {
            "bundle_id": str(bundle_id or "").strip(),
            "pack_count": len(ordered_rows),
            "source": "PACK-COMPAT-1",
        },
    }
    payload = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="pack_lock",
        payload=payload,
        update_fingerprint=False,
    )
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def _report_payload(
    *,
    engine_contract_bundle_hash: str,
    mod_policy_id: str,
    pack_list: Sequence[Mapping[str, object]],
    valid: bool,
    conflicts: Sequence[Mapping[str, object]],
    refused_packs: Sequence[Mapping[str, object]],
    refusal_codes: Sequence[object],
    warnings: Sequence[Mapping[str, object]],
    pack_lock_hash: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "report_id": "pack_compatibility_report.{}".format(
            canonical_sha256(
                {
                    "engine_contract_bundle_hash": str(engine_contract_bundle_hash).strip(),
                    "mod_policy_id": str(mod_policy_id).strip(),
                    "pack_ids": [
                        "{}@{}".format(str(row.get("pack_id", "")).strip(), str(row.get("pack_version", "")).strip())
                        for row in pack_list
                    ],
                }
            )[:16]
        ),
        "engine_contract_bundle_hash": str(engine_contract_bundle_hash).strip(),
        "mod_policy_id": str(mod_policy_id).strip(),
        "pack_list": [dict(row) for row in pack_list],
        "valid": bool(valid),
        "conflicts": [dict(row) for row in conflicts],
        "refused_packs": [dict(row) for row in refused_packs],
        "refusal_codes": _sorted_tokens(refusal_codes),
        "warnings": [dict(row) for row in warnings],
        "pack_lock_hash": str(pack_lock_hash).strip(),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def verify_pack_set(
    *,
    repo_root: str,
    bundle_id: str = "",
    mod_policy_id: str = DEFAULT_MOD_POLICY_ID,
    overlay_conflict_policy_id: str = "",
    instance_id: str = "",
    explicit_provides_resolutions: Sequence[Mapping[str, object]] | None = None,
    resolution_policy_id: str = "",
    schema_repo_root: str = "",
    packs_root_rel: str = "packs",
    bundles_root_rel: str = "bundles",
    universe_contract_bundle: Mapping[str, object] | None = None,
    universe_contract_bundle_path: str = "",
) -> dict:
    root = os.path.abspath(str(repo_root))
    schema_root = os.path.abspath(str(schema_repo_root or root))
    warnings: List[dict] = []
    errors: List[dict] = []

    contract_registry, contract_registry_error = load_semantic_contract_registry(root)
    if contract_registry_error:
        return {"result": "refused", "errors": [_error(REFUSAL_PACK_CONTRACT_RANGE_MISMATCH, "$.semantic_contract_registry", "semantic contract registry is missing or invalid")]}

    if str(universe_contract_bundle_path or "").strip():
        bundle_payload, bundle_error = _read_json(os.path.join(root, str(universe_contract_bundle_path).replace("/", os.sep)))
        if bundle_error:
            return {"result": "refused", "errors": [_error(REFUSAL_PACK_CONTRACT_RANGE_MISMATCH, "$.universe_contract_bundle", "universe contract bundle is missing or invalid")]}
    elif universe_contract_bundle:
        bundle_payload = dict(universe_contract_bundle)
    else:
        bundle_payload = build_default_universe_contract_bundle(contract_registry)
    bundle_errors = validate_universe_contract_bundle(schema_root, bundle_payload, contract_registry)
    if bundle_errors:
        return {"result": "refused", "errors": [_error(REFUSAL_PACK_CONTRACT_RANGE_MISMATCH, "$.universe_contract_bundle", "universe contract bundle failed validation", bundle_errors=sorted(bundle_errors))]}

    engine_contract_bundle_hash = bundle_hash(bundle_payload)
    semantic_contract_registry_hash = str(_as_map(bundle_payload.get("extensions")).get("semantic_contract_registry_hash", "")).strip()
    contract_rows = _contract_rows_for_bundle(bundle_payload)

    loaded = load_pack_set(
        repo_root=root,
        packs_root_rel=str(packs_root_rel or "packs").strip() or "packs",
        schema_repo_root=schema_root,
        mod_policy_id=str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
    )
    if str(loaded.get("result", "")) != "complete":
        normalized_errors = _normalize_error_rows(list(loaded.get("errors") or []))
        report = _report_payload(
            engine_contract_bundle_hash=engine_contract_bundle_hash,
            mod_policy_id=str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
            pack_list=[],
            valid=False,
            conflicts=[],
            refused_packs=[],
            refusal_codes=[str(row.get("code", "")).strip() for row in normalized_errors],
            warnings=[],
            pack_lock_hash="",
            extensions={"semantic_contract_registry_hash": semantic_contract_registry_hash, "bundle_id": str(bundle_id or "").strip(), "source": "PACK-COMPAT-1"},
        )
        return {"result": "complete", "report": report, "pack_lock": {}, "errors": normalized_errors, "warnings": []}

    packs = list(loaded.get("packs") or [])
    warnings.extend(list(loaded.get("warnings") or []))
    bundle_selection = _select_bundle(
        root=root,
        packs=packs,
        bundle_id=bundle_id,
        schema_root=schema_root,
        bundles_root_rel=str(bundles_root_rel or "bundles").strip() or "bundles",
    )
    if str(bundle_selection.get("result", "")) != "complete":
        normalized_errors = _normalize_error_rows(list(bundle_selection.get("errors") or []))
        report = _report_payload(
            engine_contract_bundle_hash=engine_contract_bundle_hash,
            mod_policy_id=str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
            pack_list=_ordered_pack_rows(packs),
            valid=False,
            conflicts=[],
            refused_packs=[],
            refusal_codes=[str(row.get("code", "")).strip() for row in normalized_errors],
            warnings=warnings,
            pack_lock_hash="",
            extensions={"semantic_contract_registry_hash": semantic_contract_registry_hash, "bundle_id": str(bundle_id or "").strip(), "selection_strategy": "bundle_profile_v1", "source": "PACK-COMPAT-1"},
        )
        return {"result": "complete", "report": report, "pack_lock": {}, "errors": normalized_errors, "warnings": warnings}

    resolved = resolve_packs(packs, bundle_selection=list(bundle_selection.get("selected_pack_ids") or []))
    if str(resolved.get("result", "")) != "complete":
        normalized_errors = _normalize_error_rows(list(resolved.get("errors") or []))
        report = _report_payload(
            engine_contract_bundle_hash=engine_contract_bundle_hash,
            mod_policy_id=str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
            pack_list=_ordered_pack_rows(packs),
            valid=False,
            conflicts=[],
            refused_packs=[],
            refusal_codes=[str(row.get("code", "")).strip() for row in normalized_errors],
            warnings=warnings,
            pack_lock_hash="",
            extensions={"semantic_contract_registry_hash": semantic_contract_registry_hash, "bundle_id": str(bundle_id or "").strip(), "selection_strategy": str(bundle_selection.get("selection_strategy", "")), "source": "PACK-COMPAT-1"},
        )
        return {"result": "complete", "report": report, "pack_lock": {}, "errors": normalized_errors, "warnings": warnings}

    ordered_packs = list(resolved.get("ordered_pack_list") or [])
    contributions_result = parse_contributions(repo_root=root, packs=ordered_packs)
    contributions = list(contributions_result.get("contributions") or []) if str(contributions_result.get("result", "")) == "complete" else []
    if str(contributions_result.get("result", "")) != "complete":
        errors.extend(list(contributions_result.get("errors") or []))

    mod_eval = evaluate_mod_policy(
        repo_root=root,
        ordered_packs=ordered_packs,
        contributions=contributions,
        mod_policy_id=str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID,
        schema_repo_root=schema_root,
    )
    if str(mod_eval.get("result", "")) != "complete":
        errors.extend(list(mod_eval.get("errors") or []))
    effective_mod_policy_id = str(mod_eval.get("mod_policy_id", "")).strip() or str(mod_policy_id).strip() or DEFAULT_MOD_POLICY_ID
    effective_conflict_policy_id = str(overlay_conflict_policy_id or mod_eval.get("overlay_conflict_policy_id", "")).strip()
    effective_resolution_policy_id = infer_resolution_policy_id(
        mod_policy_id=effective_mod_policy_id,
        overlay_conflict_policy_id=effective_conflict_policy_id,
        preferred_policy_id=str(resolution_policy_id or "").strip(),
    )

    engine_semver = _current_engine_semver(root)
    engine_protocols = _engine_protocol_rows(root)
    refused_packs: List[dict] = []
    refusal_codes: List[str] = []
    for pack_row in sorted(ordered_packs, key=lambda item: (str(item.get("pack_id", "")), str(item.get("version", "")))):
        compat_manifest = dict(pack_row.get("compat_manifest") or {})
        if not compat_manifest:
            continue
        pack_id = str(pack_row.get("pack_id", "")).strip()
        compat_errors: List[dict] = []
        for contract_id, range_row in sorted(_as_map(compat_manifest.get("required_contract_ranges")).items(), key=lambda item: str(item[0])):
            actual_token = str(contract_rows.get(str(contract_id), "")).strip()
            if not actual_token or not _token_satisfies_range(actual_token, _as_map(range_row)):
                compat_errors.append(_error(REFUSAL_PACK_CONTRACT_RANGE_MISMATCH, "$.required_contract_ranges.{}".format(contract_id), "pack '{}' requires unsupported contract range for '{}'".format(pack_id, contract_id)))
        for protocol_id, range_row in sorted(_as_map(compat_manifest.get("required_protocol_ranges")).items(), key=lambda item: str(item[0])):
            supported_tokens = list(engine_protocols.get(str(protocol_id), []))
            if not supported_tokens or not any(_token_satisfies_range(token, _as_map(range_row)) for token in supported_tokens):
                compat_errors.append(_error(REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH, "$.required_protocol_ranges.{}".format(protocol_id), "pack '{}' requires unsupported protocol range for '{}'".format(pack_id, protocol_id)))
        engine_range = _as_map(compat_manifest.get("supported_engine_version_range"))
        if engine_range and not _token_satisfies_range(engine_semver, engine_range):
            compat_errors.append(_error(REFUSAL_PACK_ENGINE_VERSION_MISMATCH, "$.supported_engine_version_range", "pack '{}' does not support engine version '{}'".format(pack_id, engine_semver)))
        if compat_errors:
            refusal_codes.extend(str(row.get("code", "")).strip() for row in compat_errors)
            refused_packs.append({"pack_id": pack_id, "pack_version": str(pack_row.get("version", "")).strip(), "errors": compat_errors})

    required_provides_ids: List[str] = []
    provides_declarations: List[dict] = []
    for pack_row in sorted(ordered_packs, key=lambda item: (str(item.get("pack_id", "")), str(item.get("version", "")))):
        compat_manifest = dict(pack_row.get("compat_manifest") or {})
        required_provides_ids.extend(
            str(item).strip()
            for item in list(compat_manifest.get("required_provides_ids") or [])
            if str(item).strip()
        )
        provides_declarations.extend(list(compat_manifest.get("provides_declarations") or []))
    provider_resolution = resolve_providers(
        instance_id=str(instance_id or bundle_id or "pack.verify").strip() or "pack.verify",
        required_provides_ids=required_provides_ids,
        provider_declarations=provides_declarations,
        explicit_resolutions=explicit_provides_resolutions,
        resolution_policy_id=effective_resolution_policy_id,
        mod_policy_id=effective_mod_policy_id,
        overlay_conflict_policy_id=effective_conflict_policy_id,
    )
    if provider_resolution.get("result") != "complete":
        provider_errors = [
            _error(
                str(row.get("code", REFUSAL_PROVIDES_MISSING_PROVIDER)).strip(),
                "$.required_provides_ids",
                str(row.get("message", "")).strip() or "provider resolution failed",
            )
            for row in list(provider_resolution.get("errors") or [])
            if isinstance(row, Mapping)
        ]
        errors.extend(provider_errors)
        refusal_codes.extend(str(row.get("code", "")).strip() for row in provider_errors)

    layers, property_patches, overlay_warnings = _overlay_rows_from_contributions(contributions)
    warnings.extend(overlay_warnings)
    conflicts: List[dict] = []
    if layers or property_patches:
        resolved_pack_rows = [{"pack_id": str(row.get("pack_id", "")).strip(), "canonical_hash": str((dict(row.get("manifest") or {})).get("canonical_hash", "")).strip(), "signature_status": str(row.get("signature_status", "")).strip()} for row in ordered_packs]
        overlay_manifest = build_overlay_manifest(
            universe_id="universe.pack.compat.verify",
            layers=layers,
            pack_lock_hash=compute_pack_lock_hash([{"pack_id": str(row.get("pack_id", "")).strip(), "version": str(row.get("version", "")).strip(), "canonical_hash": str((dict(row.get("manifest") or {})).get("canonical_hash", "")).strip(), "signature_status": str(row.get("signature_status", "")).strip(), "trust_level_id": str(row.get("trust_level_id", "")).strip(), "capability_ids": _sorted_tokens(row.get("capability_ids")), "trust_descriptor_hash": str(row.get("trust_descriptor_hash", "")).strip(), "capabilities_hash": str(row.get("capabilities_hash", "")).strip(), "compat_manifest_hash": str(row.get("compat_manifest_hash", "")).strip(), "pack_degrade_mode_id": str(row.get("pack_degrade_mode_id", "")).strip()} for row in ordered_packs]),
            extensions={"overlay_conflict_policy_id": effective_conflict_policy_id, "source": "PACK-COMPAT-1"},
        )
        merge_result = merge_overlay_view(base_objects=[], overlay_manifest=overlay_manifest, property_patches=property_patches, resolved_packs=resolved_pack_rows, expected_pack_lock_hash=str(overlay_manifest.get("pack_lock_hash", "")).strip(), overlay_conflict_policy_id=effective_conflict_policy_id)
        conflicts = list(merge_result.get("overlay_conflict_artifacts") or [])
        if str(merge_result.get("result", "")) == "refused":
            refusal_codes.append(REFUSAL_PACK_CONFLICT_IN_STRICT)
            errors.append(
                _error(
                    REFUSAL_PACK_CONFLICT_IN_STRICT,
                    "$.overlay_conflicts",
                    "overlay dry-run conflict refused under strict conflict policy",
                    underlying_refusal_code=str(merge_result.get("refusal_code", "")).strip(),
                )
            )

    pack_list = _ordered_pack_rows(ordered_packs)
    pack_lock = build_verified_pack_lock(
        repo_root=root,
        bundle_id=str(bundle_selection.get("bundle_id", "")),
        instance_id=str(instance_id or "").strip(),
        ordered_pack_list=ordered_packs,
        mod_policy_id=effective_mod_policy_id,
        overlay_conflict_policy_id=effective_conflict_policy_id,
        engine_contract_bundle_hash=engine_contract_bundle_hash,
        semantic_contract_registry_hash=semantic_contract_registry_hash,
        resolution_policy_id=effective_resolution_policy_id,
        required_provides_ids=required_provides_ids,
        provides_declarations=provides_declarations,
        provides_resolutions=list(provider_resolution.get("provides_resolutions") or []),
        provider_capability_ids=list(provider_resolution.get("implied_capabilities") or []),
    )
    valid = not errors and not refused_packs
    report = _report_payload(
        engine_contract_bundle_hash=engine_contract_bundle_hash,
        mod_policy_id=effective_mod_policy_id,
        pack_list=pack_list,
        valid=valid,
        conflicts=conflicts,
        refused_packs=refused_packs,
        refusal_codes=refusal_codes + [str(row.get("code", "")).strip() for row in errors if isinstance(row, Mapping)],
        warnings=warnings,
        pack_lock_hash=str(pack_lock.get("pack_lock_hash", "")).strip(),
        extensions={
            "semantic_contract_registry_hash": semantic_contract_registry_hash,
            "bundle_id": str(bundle_selection.get("bundle_id", "")).strip(),
            "bundle_selection_strategy": str(bundle_selection.get("selection_strategy", "")).strip(),
            "overlay_conflict_policy_id": effective_conflict_policy_id,
            "optional_missing_pack_ids": list(bundle_selection.get("optional_missing_pack_ids") or []),
            "resolution_policy_id": effective_resolution_policy_id,
            "required_provides_ids": sorted({str(item).strip() for item in required_provides_ids if str(item).strip()}),
            "provides_resolutions": list(provider_resolution.get("provides_resolutions") or []),
            "provider_capability_ids": list(provider_resolution.get("implied_capabilities") or []),
            "provider_selection_logged": bool(provider_resolution.get("selection_logged", False)),
            "auto_selected_provides_ids": list(provider_resolution.get("auto_selected_provides_ids") or []),
            "source": "PACK-COMPAT-1",
        },
    )

    report_schema = validate_instance(repo_root=schema_root, schema_name=PACK_COMPATIBILITY_REPORT_SCHEMA_NAME, payload=report, strict_top_level=True)
    lock_schema = validate_instance(repo_root=schema_root, schema_name=PACK_LOCK_SCHEMA_NAME, payload=pack_lock, strict_top_level=True)
    if not bool(report_schema.get("valid", False)) or not bool(lock_schema.get("valid", False)):
        schema_errors = list(report_schema.get("errors") or []) + list(lock_schema.get("errors") or [])
        return {"result": "refused", "errors": schema_errors}

    normalized_errors = _normalize_error_rows([dict(row) for row in errors if isinstance(row, Mapping)])
    return {
        "result": "complete",
        "report": report,
        "pack_lock": pack_lock if valid else {},
        "errors": normalized_errors,
        "warnings": sorted([dict(row) for row in warnings if isinstance(row, Mapping)], key=lambda item: (str(item.get("code", "")), str(item.get("path", "")), str(item.get("message", "")))),
    }


def write_pack_compatibility_outputs(
    *,
    report_path: str,
    report_payload: Mapping[str, object],
    pack_lock_path: str = "",
    pack_lock_payload: Mapping[str, object] | None = None,
) -> dict:
    report_abs = os.path.abspath(str(report_path))
    os.makedirs(os.path.dirname(report_abs), exist_ok=True)
    with open(report_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(report_payload or {})))
        handle.write("\n")
    lock_abs = ""
    if str(pack_lock_path or "").strip() and pack_lock_payload:
        lock_abs = os.path.abspath(str(pack_lock_path))
        os.makedirs(os.path.dirname(lock_abs), exist_ok=True)
        with open(lock_abs, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json_text(dict(pack_lock_payload or {})))
            handle.write("\n")
    return {"result": "complete", "report_path": _norm(report_abs), "pack_lock_path": _norm(lock_abs)}


__all__ = [
    "PACK_COMPATIBILITY_REPORT_SCHEMA_NAME",
    "PACK_LOCK_SCHEMA_NAME",
    "REFUSAL_PACK_CONFLICT_IN_STRICT",
    "REFUSAL_PACK_CONTRACT_RANGE_MISMATCH",
    "REFUSAL_PACK_ENGINE_VERSION_MISMATCH",
    "REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH",
    "REFUSAL_PACK_REGISTRY_MISSING",
    "REFUSAL_PACK_SCHEMA_INVALID",
    "REFUSAL_PACK_TRUST_DENIED",
    "build_verified_pack_lock",
    "verify_pack_set",
    "write_pack_compatibility_outputs",
]
