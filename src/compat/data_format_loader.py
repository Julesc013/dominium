"""Deterministic artifact format-version loading, migration, and read-only fallback."""

from __future__ import annotations

import copy
import json
import os
from typing import Dict, List, Mapping, Sequence, Tuple

from src.compat.capability_negotiation import READ_ONLY_LAW_PROFILE_ID
from src.compat.descriptor.descriptor_engine import build_product_descriptor
from tools.compatx.core.migration_runner import apply_migration, load_and_validate
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance


CURRENT_ARTIFACT_FORMAT_VERSION = "2.0.0"
LEGACY_ARTIFACT_FORMAT_VERSION = "1.0.0"
MIGRATION_REGISTRY_REL = os.path.join("data", "registries", "migration_registry.json")

REFUSAL_FORMAT_MISSING_VERSION = "refusal.format.missing_version"
REFUSAL_FORMAT_MIGRATION_MISSING = "refusal.format.migration_missing"
REFUSAL_FORMAT_FUTURE_VERSION = "refusal.format.future_version"
REFUSAL_FORMAT_METADATA_INVALID = "refusal.format.metadata_invalid"
REFUSAL_FORMAT_SCHEMA_INVALID = "refusal.format.schema_invalid"
REFUSAL_FORMAT_CONTRACT_MISMATCH = "refusal.format.contract_mismatch"
REFUSAL_FORMAT_READ_ONLY_UNAVAILABLE = "refusal.format.read_only_unavailable"

_ARTIFACT_RULES = {
    "save_file": {
        "base_schema_name": "universe_state",
        "component_type": "save",
        "metadata_fields": (
            "format_version",
            "semantic_contract_bundle_hash",
            "engine_version_created",
            "migration_history",
            "deterministic_fingerprint",
        ),
        "requires_contract_hash": True,
        "supports_required_contract_ranges": False,
    },
    "blueprint_file": {
        "base_schema_name": "blueprint",
        "component_type": "blueprint",
        "metadata_fields": (
            "format_version",
            "required_contract_ranges",
            "engine_version_created",
            "migration_history",
            "deterministic_fingerprint",
        ),
        "requires_contract_hash": False,
        "supports_required_contract_ranges": True,
    },
    "profile_bundle": {
        "base_schema_name": "",
        "component_type": "profile",
        "metadata_fields": (
            "format_version",
            "engine_version_created",
            "migration_history",
            "deterministic_fingerprint",
        ),
        "requires_contract_hash": False,
        "supports_required_contract_ranges": False,
        "fingerprint_ignored_fields": ("profile_bundle_hash",),
    },
    "session_template": {
        "base_schema_name": "",
        "component_type": "session_template",
        "metadata_fields": (
            "format_version",
            "engine_version_created",
            "migration_history",
            "deterministic_fingerprint",
        ),
        "requires_contract_hash": False,
        "supports_required_contract_ranges": False,
    },
    "pack_lock": {
        "base_schema_name": "pack_lock",
        "component_type": "pack_lock",
        "metadata_fields": (
            "format_version",
            "engine_version_created",
            "migration_history",
            "deterministic_fingerprint",
        ),
        "requires_contract_hash": False,
        "supports_required_contract_ranges": False,
    },
}


def _semver_tuple(token: object) -> Tuple[int, int, int]:
    text = str(token or "").strip()
    parts = text.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return (0, 0, 0)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Sequence[object] | object) -> List[str]:
    items = list(values or []) if isinstance(values, Sequence) and not isinstance(values, (str, bytes, bytearray)) else []
    return sorted(set(str(item).strip() for item in items if str(item).strip()))


