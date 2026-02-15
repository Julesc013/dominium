"""Deterministic Merkle utilities for cache key computation."""

from __future__ import annotations

import hashlib
from typing import Iterable, List


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return _sha256_bytes(str(text).encode("utf-8"))


def merkle_root_hex(leaf_hashes: Iterable[str]) -> str:
    rows: List[str] = [str(item).strip().lower() for item in leaf_hashes if str(item).strip()]
    if not rows:
        return _sha256_bytes(b"")

    level = rows
    while len(level) > 1:
        next_level: List[str] = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else level[index]
            chunk = bytes.fromhex(left) + bytes.fromhex(right)
            next_level.append(_sha256_bytes(chunk))
        level = next_level
    return level[0]

