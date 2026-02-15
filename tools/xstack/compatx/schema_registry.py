"""Schema registry loading for canonical v1 JSON schemas under schemas/."""

from __future__ import annotations

import json
import os
from typing import Dict, Tuple


SCHEMA_DIR_REL = "schemas"
VERSION_REGISTRY_REL = os.path.join("tools", "xstack", "compatx", "version_registry.json")


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _read_json(path: str) -> Tuple[dict, str]:
    if not os.path.isfile(path):
        return {}, "missing file: {}".format(_norm(path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json: {}".format(_norm(path))
    if not isinstance(payload, dict):
        return {}, "invalid object root: {}".format(_norm(path))
    return payload, ""


def discover_schema_files(repo_root: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    schema_root = os.path.join(repo_root, SCHEMA_DIR_REL)
    if not os.path.isdir(schema_root):
        return out
    for name in sorted(os.listdir(schema_root)):
        if not name.endswith(".schema.json"):
            continue
        schema_name = name[: -len(".schema.json")]
        out[schema_name] = os.path.join(schema_root, name)
    return out


def normalize_schema_name(schema_name: str) -> str:
    token = str(schema_name or "").strip()
    if token.endswith(".schema.json"):
        token = token[: -len(".schema.json")]
    return token


def load_schema(repo_root: str, schema_name: str) -> Tuple[dict, str, str]:
    files = discover_schema_files(repo_root)
    key = normalize_schema_name(schema_name)
    path = files.get(key, "")
    if not path:
        return {}, "", "unknown schema: {}".format(key)
    schema, error = _read_json(path)
    return schema, path, error


def load_version_registry(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, VERSION_REGISTRY_REL))

