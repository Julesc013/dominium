"""Deterministic shareable artifact manifest normalization and load-policy helpers."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Mapping, Sequence, Tuple

from lib.install import compare_required_contract_ranges, normalize_contract_range
from meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256


CURRENT_ARTIFACT_FORMAT_VERSION = "1.0.0"

ARTIFACT_KIND_PROFILE_BUNDLE = "artifact.profile_bundle"
ARTIFACT_KIND_BLUEPRINT = "artifact.blueprint"
ARTIFACT_KIND_SYSTEM_TEMPLATE = "artifact.system_template"
ARTIFACT_KIND_PROCESS_DEFINITION = "artifact.process_definition"
ARTIFACT_KIND_LOGIC_PROGRAM = "artifact.logic_program"
ARTIFACT_KIND_VIEW_PRESET = "artifact.view_preset"
ARTIFACT_KIND_RESOURCE_PACK_STUB = "artifact.resource_pack_stub"

ARTIFACT_KIND_VALUES = (
    ARTIFACT_KIND_PROFILE_BUNDLE,
    ARTIFACT_KIND_BLUEPRINT,
    ARTIFACT_KIND_SYSTEM_TEMPLATE,
    ARTIFACT_KIND_PROCESS_DEFINITION,
    ARTIFACT_KIND_LOGIC_PROGRAM,
    ARTIFACT_KIND_VIEW_PRESET,
    ARTIFACT_KIND_RESOURCE_PACK_STUB,
)

ARTIFACT_DEGRADE_STRICT_REFUSE = "artifact.degrade.strict_refuse"
ARTIFACT_DEGRADE_BEST_EFFORT = "artifact.degrade.best_effort"
ARTIFACT_DEGRADE_READ_ONLY_ONLY = "artifact.degrade.read_only_only"

ARTIFACT_DEGRADE_MODE_VALUES = (
    ARTIFACT_DEGRADE_STRICT_REFUSE,
    ARTIFACT_DEGRADE_BEST_EFFORT,
    ARTIFACT_DEGRADE_READ_ONLY_ONLY,
)

REFUSAL_ARTIFACT_HASH_MISMATCH = "refusal.artifact.hash_mismatch"
REFUSAL_ARTIFACT_MANIFEST_REQUIRED = "refusal.artifact.manifest_required"
REFUSAL_ARTIFACT_CONTRACT_RANGE_MISMATCH = "refusal.artifact.contract_range_mismatch"
REFUSAL_ARTIFACT_CAPABILITY_MISMATCH = "refusal.artifact.capability_mismatch"
REFUSAL_ARTIFACT_TOPOLOGY_MISMATCH = "refusal.artifact.topology_mismatch"
REFUSAL_ARTIFACT_PHYSICS_MISMATCH = "refusal.artifact.physics_mismatch"
REFUSAL_ARTIFACT_MIGRATION_REQUIRED = "refusal.artifact.migration_required"
REFUSAL_ARTIFACT_READ_ONLY_REQUIRED = "refusal.artifact.read_only_required"

KIND_TO_STORE_CATEGORY = {
    ARTIFACT_KIND_PROFILE_BUNDLE: "profiles",
    ARTIFACT_KIND_BLUEPRINT: "blueprints",
    ARTIFACT_KIND_SYSTEM_TEMPLATE: "system_templates",
    ARTIFACT_KIND_PROCESS_DEFINITION: "process_definitions",
    ARTIFACT_KIND_LOGIC_PROGRAM: "logic_programs",
    ARTIFACT_KIND_VIEW_PRESET: "view_presets",
    ARTIFACT_KIND_RESOURCE_PACK_STUB: "resource_pack_stubs",
}

STORE_CATEGORY_TO_KIND = dict((value, key) for key, value in KIND_TO_STORE_CATEGORY.items())

SCHEMA_KIND_HINTS = {
    "dominium.schema.profile.bundle": ARTIFACT_KIND_PROFILE_BUNDLE,
    "dominium.schema.materials.blueprint": ARTIFACT_KIND_BLUEPRINT,
    "dominium.schema.system.system_template": ARTIFACT_KIND_SYSTEM_TEMPLATE,
    "dominium.schema.process.process_definition": ARTIFACT_KIND_PROCESS_DEFINITION,
}

KIND_ID_FIELDS = {
    ARTIFACT_KIND_PROFILE_BUNDLE: ("artifact_id", "profile_bundle_id"),
    ARTIFACT_KIND_BLUEPRINT: ("artifact_id", "blueprint_id"),
    ARTIFACT_KIND_SYSTEM_TEMPLATE: ("artifact_id", "template_id", "system_template_id"),
    ARTIFACT_KIND_PROCESS_DEFINITION: ("artifact_id", "process_id"),
    ARTIFACT_KIND_LOGIC_PROGRAM: ("artifact_id", "logic_program_id"),
    ARTIFACT_KIND_VIEW_PRESET: ("artifact_id", "view_preset_id", "preset_id"),
    ARTIFACT_KIND_RESOURCE_PACK_STUB: ("artifact_id", "resource_pack_stub_id", "resource_pack_id"),
}

PATH_LIKE_KEYS = {
    "artifact_manifest_ref",
    "descriptor_ref",
    "manifest_ref",
    "path",
    "payload_path",
    "payload_ref",
    "root_path",
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: object) -> str:
    token = str(path or "").replace("\\", "/")
    if token.startswith("./"):
        token = token[2:]
    return token


def _normalize_value(value: object, key: str = "") -> object:
    if isinstance(value, Mapping):
        return {
            str(name): _normalize_value(item, str(name))
            for name, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    if isinstance(value, str):
        if key in PATH_LIKE_KEYS or key.endswith(("_path", "_ref", "_root")):
            return _norm(value)
        return value
    return value


def write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.abspath(str(path or "").strip())
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            _normalize_value(normalize_extensions_tree(dict(payload or {}))),
            handle,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        handle.write("\n")
    return target


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def stable_artifact_id(seed_payload: Mapping[str, object]) -> str:
    return "artifact.{}".format(
        canonical_sha256(_normalize_value(normalize_extensions_tree(dict(seed_payload or {}))))[:24]
    )


def _sorted_unique_strings(values: object) -> List[str]:
    return sorted({str(value).strip() for value in _as_list(values) if str(value).strip()})


def _normalize_contract_ranges(values: object) -> Dict[str, dict]:
    rows: Dict[str, dict] = {}
    for contract_id, row in sorted(_as_map(values).items(), key=lambda item: str(item[0])):
        token = str(contract_id or "").strip()
        if not token:
            continue
        item = normalize_contract_range(row)
        if not str(item.get("contract_category_id", "")).strip():
            item["contract_category_id"] = token
            item["deterministic_fingerprint"] = deterministic_fingerprint(item)
        rows[token] = item
    return dict((key, rows[key]) for key in sorted(rows.keys()))


def _normalize_migration_refs(values: object) -> List[str]:
    refs: List[str] = []
    for row in _as_list(values):
        if isinstance(row, Mapping):
            token = str(_as_map(row).get("migration_id", "")).strip() or str(_as_map(row).get("event_id", "")).strip()
        else:
            token = str(row or "").strip()
        if token:
            refs.append(token)
    return sorted(set(refs))


def artifact_kind_from_store_category(category: str) -> str:
    return STORE_CATEGORY_TO_KIND.get(str(category or "").strip().lower(), "")


def artifact_store_category(artifact_kind_id: str) -> str:
    return KIND_TO_STORE_CATEGORY.get(str(artifact_kind_id or "").strip(), "")


def infer_artifact_kind_id(payload: Mapping[str, object] | None, expected_kind_id: str = "") -> str:
    token = str(expected_kind_id or "").strip()
    if token:
        return token
    row = _as_map(payload)
    explicit = str(row.get("artifact_kind_id", "")).strip()
    if explicit:
        return explicit
    schema_id = str(row.get("schema_id", "")).strip()
    if schema_id in SCHEMA_KIND_HINTS:
        return SCHEMA_KIND_HINTS[schema_id]
    for kind_id, field_names in KIND_ID_FIELDS.items():
        if any(str(row.get(field_name, "")).strip() for field_name in field_names):
            return kind_id
    return ""


def infer_artifact_id(payload: Mapping[str, object] | None, artifact_kind_id: str = "") -> str:
    row = _as_map(payload)
    explicit = str(row.get("artifact_id", "")).strip()
    if explicit:
        return explicit
    field_names = KIND_ID_FIELDS.get(str(artifact_kind_id or "").strip(), ())
    for field_name in field_names:
        token = str(row.get(field_name, "")).strip()
        if token:
            return token
    return ""


def compute_artifact_content_hash(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["content_hash"] = ""
        body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _hash_bytes(payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(payload)
    return digest.hexdigest()


def compute_artifact_content_hash_from_path(path: str) -> str:
    abs_path = os.path.abspath(str(path or "").strip())
    with open(abs_path, "rb") as handle:
        raw = handle.read()
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _hash_bytes(raw)
    try:
        payload = json.loads(decoded)
    except ValueError:
        return _hash_bytes(raw)
    if isinstance(payload, Mapping):
        return canonical_sha256(_normalize_value(normalize_extensions_tree(dict(payload))))
    if isinstance(payload, list):
        return canonical_sha256(_normalize_value(payload))
    return canonical_sha256(payload)


def canonicalize_artifact_manifest(
    payload: Mapping[str, object],
    *,
    expected_kind_id: str = "",
    content_path: str = "",
) -> dict:
    normalized = normalize_artifact_manifest(payload, expected_kind_id=expected_kind_id)
    normalized["content_hash"] = (
        compute_artifact_content_hash_from_path(content_path)
        if str(content_path or "").strip()
        else compute_artifact_content_hash(normalized)
    )
    if not str(normalized.get("artifact_id", "")).strip():
        normalized["artifact_id"] = stable_artifact_id(
            {
                "artifact_kind_id": str(normalized.get("artifact_kind_id", "")).strip(),
                "content_hash": str(normalized.get("content_hash", "")).strip(),
            }
        )
    normalized["deterministic_fingerprint"] = ""
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return _normalize_value(normalized)


def normalize_artifact_manifest(payload: Mapping[str, object], *, expected_kind_id: str = "") -> dict:
    manifest = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    artifact_kind_id = infer_artifact_kind_id(manifest, expected_kind_id=expected_kind_id)
    format_version = (
        str(manifest.get("format_version", "")).strip()
        or str(manifest.get("schema_version", "")).strip()
        or CURRENT_ARTIFACT_FORMAT_VERSION
    )
    degrade_mode_id = str(manifest.get("degrade_mode_id", "")).strip() or ARTIFACT_DEGRADE_STRICT_REFUSE
    if degrade_mode_id not in ARTIFACT_DEGRADE_MODE_VALUES:
        degrade_mode_id = ARTIFACT_DEGRADE_STRICT_REFUSE
    normalized = dict(manifest)
    normalized["artifact_id"] = infer_artifact_id(manifest, artifact_kind_id) or str(manifest.get("artifact_id", "")).strip()
    normalized["artifact_kind_id"] = artifact_kind_id
    normalized["format_version"] = format_version
    normalized["content_hash"] = str(manifest.get("content_hash", "")).strip()
    normalized["required_contract_ranges"] = _normalize_contract_ranges(
        manifest.get("required_contract_ranges", manifest.get("required_contracts", {}))
    )
    normalized["required_capabilities"] = _sorted_unique_strings(manifest.get("required_capabilities"))
    normalized["compatible_topology_profiles"] = _sorted_unique_strings(manifest.get("compatible_topology_profiles"))
    normalized["compatible_physics_profiles"] = _sorted_unique_strings(manifest.get("compatible_physics_profiles"))
    normalized["degrade_mode_id"] = degrade_mode_id
    normalized["migration_refs"] = _normalize_migration_refs(
        manifest.get("migration_refs", manifest.get("migration_history", []))
    )
    normalized["extensions"] = normalize_extensions_map(_as_map(manifest.get("extensions")))
    normalized["deterministic_fingerprint"] = str(manifest.get("deterministic_fingerprint", "")).strip()
    return _normalize_value(normalized)


def _required_fields(manifest: Mapping[str, object]) -> List[str]:
    required = (
        "artifact_id",
        "artifact_kind_id",
        "format_version",
        "content_hash",
        "required_contract_ranges",
        "degrade_mode_id",
        "migration_refs",
        "deterministic_fingerprint",
        "extensions",
    )
    missing: List[str] = []
    for field in required:
        value = manifest.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if isinstance(value, dict):
            if field in ("required_contract_ranges", "extensions"):
                continue
            if value:
                continue
        if isinstance(value, list) and field == "migration_refs":
            continue
        missing.append(field)
    return missing


def validate_artifact_manifest(
    *,
    repo_root: str,
    artifact_manifest_path: str = "",
    manifest_payload: Mapping[str, object] | None = None,
    expected_kind_id: str = "",
    content_path: str = "",
) -> Dict[str, object]:
    del repo_root
    if manifest_payload is None:
        try:
            payload = json.load(open(artifact_manifest_path, "r", encoding="utf-8"))
        except (OSError, ValueError):
            return {
                "result": "refused",
                "refusal_code": REFUSAL_ARTIFACT_MANIFEST_REQUIRED,
                "errors": [
                    {
                        "code": "artifact_manifest_invalid",
                        "path": "$",
                        "message": "unable to load artifact manifest",
                    }
                ],
                "warnings": [],
                "artifact_manifest": {},
            }
    else:
        payload = dict(manifest_payload or {})

    manifest = normalize_artifact_manifest(payload, expected_kind_id=expected_kind_id)
    errors: List[dict] = []
    warnings: List[dict] = []

    for field in _required_fields(manifest):
        errors.append(
            {
                "code": "artifact_manifest_missing_field",
                "path": "$.{}".format(field),
                "message": "missing required field '{}'".format(field),
            }
        )

    if expected_kind_id and str(manifest.get("artifact_kind_id", "")).strip() != str(expected_kind_id).strip():
        errors.append(
            {
                "code": "artifact_manifest_kind_mismatch",
                "path": "$.artifact_kind_id",
                "message": "artifact_kind_id does not match the expected kind",
            }
        )

    if str(manifest.get("degrade_mode_id", "")).strip() not in ARTIFACT_DEGRADE_MODE_VALUES:
        errors.append(
            {
                "code": "artifact_manifest_invalid_degrade_mode",
                "path": "$.degrade_mode_id",
                "message": "degrade_mode_id must be a registered artifact degrade mode",
            }
        )

    artifact_id = str(manifest.get("artifact_id", "")).strip()
    if artifact_id and ("/" in artifact_id or "\\" in artifact_id):
        errors.append(
            {
                "code": "artifact_manifest_invalid_artifact_id",
                "path": "$.artifact_id",
                "message": "artifact_id must not contain path separators",
            }
        )

    actual_content_hash = (
        compute_artifact_content_hash_from_path(content_path)
        if str(content_path or "").strip()
        else compute_artifact_content_hash(manifest)
    )
    if str(manifest.get("content_hash", "")).strip() != actual_content_hash:
        errors.append(
            {
                "code": REFUSAL_ARTIFACT_HASH_MISMATCH,
                "path": "$.content_hash",
                "message": "content_hash mismatch",
            }
        )

    expected_fingerprint = deterministic_fingerprint(manifest)
    if str(manifest.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
        errors.append(
            {
                "code": REFUSAL_ARTIFACT_HASH_MISMATCH,
                "path": "$.deterministic_fingerprint",
                "message": "deterministic_fingerprint mismatch",
            }
        )

    result = "complete" if not errors else "refused"
    refusal_code = str(errors[0].get("code", "")).strip() if errors else ""
    return {
        "result": result,
        "refusal_code": refusal_code,
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "warnings": warnings,
        "artifact_manifest": manifest,
    }


def normalize_artifact_reference(payload: Mapping[str, object] | None) -> dict:
    row = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    normalized = {
        "artifact_id": str(_as_map(row).get("artifact_id", "")).strip(),
        "content_hash": str(_as_map(row).get("content_hash", "")).strip(),
        "expected_hash": str(_as_map(row).get("expected_hash", "")).strip(),
        "deterministic_fingerprint": str(_as_map(row).get("deterministic_fingerprint", "")).strip(),
        "extensions": normalize_extensions_map(_as_map(_as_map(row).get("extensions"))),
    }
    if not normalized["expected_hash"]:
        normalized["expected_hash"] = normalized["content_hash"]
    return _normalize_value(normalized)


def canonicalize_artifact_reference(payload: Mapping[str, object] | None) -> dict:
    normalized = normalize_artifact_reference(payload)
    normalized["deterministic_fingerprint"] = ""
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return _normalize_value(normalized)


def validate_artifact_reference(payload: Mapping[str, object] | None) -> Dict[str, object]:
    reference = normalize_artifact_reference(payload)
    errors: List[dict] = []
    if not str(reference.get("artifact_id", "")).strip() and not str(reference.get("content_hash", "")).strip():
        errors.append(
            {
                "code": "artifact_reference_missing_locator",
                "path": "$",
                "message": "artifact reference requires artifact_id or content_hash",
            }
        )
    expected_fingerprint = deterministic_fingerprint(reference)
    if str(reference.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
        errors.append(
            {
                "code": REFUSAL_ARTIFACT_HASH_MISMATCH,
                "path": "$.deterministic_fingerprint",
                "message": "artifact reference deterministic_fingerprint mismatch",
            }
        )
    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": str(errors[0].get("code", "")).strip() if errors else "",
        "errors": errors,
        "artifact_reference": reference,
    }


def _apply_degrade_policy(
    *,
    degrade_mode_id: str,
    allow_read_only: bool,
    compatibility_mode: str,
    refusal_code: str,
    degrade_reason: str,
    degrade_reasons: List[str],
) -> Tuple[str, str, bool]:
    if degrade_mode_id == ARTIFACT_DEGRADE_STRICT_REFUSE:
        return "refuse", refusal_code, False
    if degrade_mode_id == ARTIFACT_DEGRADE_READ_ONLY_ONLY:
        if not allow_read_only:
            return "refuse", REFUSAL_ARTIFACT_READ_ONLY_REQUIRED, False
        if degrade_reason not in degrade_reasons:
            degrade_reasons.append(degrade_reason)
        return "inspect-only", "", True
    if compatibility_mode != "inspect-only":
        compatibility_mode = "degraded"
    if degrade_reason not in degrade_reasons:
        degrade_reasons.append(degrade_reason)
    return compatibility_mode, "", False


def evaluate_artifact_load(
    *,
    repo_root: str,
    artifact_manifest_path: str = "",
    manifest_payload: Mapping[str, object] | None = None,
    expected_kind_id: str = "",
    install_manifest: Mapping[str, object] | None = None,
    provided_capabilities: Sequence[str] | None = None,
    topology_profile_id: str = "",
    physics_profile_id: str = "",
    allow_read_only: bool = False,
    allow_artifact_migration: bool = False,
    content_path: str = "",
) -> Dict[str, object]:
    validation = validate_artifact_manifest(
        repo_root=repo_root,
        artifact_manifest_path=artifact_manifest_path,
        manifest_payload=manifest_payload,
        expected_kind_id=expected_kind_id,
        content_path=content_path,
    )
    if validation.get("result") != "complete":
        return {
            "result": "refused",
            "refusal_code": str(validation.get("refusal_code", REFUSAL_ARTIFACT_MANIFEST_REQUIRED)).strip() or REFUSAL_ARTIFACT_MANIFEST_REQUIRED,
            "compatibility_mode": "refuse",
            "artifact_manifest": dict(validation.get("artifact_manifest") or {}),
            "artifact_validation": validation,
            "degrade_reasons": [],
            "read_only_required": False,
            "migration_required": False,
        }

    manifest = dict(validation.get("artifact_manifest") or {})
    degrade_mode_id = str(manifest.get("degrade_mode_id", ARTIFACT_DEGRADE_STRICT_REFUSE)).strip() or ARTIFACT_DEGRADE_STRICT_REFUSE
    compatibility_mode = "full"
    refusal_code = ""
    degrade_reasons: List[str] = []
    read_only_required = False

    required_contract_ranges = dict(manifest.get("required_contract_ranges") or {})
    required_capabilities = list(manifest.get("required_capabilities") or [])
    compatible_topology_profiles = list(manifest.get("compatible_topology_profiles") or [])
    compatible_physics_profiles = list(manifest.get("compatible_physics_profiles") or [])

    contract_mismatches: List[dict] = []
    if install_manifest is not None and required_contract_ranges:
        contract_mismatches = compare_required_contract_ranges(install_manifest, required_contract_ranges)
        if contract_mismatches:
            compatibility_mode, refusal_code, read_only_required = _apply_degrade_policy(
                degrade_mode_id=degrade_mode_id,
                allow_read_only=allow_read_only,
                compatibility_mode=compatibility_mode,
                refusal_code=REFUSAL_ARTIFACT_CONTRACT_RANGE_MISMATCH,
                degrade_reason="artifact_contract_range_mismatch",
                degrade_reasons=degrade_reasons,
            )

    missing_capabilities: List[str] = []
    if provided_capabilities is not None and required_capabilities:
        provided = set(_sorted_unique_strings(list(provided_capabilities)))
        missing_capabilities = sorted(set(required_capabilities) - provided)
        if missing_capabilities and compatibility_mode != "refuse":
            compatibility_mode, refusal_code, read_only_required = _apply_degrade_policy(
                degrade_mode_id=degrade_mode_id,
                allow_read_only=allow_read_only,
                compatibility_mode=compatibility_mode,
                refusal_code=REFUSAL_ARTIFACT_CAPABILITY_MISMATCH,
                degrade_reason="artifact_capability_mismatch",
                degrade_reasons=degrade_reasons,
            )

    topology_mismatch = bool(
        compatible_topology_profiles
        and str(topology_profile_id or "").strip()
        and str(topology_profile_id or "").strip() not in set(compatible_topology_profiles)
    )
    if topology_mismatch and compatibility_mode != "refuse":
        compatibility_mode, refusal_code, read_only_required = _apply_degrade_policy(
            degrade_mode_id=degrade_mode_id,
            allow_read_only=allow_read_only,
            compatibility_mode=compatibility_mode,
            refusal_code=REFUSAL_ARTIFACT_TOPOLOGY_MISMATCH,
            degrade_reason="artifact_topology_profile_mismatch",
            degrade_reasons=degrade_reasons,
        )

    physics_mismatch = bool(
        compatible_physics_profiles
        and str(physics_profile_id or "").strip()
        and str(physics_profile_id or "").strip() not in set(compatible_physics_profiles)
    )
    if physics_mismatch and compatibility_mode != "refuse":
        compatibility_mode, refusal_code, read_only_required = _apply_degrade_policy(
            degrade_mode_id=degrade_mode_id,
            allow_read_only=allow_read_only,
            compatibility_mode=compatibility_mode,
            refusal_code=REFUSAL_ARTIFACT_PHYSICS_MISMATCH,
            degrade_reason="artifact_physics_profile_mismatch",
            degrade_reasons=degrade_reasons,
        )

    migration_required = str(manifest.get("format_version", CURRENT_ARTIFACT_FORMAT_VERSION)).strip() != CURRENT_ARTIFACT_FORMAT_VERSION
    if migration_required and not allow_artifact_migration and compatibility_mode != "refuse":
        compatibility_mode, refusal_code, read_only_required = _apply_degrade_policy(
            degrade_mode_id=ARTIFACT_DEGRADE_READ_ONLY_ONLY if allow_read_only else ARTIFACT_DEGRADE_STRICT_REFUSE,
            allow_read_only=allow_read_only,
            compatibility_mode=compatibility_mode,
            refusal_code=REFUSAL_ARTIFACT_MIGRATION_REQUIRED,
            degrade_reason="artifact_migration_required",
            degrade_reasons=degrade_reasons,
        )

    return {
        "result": "refused" if compatibility_mode == "refuse" else "complete",
        "refusal_code": refusal_code,
        "compatibility_mode": compatibility_mode,
        "artifact_manifest": manifest,
        "artifact_validation": validation,
        "required_contract_ranges": required_contract_ranges,
        "contract_mismatches": contract_mismatches,
        "required_capabilities": required_capabilities,
        "missing_capabilities": missing_capabilities,
        "compatible_topology_profiles": compatible_topology_profiles,
        "compatible_physics_profiles": compatible_physics_profiles,
        "topology_profile_mismatch": topology_mismatch,
        "physics_profile_mismatch": physics_mismatch,
        "degrade_reasons": sorted(degrade_reasons),
        "read_only_required": bool(read_only_required or compatibility_mode == "inspect-only"),
        "migration_required": bool(migration_required and not allow_artifact_migration),
    }


__all__ = [
    "ARTIFACT_DEGRADE_BEST_EFFORT",
    "ARTIFACT_DEGRADE_MODE_VALUES",
    "ARTIFACT_DEGRADE_READ_ONLY_ONLY",
    "ARTIFACT_DEGRADE_STRICT_REFUSE",
    "ARTIFACT_KIND_BLUEPRINT",
    "ARTIFACT_KIND_LOGIC_PROGRAM",
    "ARTIFACT_KIND_PROCESS_DEFINITION",
    "ARTIFACT_KIND_PROFILE_BUNDLE",
    "ARTIFACT_KIND_RESOURCE_PACK_STUB",
    "ARTIFACT_KIND_SYSTEM_TEMPLATE",
    "ARTIFACT_KIND_VALUES",
    "ARTIFACT_KIND_VIEW_PRESET",
    "CURRENT_ARTIFACT_FORMAT_VERSION",
    "REFUSAL_ARTIFACT_CAPABILITY_MISMATCH",
    "REFUSAL_ARTIFACT_CONTRACT_RANGE_MISMATCH",
    "REFUSAL_ARTIFACT_HASH_MISMATCH",
    "REFUSAL_ARTIFACT_MANIFEST_REQUIRED",
    "REFUSAL_ARTIFACT_MIGRATION_REQUIRED",
    "REFUSAL_ARTIFACT_PHYSICS_MISMATCH",
    "REFUSAL_ARTIFACT_READ_ONLY_REQUIRED",
    "REFUSAL_ARTIFACT_TOPOLOGY_MISMATCH",
    "artifact_kind_from_store_category",
    "artifact_store_category",
    "canonicalize_artifact_manifest",
    "canonicalize_artifact_reference",
    "compute_artifact_content_hash",
    "compute_artifact_content_hash_from_path",
    "deterministic_fingerprint",
    "evaluate_artifact_load",
    "infer_artifact_id",
    "infer_artifact_kind_id",
    "normalize_artifact_manifest",
    "normalize_artifact_reference",
    "stable_artifact_id",
    "validate_artifact_manifest",
    "validate_artifact_reference",
    "write_json",
]
