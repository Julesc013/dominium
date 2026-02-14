"""Content-addressed cache helpers for PerformX."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict


def cache_root(repo_root: str, workspace_id: str = "") -> str:
    ws_id = str(workspace_id or "").strip() or "default"
    return os.path.join(repo_root, ".xstack_cache", ws_id, "performx", "cache")


def build_cache_key(context: Dict[str, Any]) -> str:
    blob = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def load_cache(repo_root: str, cache_key: str, workspace_id: str = "") -> Dict[str, Any] | None:
    path = os.path.join(cache_root(repo_root, workspace_id=workspace_id), "{}.json".format(cache_key))
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def write_cache(repo_root: str, cache_key: str, payload: Dict[str, Any], workspace_id: str = "") -> str:
    root = cache_root(repo_root, workspace_id=workspace_id)
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, "{}.json".format(cache_key))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
