"""Runtime-local canonical hashing helpers for platform surfaces."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping


def canonical_json_text(payload: Mapping[str, object] | None) -> str:
    return json.dumps(
        dict(payload or {}),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_sha256(payload: Mapping[str, object] | None) -> str:
    return hashlib.sha256(canonical_json_text(payload).encode("utf-8")).hexdigest()


__all__ = ["canonical_json_text", "canonical_sha256"]