def _read_json_object(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _refusal(reason_code: str, message: str, remediation_hint: str, *, path: str = "$", relevant_ids: Mapping[str, object] | None = None) -> dict:
    ids = {}
    for key, value in sorted(_as_map(relevant_ids).items(), key=lambda row: str(row[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def current_format_version(_artifact_kind: str) -> str:
    return CURRENT_ARTIFACT_FORMAT_VERSION


def artifact_deterministic_fingerprint(payload: Mapping[str, object], *, ignored_fields: Sequence[str] | None = None) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    for field_name in list(ignored_fields or []):
        token = str(field_name).strip()
        if token:
            body[token] = ""
    return canonical_sha256(body)


def current_engine_version_created(repo_root: str) -> str:
    descriptor = build_product_descriptor(repo_root, product_id="engine")
    token = str(descriptor.get("product_version", "")).strip()
    if not token:
        raise ValueError("engine descriptor missing product_version")
    return token


def stamp_artifact_metadata(
    repo_root: str,
    artifact_kind: str,
    payload: Mapping[str, object],
    *,
    semantic_contract_bundle_hash: str = "",
    required_contract_ranges: Mapping[str, object] | None = None,
    engine_version_created: str = "",
    update_fingerprint: bool = True,
) -> dict:
    rules = dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {})
    if not rules:
        raise ValueError("unknown artifact_kind '{}'".format(str(artifact_kind)))
    stamped = copy.deepcopy(dict(payload or {}))
    stamped["format_version"] = CURRENT_ARTIFACT_FORMAT_VERSION
    stamped["engine_version_created"] = str(engine_version_created or current_engine_version_created(repo_root)).strip()
    if rules.get("requires_contract_hash"):
        stamped["semantic_contract_bundle_hash"] = str(semantic_contract_bundle_hash or "").strip()
    if rules.get("supports_required_contract_ranges"):
        ranges = _as_map(required_contract_ranges or stamped.get("required_contract_ranges"))
        stamped["required_contract_ranges"] = {
            str(key): copy.deepcopy(ranges[key])
            for key in sorted(ranges.keys(), key=lambda item: str(item))
            if str(key).strip()
        }
    history = list(stamped.get("migration_history") or [])
    if history:
        stamped["migration_history"] = sorted(
            [copy.deepcopy(row) for row in history if isinstance(row, Mapping)],
            key=lambda row: (
                str(dict(row).get("migration_id", "")),
                str(dict(row).get("from_version", "")),
                str(dict(row).get("to_version", "")),
            ),
        )
    elif "migration_history" in stamped:
        stamped.pop("migration_history", None)
    if update_fingerprint:
        stamped["deterministic_fingerprint"] = artifact_deterministic_fingerprint(
            stamped,
            ignored_fields=rules.get("fingerprint_ignored_fields"),
        )
    return stamped


def strip_artifact_metadata(artifact_kind: str, payload: Mapping[str, object]) -> dict:
    rules = dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {})
    stripped = copy.deepcopy(dict(payload or {}))
    for field_name in list(rules.get("metadata_fields") or []):
        stripped.pop(str(field_name), None)
    return stripped


def _metadata_errors(
    artifact_kind: str,
    payload: Mapping[str, object],
    *,
    expected_contract_bundle_hash: str = "",
    future_version_allowed: bool = False,
) -> List[str]:
    rules = dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {})
    row = dict(payload or {})
    errors: List[str] = []
    version = str(row.get("format_version", "")).strip()
    if future_version_allowed:
        if not version:
            errors.append("missing format_version")
    elif version != CURRENT_ARTIFACT_FORMAT_VERSION:
        errors.append("format_version mismatch")
    if not str(row.get("engine_version_created", "")).strip():
        errors.append("engine_version_created missing")
    if rules.get("requires_contract_hash"):
        contract_hash = str(row.get("semantic_contract_bundle_hash", "")).strip()
        if not contract_hash:
            errors.append("semantic_contract_bundle_hash missing")
        elif str(expected_contract_bundle_hash or "").strip() and contract_hash != str(expected_contract_bundle_hash).strip():
            errors.append("semantic_contract_bundle_hash mismatch")
    fingerprint = str(row.get("deterministic_fingerprint", "")).strip()
    if not fingerprint:
        errors.append("deterministic_fingerprint missing")
    elif fingerprint != artifact_deterministic_fingerprint(
        row,
        ignored_fields=rules.get("fingerprint_ignored_fields"),
    ):
        errors.append("deterministic_fingerprint mismatch")
    if rules.get("supports_required_contract_ranges") and "required_contract_ranges" in row:
        ranges = row.get("required_contract_ranges")
        if not isinstance(ranges, Mapping):
            errors.append("required_contract_ranges invalid")
    return sorted(set(errors))


def _validate_base_schema(repo_root: str, artifact_kind: str, payload: Mapping[str, object], *, strict_top_level: bool) -> dict:
    schema_name = str(dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {}).get("base_schema_name", "")).strip()
    if not schema_name:
        return {"valid": True, "errors": []}
    return validate_instance(
        repo_root=repo_root,
        schema_name=schema_name,
        payload=dict(payload),
        strict_top_level=bool(strict_top_level),
    )


def _migration_rows_for_artifact(repo_root: str, artifact_kind: str) -> Tuple[List[dict], dict]:
    rows, errors = load_and_validate(os.path.join(repo_root, MIGRATION_REGISTRY_REL.replace("/", os.sep)))
    if errors:
        return [], _refusal(
            REFUSAL_FORMAT_MIGRATION_MISSING,
            "migration registry is missing or invalid",
            "Restore data/registries/migration_registry.json before loading versioned artifacts.",
            path="$.migration_registry",
            relevant_ids={"artifact_kind": artifact_kind},
        )
    component_type = str(dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {}).get("component_type", "")).strip()
    selected = [
        dict(row)
        for row in rows
        if str(dict(row).get("component_type", "")).strip() == component_type
    ]
    return sorted(selected, key=lambda row: (str(row.get("from_version", "")), str(row.get("to_version", "")), str(row.get("migration_id", "")))), {}


