"""Deterministic JSON serialization and hashing helpers for schema artifacts."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_text(value: Any) -> str:
    """Return canonical JSON text with stable key ordering and compact separators."""
    return json.dumps(
        value,
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

