"""Shared deterministic helpers for SessionSpec creator and boot tooling."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Tuple

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_COMPATIBILITY_VERSION = "1.0.0"
DEFAULT_TIMESTAMP_UTC = "1970-01-01T00:00:00Z"


def norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def read_json_object(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def write_canonical_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def now_utc_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def identity_hash_for_payload(payload: Dict[str, object]) -> str:
    body = dict(payload)
    body["identity_hash"] = ""
    return canonical_sha256(body)


def deterministic_seed_hex(seed_text: str, salt: str) -> str:
    token = "{}|{}".format(str(seed_text), str(salt))
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refusal(
    reason_code: str,
    message: str,
    remediation_hint: str,
    relevant_ids: Dict[str, str] | None = None,
    path: str = "$",
) -> Dict[str, object]:
    ids = {}
    for key, value in sorted((relevant_ids or {}).items(), key=lambda row: str(row[0])):
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