def _build_migration_chain(repo_root: str, artifact_kind: str, from_version: str) -> Tuple[List[dict], dict]:
    rows, error = _migration_rows_for_artifact(repo_root, artifact_kind)
    if error:
        return [], error
    by_from: Dict[str, dict] = {}
    for row in rows:
        token = str(row.get("from_version", "")).strip()
        if token and token not in by_from:
            by_from[token] = dict(row)
    chain: List[dict] = []
    current = str(from_version or "").strip()
    guard = set()
    while current and current != CURRENT_ARTIFACT_FORMAT_VERSION:
        if current in guard:
            return [], _refusal(
                REFUSAL_FORMAT_MIGRATION_MISSING,
                "migration registry contains a non-terminating migration chain",
                "Repair PACK-COMPAT-2 migration_registry.json so artifact migrations converge on the current format.",
                path="$.migration_registry",
                relevant_ids={"artifact_kind": artifact_kind, "from_version": current},
            )
        guard.add(current)
        row = dict(by_from.get(current) or {})
        if not row:
            return [], _refusal(
                REFUSAL_FORMAT_MIGRATION_MISSING,
                "no deterministic migration chain exists for the artifact format",
                "Provide a CompatX migration path or load the artifact in a compatible engine build.",
                path="$.format_version",
                relevant_ids={"artifact_kind": artifact_kind, "from_version": from_version, "to_version": CURRENT_ARTIFACT_FORMAT_VERSION},
            )
        chain.append(row)
        current = str(row.get("to_version", "")).strip()
    return chain, {}


def _apply_migration_chain(
    repo_root: str,
    artifact_kind: str,
    payload: Mapping[str, object],
    *,
    semantic_contract_bundle_hash: str = "",
) -> Tuple[dict, List[dict], dict]:
    version = str(dict(payload or {}).get("format_version", "")).strip() or LEGACY_ARTIFACT_FORMAT_VERSION
    chain, error = _build_migration_chain(repo_root, artifact_kind, version)
    if error:
        return {}, [], error
    current = copy.deepcopy(dict(payload or {}))
    migration_events: List[dict] = []
    for migration in chain:
        migration = dict(migration or {})
        current = apply_migration(current, migration)
        current = stamp_artifact_metadata(
            repo_root=repo_root,
            artifact_kind=artifact_kind,
            payload=current,
            semantic_contract_bundle_hash=semantic_contract_bundle_hash,
            update_fingerprint=True,
        )
        migration_events.append(
            {
                "migration_id": str(migration.get("migration_id", "")).strip(),
                "from_version": str(migration.get("from_version", "")).strip(),
                "to_version": str(migration.get("to_version", "")).strip(),
                "deterministic_transform_function_id": str(migration.get("deterministic_transform_function_id", "")).strip(),
                "artifact_kind": str(artifact_kind).strip(),
            }
        )
    return current, migration_events, {}


def _future_read_only_allowed(
    artifact_kind: str,
    payload: Mapping[str, object],
    *,
    expected_contract_bundle_hash: str = "",
) -> bool:
    rules = dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {})
    if rules.get("requires_contract_hash"):
        actual = str(dict(payload or {}).get("semantic_contract_bundle_hash", "")).strip()
        expected = str(expected_contract_bundle_hash or "").strip()
        if expected and actual and expected != actual:
            return False
    base_report = _validate_base_schema(os.getcwd(), artifact_kind, payload, strict_top_level=False)
    return bool(base_report.get("valid", False)) or not str(rules.get("base_schema_name", "")).strip()


