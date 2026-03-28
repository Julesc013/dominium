"""Shared deterministic observability contract helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
OBSERVABILITY_GUARANTEE_REGISTRY_REL = os.path.join("data", "registries", "observability_guarantee_registry.json")
LOG_CATEGORY_REGISTRY_REL = os.path.join("data", "registries", "log_category_registry.json")
LOG_MESSAGE_KEY_REGISTRY_REL = os.path.join("data", "registries", "log_message_key_registry.json")
REDACTION_PLACEHOLDER = "[redacted]"
SECRET_KEY_FRAGMENTS = (
    "account_secret",
    "auth_token",
    "credential",
    "email",
    "machine_id",
    "password",
    "private_key",
    "secret",
    "signing_key",
    "token",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _repo_root(repo_root: str = "") -> str:
    token = _token(repo_root)
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


@lru_cache(maxsize=8)
def load_observability_guarantee_registry(repo_root: str = "") -> dict:
    root = _repo_root(repo_root)
    return _read_json(os.path.join(root, OBSERVABILITY_GUARANTEE_REGISTRY_REL))


@lru_cache(maxsize=8)
def load_log_category_registry(repo_root: str = "") -> dict:
    root = _repo_root(repo_root)
    return _read_json(os.path.join(root, LOG_CATEGORY_REGISTRY_REL))


@lru_cache(maxsize=8)
def load_log_message_key_registry(repo_root: str = "") -> dict:
    root = _repo_root(repo_root)
    return _read_json(os.path.join(root, LOG_MESSAGE_KEY_REGISTRY_REL))


def _secret_key(key: str) -> bool:
    lowered = _token(key).lower()
    return bool(lowered) and any(fragment in lowered for fragment in SECRET_KEY_FRAGMENTS)


def _redact_tree(value: object) -> tuple[object, int]:
    if isinstance(value, Mapping):
        sanitized = {}
        redaction_count = 0
        for raw_key, raw_item in sorted(value.items(), key=lambda pair: str(pair[0])):
            key = str(raw_key)
            if _secret_key(key):
                sanitized[key] = REDACTION_PLACEHOLDER
                redaction_count += 1
                continue
            sanitized_value, nested_count = _redact_tree(raw_item)
            sanitized[key] = sanitized_value
            redaction_count += int(nested_count)
        return sanitized, redaction_count
    if isinstance(value, list):
        rows = []
        redaction_count = 0
        for item in value:
            sanitized_value, nested_count = _redact_tree(item)
            rows.append(sanitized_value)
            redaction_count += int(nested_count)
        return rows, redaction_count
    if isinstance(value, tuple):
        rows = []
        redaction_count = 0
        for item in value:
            sanitized_value, nested_count = _redact_tree(item)
            rows.append(sanitized_value)
            redaction_count += int(nested_count)
        return rows, redaction_count
    return value, 0


def redact_observability_mapping(payload: Mapping[str, object] | None) -> tuple[dict, int]:
    sanitized, redaction_count = _redact_tree(dict(payload or {}))
    return dict(sanitized or {}), int(redaction_count)


def _field_exists(payload: Mapping[str, object], field_path: str) -> bool:
    current: object = payload
    for token in [segment for segment in _token(field_path).split(".") if segment]:
        if not isinstance(current, Mapping):
            return False
        if token not in current:
            return False
        current = current[token]
    if current is None:
        return False
    if isinstance(current, str):
        return bool(current.strip())
    if isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
        return bool(list(current))
    if isinstance(current, Mapping):
        return bool(dict(current))
    return True


def _guarantee_rows(repo_root: str = "") -> dict[str, dict]:
    payload = load_observability_guarantee_registry(repo_root)
    rows = {}
    for row in list(dict(payload.get("record") or {}).get("guarantees") or []):
        if not isinstance(row, Mapping):
            continue
        category_id = _token(dict(row).get("category_id"))
        if category_id:
            rows[category_id] = dict(row)
    return rows


def _category_rows(repo_root: str = "") -> dict[str, dict]:
    payload = load_log_category_registry(repo_root)
    rows = {}
    for row in list(dict(payload.get("record") or {}).get("categories") or []):
        if not isinstance(row, Mapping):
            continue
        category_id = _token(dict(row).get("category_id"))
        if category_id:
            rows[category_id] = dict(row)
    return rows


def _message_key_rows(repo_root: str = "") -> dict[str, dict]:
    payload = load_log_message_key_registry(repo_root)
    rows = {}
    for row in list(dict(payload.get("record") or {}).get("messages") or []):
        if not isinstance(row, Mapping):
            continue
        message_key = _token(dict(row).get("message_key"))
        if message_key:
            rows[message_key] = dict(row)
    return rows


def validate_observability_event(payload: Mapping[str, object] | None, *, repo_root: str = "") -> dict:
    row = dict(payload or {})
    category_id = _token(row.get("category"))
    message_key = _token(row.get("message_key"))
    guarantee_row = dict(_guarantee_rows(repo_root).get(category_id) or {})
    category_row = dict(_category_rows(repo_root).get(category_id) or {})
    message_row = dict(_message_key_rows(repo_root).get(message_key) or {})
    guaranteed = bool(guarantee_row) and bool(guarantee_row.get("guaranteed", False))
    warnings: list[dict] = []
    errors: list[dict] = []

    if guaranteed and not category_row:
        errors.append(
            {
                "code": "observability.category_missing",
                "message": "guaranteed category '{}' is not declared in the log category registry".format(category_id),
                "field_path": "category",
            }
        )
    if guaranteed and not message_row:
        errors.append(
            {
                "code": "observability.message_key_missing",
                "message": "guaranteed category '{}' emitted an undeclared message key '{}'".format(category_id, message_key),
                "field_path": "message_key",
            }
        )
    expected_category_id = _token(message_row.get("category_id"))
    if guaranteed and expected_category_id and expected_category_id != category_id:
        errors.append(
            {
                "code": "observability.category_mismatch",
                "message": "message key '{}' is declared for category '{}' but event emitted '{}'".format(message_key, expected_category_id, category_id),
                "field_path": "category",
            }
        )
    for field_path in list(guarantee_row.get("minimum_fields") or []):
        field_token = _token(field_path)
        if not field_token:
            continue
        if _field_exists(row, field_token):
            continue
        errors.append(
            {
                "code": "observability.required_field_missing",
                "message": "guaranteed category '{}' requires '{}'".format(category_id, field_token),
                "field_path": field_token,
            }
        )
    if not guaranteed and category_id and dict(_guarantee_rows(repo_root)).get(category_id):
        warnings.append(
            {
                "code": "observability.category_not_guaranteed",
                "message": "category '{}' is declared but not guaranteed".format(category_id),
                "field_path": "category",
            }
        )
    return {
        "category_id": category_id,
        "message_key": message_key,
        "guaranteed": guaranteed,
        "warnings": warnings,
        "errors": errors,
    }


def filter_log_events(
    rows: Sequence[Mapping[str, object]] | None,
    *,
    category_id: str = "",
    severity: str = "",
    session_id: str = "",
    connection_id: str = "",
) -> list[dict]:
    category_token = _token(category_id)
    severity_token = _token(severity).lower()
    session_token = _token(session_id)
    connection_token = _token(connection_id)
    filtered = []
    for raw_row in list(rows or []):
        if not isinstance(raw_row, Mapping):
            continue
        row = dict(raw_row)
        if category_token and _token(row.get("category")) != category_token:
            continue
        if severity_token and _token(row.get("severity")).lower() != severity_token:
            continue
        if session_token and _token(row.get("session_id")) != session_token:
            continue
        if connection_token and _token(dict(row.get("params") or {}).get("connection_id")) != connection_token:
            continue
        filtered.append(row)
    return sorted(
        filtered,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            _token(row.get("session_id")),
            _token(row.get("category")),
            _token(row.get("severity")),
            _token(row.get("event_id")),
            _token(row.get("deterministic_fingerprint")),
        ),
    )


__all__ = [
    "LOG_CATEGORY_REGISTRY_REL",
    "LOG_MESSAGE_KEY_REGISTRY_REL",
    "OBSERVABILITY_GUARANTEE_REGISTRY_REL",
    "REDACTION_PLACEHOLDER",
    "SECRET_KEY_FRAGMENTS",
    "filter_log_events",
    "load_log_category_registry",
    "load_log_message_key_registry",
    "load_observability_guarantee_registry",
    "redact_observability_mapping",
    "validate_observability_event",
]
