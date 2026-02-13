"""Content-addressed execution cache for XStack runners."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List

from .profiler import end_phase, start_phase


def _cache_root(repo_root: str, cache_root: str = "") -> str:
    root = cache_root or os.path.join(repo_root, ".xstack_cache")
    if not os.path.isdir(root):
        os.makedirs(root, exist_ok=True)
    return root


def _hash_key(runner_id: str, input_hash: str, profile_id: str, tool_version: str = "") -> str:
    payload = "{}|{}|{}|{}".format(runner_id, input_hash, profile_id, tool_version)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _entry_path(repo_root: str, runner_id: str, key_hash: str, cache_root: str = "") -> str:
    root = _cache_root(repo_root, cache_root=cache_root)
    folder = os.path.join(root, runner_id)
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, key_hash + ".json")


def load_entry(
    repo_root: str,
    runner_id: str,
    input_hash: str,
    profile_id: str,
    tool_version: str = "",
    cache_root: str = "",
) -> Dict[str, object]:
    phase = "cache.lookup.{}".format(runner_id)
    start_phase(phase)
    key = _hash_key(runner_id, input_hash, profile_id, tool_version=tool_version)
    path = _entry_path(repo_root, runner_id, key, cache_root=cache_root)
    if not os.path.isfile(path):
        end_phase(phase, {"cache_hit": False})
        return {}
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        end_phase(phase, {"cache_hit": False, "error": "read_error"})
        return {}
    if not isinstance(payload, dict):
        end_phase(phase, {"cache_hit": False, "error": "invalid_payload"})
        return {}
    if str(payload.get("input_hash", "")).strip() != str(input_hash).strip():
        end_phase(phase, {"cache_hit": False, "error": "input_hash_mismatch"})
        return {}
    if str(payload.get("profile_id", "")).strip() != str(profile_id).strip():
        end_phase(phase, {"cache_hit": False, "error": "profile_mismatch"})
        return {}
    end_phase(phase, {"cache_hit": True})
    return payload


def store_entry(
    repo_root: str,
    runner_id: str,
    input_hash: str,
    profile_id: str,
    exit_code: int,
    output_hash: str,
    artifacts_produced: List[str],
    timestamp_utc: str,
    output: str = "",
    tool_version: str = "",
    cache_root: str = "",
) -> str:
    phase = "cache.store.{}".format(runner_id)
    start_phase(phase)
    key = _hash_key(runner_id, input_hash, profile_id, tool_version=tool_version)
    path = _entry_path(repo_root, runner_id, key, cache_root=cache_root)
    payload = {
        "runner_id": runner_id,
        "input_hash": input_hash,
        "profile_id": profile_id,
        "tool_version": tool_version,
        "output_hash": output_hash,
        "exit_code": int(exit_code),
        "output": str(output or ""),
        "artifacts_produced": sorted(set(str(item) for item in (artifacts_produced or []) if str(item).strip())),
        "timestamp_utc": timestamp_utc,
    }
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    end_phase(phase)
    return path
