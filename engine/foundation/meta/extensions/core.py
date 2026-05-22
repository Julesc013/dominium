"""Deterministic extension validation, normalization, and registry-backed access."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


EXTENSION_INTERPRETATION_REGISTRY_REL = os.path.join("data", "registries", "extension_interpretation_registry.json")
DEFAULT_EXTENSION_POLICY_ID = "extensions.default"
WARN_EXTENSION_POLICY_ID = "extensions.warn"
STRICT_EXTENSION_POLICY_ID = "extensions.strict"

_NAMESPACED_KEY_RE = re.compile(
    r"^(?:official|dev)\.[a-z0-9][a-z0-9_.-]*$|^mod\.[a-z0-9][a-z0-9_.-]*\.[a-z0-9][a-z0-9_.-]*$"
)
_LEGACY_BARE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
_INVALID_FLOAT_TYPES = (float,)


def _canonical_json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json_text(value).encode("utf-8")).hexdigest()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json: {}".format(path.replace("\\", "/"))
    if not isinstance(payload, dict):
        return {}, "invalid root object: {}".format(path.replace("\\", "/"))
    return dict(payload), ""


def _message(code: str, path: str, message: str) -> dict:
    return {"code": str(code), "path": str(path), "message": str(message)}


def _child_path(parent: str, key: str) -> str:
    if parent == "$":
        return "$.{}".format(key)
    return "{}.{}".format(parent, key)


def legacy_alias_for_key(key: object) -> str:
    token = str(key or "").strip()
    if not token:
        return ""
    return "mod.unknown.{}".format(token)


def _key_classification(key: object) -> Tuple[str, str]:
    token = str(key or "").strip()
    if not token:
        return "invalid", ""
    if _NAMESPACED_KEY_RE.fullmatch(token):
        return "namespaced", token
    if _LEGACY_BARE_KEY_RE.fullmatch(token):
        return "legacy_bare", legacy_alias_for_key(token)
    return "invalid", ""


def _normalize_extension_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_extension_value(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_extension_value(item) for item in list(value)]
    return copy.deepcopy(value)


def normalize_extensions_map(extensions: Mapping[str, object] | None) -> dict:
    return {
        str(key): _normalize_extension_value(value)
        for key, value in sorted(_as_map(extensions).items(), key=lambda row: str(row[0]))
    }


def normalize_extensions_tree(value: object) -> object:
    if isinstance(value, Mapping):
        out = {}
        for key, item in sorted(dict(value).items(), key=lambda row: str(row[0])):
            token = str(key)
            if token == "extensions":
                out[token] = normalize_extensions_map(_as_map(item))
            else:
                out[token] = normalize_extensions_tree(item)
        return out
    if isinstance(value, list):
        return [normalize_extensions_tree(item) for item in list(value)]
    return copy.deepcopy(value)


def _entry_fingerprint(row: Mapping[str, object]) -> str:
    body = dict(row)
    body["deterministic_fingerprint"] = ""
    return _canonical_sha256(body)


def load_extension_interpretation_registry(repo_root: str) -> Tuple[dict, str]:
    payload, error = _read_json(os.path.join(repo_root, EXTENSION_INTERPRETATION_REGISTRY_REL))
    if error:
        return {}, error
    return normalize_extensions_tree(payload), ""


def normalize_extension_interpretation_rows(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    body = _as_map(payload)
    record = _as_map(body.get("record"))
    rows = record.get("extension_interpretations")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("extension_key", ""))):
        extension_key = str(row.get("extension_key", "")).strip()
        if not extension_key:
            continue
        normalized = {
            "extension_key": extension_key,
            "allowed_owners": _sorted_tokens(row.get("allowed_owners") or ["*"]),
            "value_type": str(row.get("value_type", "any")).strip() or "any",
            "semantic_contract_version_required": str(row.get("semantic_contract_version_required", "")).strip(),
            "profile_gate_required": str(row.get("profile_gate_required", DEFAULT_EXTENSION_POLICY_ID)).strip()
            or DEFAULT_EXTENSION_POLICY_ID,
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": normalize_extensions_map(_as_map(row.get("extensions"))),
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = _entry_fingerprint(normalized)
        out[extension_key] = normalized
        alias = str(_as_map(normalized.get("extensions")).get("legacy_alias_for", "")).strip()
        if alias and alias not in out:
            out[alias] = dict(normalized)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def extension_interpretation_registry_hash(payload: Mapping[str, object] | None) -> str:
    return _canonical_sha256(normalize_extensions_tree(_as_map(payload)))


def validate_extensions_map(
    *,
    owner_schema_id: str,
    extensions: Mapping[str, object] | None,
    registry_payload: Mapping[str, object] | None = None,
    policy_mode: str = DEFAULT_EXTENSION_POLICY_ID,
    path: str = "$.extensions",
) -> dict:
    normalized = normalize_extensions_map(extensions)
    registry_rows = normalize_extension_interpretation_rows(registry_payload)
    warnings: List[dict] = []
    errors: List[dict] = []
    owner_token = str(owner_schema_id or "").strip() or "*"
    mode = str(policy_mode or DEFAULT_EXTENSION_POLICY_ID).strip() or DEFAULT_EXTENSION_POLICY_ID

    for key, value in normalized.items():
        key_state, canonical_key = _key_classification(key)
        row = registry_rows.get(key) or registry_rows.get(canonical_key)
        row_extensions = _as_map((row or {}).get("extensions"))
        if key_state == "legacy_bare" and mode in {WARN_EXTENSION_POLICY_ID, STRICT_EXTENSION_POLICY_ID}:
            warnings.append(
                _message(
                    "extension.bare_key",
                    _child_path(path, key),
                    "bare extension key '{}' is legacy and is treated as '{}' in compatibility mode".format(key, canonical_key),
                )
            )
        elif key_state == "invalid":
            target = errors if mode == STRICT_EXTENSION_POLICY_ID else warnings
            target.append(
                _message(
                    "extension.invalid_key",
                    _child_path(path, key),
                    "extension key '{}' is invalid; expected official.*, dev.*, or mod.<pack_id>.*".format(key),
                )
            )

        if not row:
            if mode == WARN_EXTENSION_POLICY_ID:
                warnings.append(
                    _message(
                        "extension.unknown_key",
                        _child_path(path, key),
                        "unknown extension key '{}' is ignored in policy '{}'".format(key, mode),
                    )
                )
            elif mode == STRICT_EXTENSION_POLICY_ID and key_state == "namespaced":
                errors.append(
                    _message(
                        "extension.unknown_key",
                        _child_path(path, key),
                        "unknown extension key '{}' is refused in strict policy".format(key),
                    )
                )
        else:
            allowed_owners = _sorted_tokens((row or {}).get("allowed_owners") or ["*"])
            if "*" not in allowed_owners and owner_token not in allowed_owners:
                warnings.append(
                    _message(
                        "extension.owner_scope_warning",
                        _child_path(path, key),
                        "extension key '{}' is registered outside owner '{}'".format(key, owner_token),
                    )
                )
            if str((row or {}).get("profile_gate_required", "")).strip() == STRICT_EXTENSION_POLICY_ID and mode != STRICT_EXTENSION_POLICY_ID:
                warnings.append(
                    _message(
                        "extension.profile_gate_warning",
                        _child_path(path, key),
                        "extension key '{}' declares strict interpretation gate '{}'".format(
                            key, str((row or {}).get("profile_gate_required", "")).strip()
                        ),
                    )
                )
            if isinstance(value, _INVALID_FLOAT_TYPES) or isinstance(row_extensions.get("legacy_alias_for"), _INVALID_FLOAT_TYPES):
                target = errors if mode == STRICT_EXTENSION_POLICY_ID else warnings
                target.append(
                    _message(
                        "extension.float_value",
                        _child_path(path, key),
                        "extension key '{}' carries a float-like value; deterministic stable formats require non-float values".format(key),
                    )
                )

    return {
        "owner_schema_id": owner_token,
        "policy_mode": mode,
        "normalized_extensions": normalized,
        "warnings": sorted(warnings, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
    }


def validate_extensions_tree(
    *,
    owner_schema_id: str,
    payload: object,
    registry_payload: Mapping[str, object] | None = None,
    policy_mode: str = DEFAULT_EXTENSION_POLICY_ID,
) -> dict:
    warnings: List[dict] = []
    errors: List[dict] = []

    def _walk(node: object, path: str) -> None:
        if isinstance(node, Mapping):
            for key, value in sorted(dict(node).items(), key=lambda row: str(row[0])):
                subpath = _child_path(path, str(key))
                if str(key) == "extensions":
                    report = validate_extensions_map(
                        owner_schema_id=owner_schema_id,
                        extensions=_as_map(value),
                        registry_payload=registry_payload,
                        policy_mode=policy_mode,
                        path=subpath,
                    )
                    warnings.extend(list(report.get("warnings") or []))
                    errors.extend(list(report.get("errors") or []))
                else:
                    _walk(value, subpath)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                _walk(item, "{}[{}]".format(path, idx))

    _walk(payload, "$")
    return {
        "owner_schema_id": str(owner_schema_id or "").strip() or "*",
        "policy_mode": str(policy_mode or DEFAULT_EXTENSION_POLICY_ID).strip() or DEFAULT_EXTENSION_POLICY_ID,
        "warnings": sorted(warnings, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
    }


def _find_extension_value(extensions: Mapping[str, object] | None, key: str) -> Tuple[bool, object]:
    normalized = normalize_extensions_map(extensions)
    if key in normalized:
        return True, normalized.get(key)
    key_state, canonical_key = _key_classification(key)
    if key_state == "legacy_bare" and key in normalized:
        return True, normalized.get(key)
    if canonical_key and canonical_key in normalized:
        return True, normalized.get(canonical_key)
    if key_state == "namespaced":
        tail = key.split(".")[-1]
        if tail in normalized:
            return True, normalized.get(tail)
    return False, None


def extensions_get(
    *,
    repo_root: str,
    owner_schema_id: str,
    extensions: Mapping[str, object] | None,
    key: str,
    registry_payload: Mapping[str, object] | None = None,
    policy_mode: str = DEFAULT_EXTENSION_POLICY_ID,
    active_profile_gate_ids: Sequence[str] | None = None,
    default: object = None,
) -> object:
    registry = _as_map(registry_payload)
    if not registry:
        registry, _error = load_extension_interpretation_registry(repo_root)
    rows = normalize_extension_interpretation_rows(registry)
    key_token = str(key or "").strip()
    if not key_token:
        return default
    key_state, canonical_key = _key_classification(key_token)
    row = rows.get(key_token) or rows.get(canonical_key)
    if not row:
        return default

    allowed_owners = _sorted_tokens(row.get("allowed_owners") or ["*"])
    owner_token = str(owner_schema_id or "").strip() or "*"
    if "*" not in allowed_owners and owner_token not in allowed_owners:
        return default

    required_gate = str(row.get("profile_gate_required", DEFAULT_EXTENSION_POLICY_ID)).strip() or DEFAULT_EXTENSION_POLICY_ID
    active_gates = set(_sorted_tokens(active_profile_gate_ids or []))
    if active_gates and required_gate not in active_gates and required_gate != DEFAULT_EXTENSION_POLICY_ID:
        return default

    found, value = _find_extension_value(extensions, key_token if key_state != "legacy_bare" else key_token)
    if found:
        return value
    found, value = _find_extension_value(extensions, canonical_key or key_token)
    return value if found else default


__all__ = [
    "DEFAULT_EXTENSION_POLICY_ID",
    "WARN_EXTENSION_POLICY_ID",
    "STRICT_EXTENSION_POLICY_ID",
    "EXTENSION_INTERPRETATION_REGISTRY_REL",
    "legacy_alias_for_key",
    "load_extension_interpretation_registry",
    "normalize_extension_interpretation_rows",
    "extension_interpretation_registry_hash",
    "normalize_extensions_map",
    "normalize_extensions_tree",
    "validate_extensions_map",
    "validate_extensions_tree",
    "extensions_get",
]
