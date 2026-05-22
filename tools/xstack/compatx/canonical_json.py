"""Compatibility wrapper for engine-owned deterministic JSON helpers."""

from __future__ import annotations

from typing import Any

from engine.serialization.canonical_json import (
    canonical_json_bytes as _engine_canonical_json_bytes,
    canonical_json_text as _engine_canonical_json_text,
    canonical_sha256 as _engine_canonical_sha256,
)
from engine.foundation.meta.extensions.core import normalize_extensions_tree


def canonical_json_text(value: Any) -> str:
    return _engine_canonical_json_text(normalize_extensions_tree(value))


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_text(value).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return _engine_canonical_sha256(normalize_extensions_tree(value))

__all__ = ["canonical_json_bytes", "canonical_json_text", "canonical_sha256"]
