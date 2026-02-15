"""Deterministic I/O and hashing helpers for ControlX."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from typing import Any


def norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def write_json(path: str, payload: Any) -> None:
    parent = os.path.dirname(path)
    if parent:
        ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def now_utc_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

