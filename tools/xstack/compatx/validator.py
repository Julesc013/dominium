"""Deterministic strict schema validation for canonical v1 JSON contracts."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Tuple

from .canonical_json import canonical_sha256
from .schema_registry import load_schema, load_version_registry, normalize_schema_name
from .versioning import resolve_payload_version


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _error(code: str, path: str, message: str) -> Dict[str, str]:
    return {"code": str(code), "path": str(path), "message": str(message)}


def _as_type_list(raw: Any) -> List[str]:
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        out: List[str] = []
        for item in raw:
            if isinstance(item, str) and item:
                out.append(item)
        return out
    return []


def _child_path(parent: str, key: str) -> str:
    if parent == "$":
        return "$.{}".format(key)
    return "{}.{}".format(parent, key)


def _validate_node(
    schema_node: Dict[str, Any],
    value: Any,
    path: str,
    errors: List[Dict[str, str]],
    strict_top_level: bool,
) -> None:
    expected_types = _as_type_list(schema_node.get("type"))
    if expected_types and not any(_matches_type(value, token) for token in expected_types):
        errors.append(
            _error(
                "type_mismatch",
                path,
                "expected type {} but found {}".format("|".join(expected_types), _type_name(value)),
            )
        )
        return

    if "const" in schema_node and value != schema_node.get("const"):
        errors.append(
            _error(
                "const_mismatch",
                path,
                "expected const {} but found {}".format(repr(schema_node.get("const")), repr(value)),
            )
        )

    enum_values = schema_node.get("enum")
    if isinstance(enum_values, list) and enum_values and value not in enum_values:
        errors.append(
            _error(
                "enum_mismatch",
                path,
                "value {} not in enum {}".format(repr(value), repr(enum_values)),
            )
        )

    pattern = schema_node.get("pattern")
    if isinstance(pattern, str) and isinstance(value, str):
        try:
            matched = re.fullmatch(pattern, value)
        except re.error:
            matched = None
        if matched is None:
            errors.append(_error("pattern_mismatch", path, "value does not match pattern {}".format(repr(pattern))))

    if isinstance(value, dict):
        properties = schema_node.get("properties")
        if not isinstance(properties, dict):
            properties = {}

        required = schema_node.get("required")
        required_fields = sorted(set(str(item) for item in required if isinstance(item, str))) if isinstance(required, list) else []
        for field in required_fields:
            if field not in value:
                errors.append(
                    _error(
                        "required_missing",
                        _child_path(path, field),
                        "missing required field '{}'".format(field),
                    )
                )

        additional = schema_node.get("additionalProperties", True)
        for field in sorted(value.keys(), key=lambda token: str(token)):
            key = str(field)
            subpath = _child_path(path, key)
            if key in properties:
                child_schema = properties.get(key)
                if isinstance(child_schema, dict):
                    _validate_node(child_schema, value.get(key), subpath, errors, strict_top_level)
                continue

            if path == "$" and strict_top_level:
                errors.append(_error("unknown_top_level_field", subpath, "unknown top-level field '{}'".format(key)))
                continue
            if additional is False:
                errors.append(_error("unknown_field", subpath, "unknown field '{}'".format(key)))
                continue
            if isinstance(additional, dict):
                _validate_node(additional, value.get(key), subpath, errors, strict_top_level)

    if isinstance(value, list):
        items = schema_node.get("items")
        if isinstance(items, dict):
            for idx, item in enumerate(value):
                _validate_node(items, item, "{}[{}]".format(path, idx), errors, strict_top_level)


def _schema_registry_entry(version_registry: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    schemas = version_registry.get("schemas")
    if not isinstance(schemas, dict):
        return {}
    row = schemas.get(schema_name)
    return row if isinstance(row, dict) else {}


def _version_field_name(schema: Dict[str, Any]) -> str:
    required = schema.get("required")
    properties = schema.get("properties")
    required_fields = set(str(item) for item in required if isinstance(item, str)) if isinstance(required, list) else set()
    property_fields = set(str(key) for key in properties.keys()) if isinstance(properties, dict) else set()
    for key in ("schema_version", "format_version", "lockfile_version"):
        if key in required_fields or key in property_fields:
            return key
    return "schema_version"


def _deterministic_errors(errors: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return sorted(
        errors,
        key=lambda row: (
            str(row.get("path", "")),
            str(row.get("code", "")),
            str(row.get("message", "")),
        ),
    )


def validate_instance(
    repo_root: str,
    schema_name: str,
    payload: Any,
    strict_top_level: bool = True,
) -> Dict[str, Any]:
    key = normalize_schema_name(schema_name)
    schema, schema_path, schema_error = load_schema(repo_root, key)
    version_registry, version_registry_error = load_version_registry(repo_root)

    errors: List[Dict[str, str]] = []
    if schema_error:
        errors.append(_error("schema_load_error", "$", schema_error))
    if version_registry_error:
        errors.append(_error("version_registry_error", "$", version_registry_error))

    schema_version = str(schema.get("version", "")).strip() if isinstance(schema, dict) else ""
    entry = _schema_registry_entry(version_registry, key) if isinstance(version_registry, dict) else {}
    current_version = str(entry.get("current_version", "")).strip()
    supported_versions = entry.get("supported_versions", []) if isinstance(entry, dict) else []

    if not entry:
        errors.append(_error("missing_registry_entry", "$", "missing schema entry in version registry for '{}'".format(key)))
    if not schema_version:
        errors.append(_error("missing_schema_version", "$", "schema file missing required top-level 'version'"))
    if schema_version and current_version and schema_version != current_version:
        errors.append(
            _error(
                "schema_registry_mismatch",
                "$",
                "schema file version '{}' does not match registry current '{}'".format(schema_version, current_version),
            )
        )

    payload_version = ""
    version_field = _version_field_name(schema) if isinstance(schema, dict) else "schema_version"
    if isinstance(payload, dict):
        payload_version = str(payload.get(version_field, "")).strip()

    if current_version:
        version_result = resolve_payload_version(
            schema_name=key,
            payload_version=payload_version,
            current_version=current_version,
            supported_versions=supported_versions if isinstance(supported_versions, list) else [],
            version_field=version_field,
        )
        if not bool(version_result.get("ok", False)):
            errors.append(
                _error(
                    str(version_result.get("refusal_code", "version_mismatch")),
                    "$.{}".format(version_field),
                    str(version_result.get("message", "schema version resolution failed")),
                )
            )

    if isinstance(schema, dict):
        _validate_node(schema, payload, "$", errors, strict_top_level=bool(strict_top_level))

    deterministic_errors = _deterministic_errors(errors)
    payload_hash = canonical_sha256(payload)
    return {
        "schema_name": key,
        "schema_file": _norm(os.path.relpath(schema_path, repo_root)) if schema_path else "",
        "schema_version": schema_version,
        "payload_hash": payload_hash,
        "valid": len(deterministic_errors) == 0,
        "errors": deterministic_errors,
    }


def validate_schema_example(repo_root: str, schema_name: str) -> Dict[str, Any]:
    schema, _path, schema_error = load_schema(repo_root, schema_name)
    if schema_error:
        return {
            "schema_name": normalize_schema_name(schema_name),
            "valid": False,
            "errors": [_error("schema_load_error", "$", schema_error)],
        }
    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        return {
            "schema_name": normalize_schema_name(schema_name),
            "valid": False,
            "errors": [_error("missing_examples", "$", "schema must define at least one example object")],
        }
    return validate_instance(repo_root=repo_root, schema_name=schema_name, payload=examples[0], strict_top_level=True)
