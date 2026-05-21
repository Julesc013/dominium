"""Deterministic JSON serialization and hashing helpers."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _normalize_extension_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_extension_value(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_extension_value(item) for item in list(value)]
    return copy.deepcopy(value)


def _normalize_extensions_map(extensions: Mapping[str, object] | None) -> dict:
    return {
        str(key): _normalize_extension_value(value)
        for key, value in sorted(_as_map(extensions).items(), key=lambda row: str(row[0]))
    }


def _normalize_extensions_tree(value: object) -> object:
    if isinstance(value, Mapping):
        out = {}
        for key, item in sorted(dict(value).items(), key=lambda row: str(row[0])):
            token = str(key)
            if token == "extensions":
                out[token] = _normalize_extensions_map(_as_map(item))
            else:
                out[token] = _normalize_extensions_tree(item)
        return out
    if isinstance(value, list):
        return [_normalize_extensions_tree(item) for item in list(value)]
    return copy.deepcopy(value)


def canonical_json_text(value: Any) -> str:
    """Return canonical JSON text with stable key ordering and compact separators."""
    normalized = _normalize_extensions_tree(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return UTF-8 bytes for canonical JSON text."""
    return canonical_json_text(value).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    """Return SHA-256 digest for canonical JSON bytes."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


__all__ = ["canonical_json_bytes", "canonical_json_text", "canonical_sha256"]