def load_versioned_artifact(
    repo_root: str,
    artifact_kind: str,
    path: str,
    *,
    semantic_contract_bundle_hash: str = "",
    allow_read_only: bool = False,
    strip_loaded_metadata: bool = False,
) -> Tuple[dict, dict, dict]:
    rules = dict(_ARTIFACT_RULES.get(str(artifact_kind).strip()) or {})
    if not rules:
        return {}, {}, _refusal(
            REFUSAL_FORMAT_SCHEMA_INVALID,
            "artifact_kind is not declared for PACK-COMPAT-2 loading",
            "Use a supported PACK-COMPAT-2 artifact kind.",
            path="$",
            relevant_ids={"artifact_kind": artifact_kind},
        )
    payload, err = _read_json_object(path)
    if err:
        return {}, {}, _refusal(
            REFUSAL_FORMAT_SCHEMA_INVALID,
            "unable to parse artifact JSON payload",
            "Restore the artifact file so it contains a valid JSON object.",
            path="$",
            relevant_ids={"artifact_kind": artifact_kind, "path": _norm(path)},
        )
    raw_version = str(payload.get("format_version", "")).strip() or LEGACY_ARTIFACT_FORMAT_VERSION
    migration_events: List[dict] = []
    read_only_mode = False

    current_tuple = _semver_tuple(CURRENT_ARTIFACT_FORMAT_VERSION)
    raw_tuple = _semver_tuple(raw_version)
    if raw_version == CURRENT_ARTIFACT_FORMAT_VERSION:
        loaded = copy.deepcopy(payload)
    elif raw_tuple < current_tuple:
        loaded, migration_events, migration_error = _apply_migration_chain(
            repo_root=repo_root,
            artifact_kind=artifact_kind,
            payload=payload,
            semantic_contract_bundle_hash=semantic_contract_bundle_hash,
        )
        if migration_error:
            return {}, {}, migration_error
    else:
        if not allow_read_only:
            return {}, {}, _refusal(
                REFUSAL_FORMAT_FUTURE_VERSION,
                "artifact format_version is newer than this engine build supports",
                "Open the artifact in a newer engine build or use a read-only compatibility path.",
                path="$.format_version",
                relevant_ids={"artifact_kind": artifact_kind, "path": _norm(path), "format_version": raw_version},
            )
        base_report = _validate_base_schema(repo_root, artifact_kind, payload, strict_top_level=False)
        if str(dict(payload).get("semantic_contract_bundle_hash", "")).strip():
            expected = str(semantic_contract_bundle_hash or "").strip()
            actual = str(dict(payload).get("semantic_contract_bundle_hash", "")).strip()
            if expected and actual != expected:
                return {}, {}, _refusal(
                    REFUSAL_FORMAT_CONTRACT_MISMATCH,
                    "future-format artifact contract hash does not match the expected pinned contract bundle",
                    "Use a compatible artifact or run a CompatX migration tool before loading.",
                    path="$.semantic_contract_bundle_hash",
                    relevant_ids={"artifact_kind": artifact_kind, "expected": expected, "actual": actual},
                )
        if not bool(base_report.get("valid", False)):
            return {}, {}, _refusal(
                REFUSAL_FORMAT_READ_ONLY_UNAVAILABLE,
                "future-format artifact cannot be opened safely in read-only mode",
                "Use a newer engine build or install a migration path for the artifact.",
                path="$",
                relevant_ids={"artifact_kind": artifact_kind, "path": _norm(path), "format_version": raw_version},
            )
        loaded = copy.deepcopy(payload)
        read_only_mode = True

    strict_base = not read_only_mode
    base_report = _validate_base_schema(repo_root, artifact_kind, loaded, strict_top_level=strict_base)
    if not bool(base_report.get("valid", False)):
        return {}, {}, _refusal(
            REFUSAL_FORMAT_SCHEMA_INVALID,
            "artifact payload failed base schema validation",
            "Repair the artifact payload so it satisfies the current structural schema before loading.",
            path="$",
            relevant_ids={"artifact_kind": artifact_kind, "path": _norm(path)},
        )

    metadata_errors = _metadata_errors(
        artifact_kind,
        loaded,
        expected_contract_bundle_hash=semantic_contract_bundle_hash,
        future_version_allowed=read_only_mode,
    )
    if metadata_errors:
        return {}, {}, _refusal(
            REFUSAL_FORMAT_METADATA_INVALID,
            "artifact format metadata is missing or invalid",
            "Regenerate the artifact with PACK-COMPAT-2 metadata or run the declared CompatX migration chain.",
            path="$",
            relevant_ids={"artifact_kind": artifact_kind, "errors": ",".join(metadata_errors)},
        )

    returned_payload = strip_artifact_metadata(artifact_kind, loaded) if strip_loaded_metadata else dict(loaded)
    meta = {
        "result": "complete",
        "artifact_kind": str(artifact_kind).strip(),
        "path": _norm(path),
        "format_version": str(loaded.get("format_version", "")).strip(),
        "migration_events": list(migration_events),
        "read_only_mode": bool(read_only_mode),
        "law_profile_id_override": READ_ONLY_LAW_PROFILE_ID if read_only_mode else "",
        "explain_keys": [
            "explain.read_only_mode" if read_only_mode else "",
            "explain.migration_applied" if migration_events else "",
        ],
    }
    meta["explain_keys"] = [token for token in meta["explain_keys"] if token]
    return returned_payload, meta, {}
