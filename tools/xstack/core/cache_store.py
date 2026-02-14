"""Content-addressed execution cache for XStack runners."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Callable, Dict, List

from .profiler import end_phase, start_phase


def _cache_root(repo_root: str, cache_root: str = "") -> str:
    root = cache_root or os.path.join(repo_root, ".xstack_cache")
    if not os.path.isdir(root):
        os.makedirs(root, exist_ok=True)
    return root


def _hash_key(runner_id: str, input_hash: str, profile_id: str, version_hash: str = "") -> str:
    payload = "{}|{}|{}|{}".format(runner_id, input_hash, profile_id, version_hash)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _entry_hash(payload: Dict[str, object]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    version_hash: str = "",
    tool_version: str = "",
    cache_root: str = "",
) -> Dict[str, object]:
    phase = "cache.lookup.{}".format(runner_id)
    start_phase(phase)
    version = str(version_hash or tool_version or "")
    key = _hash_key(runner_id, input_hash, profile_id, version_hash=version)
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
    if str(payload.get("runner_id", "")).strip() != str(runner_id).strip():
        end_phase(phase, {"cache_hit": False, "error": "runner_mismatch"})
        return {}
    if str(payload.get("input_hash", "")).strip() != str(input_hash).strip():
        end_phase(phase, {"cache_hit": False, "error": "input_hash_mismatch"})
        return {}
    if str(payload.get("profile_id", "")).strip() != str(profile_id).strip():
        end_phase(phase, {"cache_hit": False, "error": "profile_mismatch"})
        return {}
    payload_version = str(payload.get("version_hash", "") or payload.get("tool_version", "")).strip()
    if payload_version != version:
        end_phase(phase, {"cache_hit": False, "error": "version_hash_mismatch"})
        return {}
    key_hash = str(payload.get("key_hash", "")).strip()
    if key_hash != key:
        end_phase(phase, {"cache_hit": False, "error": "key_hash_mismatch"})
        return {}
    payload_core = dict(payload)
    payload_entry_hash = str(payload_core.pop("entry_hash", "")).strip()
    if payload_entry_hash != _entry_hash(payload_core):
        end_phase(phase, {"cache_hit": False, "error": "entry_hash_mismatch"})
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
    version_hash: str = "",
    tool_version: str = "",
    failure_class: str = "",
    failure_message: str = "",
    remediation_hint: str = "",
    cache_root: str = "",
) -> str:
    phase = "cache.store.{}".format(runner_id)
    start_phase(phase)
    version = str(version_hash or tool_version or "")
    key = _hash_key(runner_id, input_hash, profile_id, version_hash=version)
    path = _entry_path(repo_root, runner_id, key, cache_root=cache_root)
    payload = {
        "runner_id": runner_id,
        "input_hash": input_hash,
        "profile_id": profile_id,
        "version_hash": version,
        "tool_version": version,
        "key_hash": key,
        "output_hash": output_hash,
        "exit_code": int(exit_code),
        "output": str(output or ""),
        "failure_class": str(failure_class or ""),
        "failure_message": str(failure_message or ""),
        "remediation_hint": str(remediation_hint or ""),
        "artifacts_produced": sorted(set(str(item) for item in (artifacts_produced or []) if str(item).strip())),
        "timestamp_utc": timestamp_utc,
    }
    payload["entry_hash"] = _entry_hash(payload)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    end_phase(phase)
    return path


def scan_cache(
    repo_root: str,
    cache_root: str = "",
    version_resolver: Callable[[str], str] | None = None,
) -> Dict[str, object]:
    root = _cache_root(repo_root, cache_root=cache_root)
    skipped_roots = {"plans", "merkle", "ledger", "artifacts", "xstack", "gate"}
    corrupt_entries: List[dict] = []
    orphaned_entries: List[str] = []
    stale_groups = set()
    entries_scanned = 0
    known_groups = 0

    for name in sorted(os.listdir(root)):
        abs_path = os.path.join(root, name)
        if not os.path.isdir(abs_path):
            continue
        if name in skipped_roots:
            continue
        expected_version = str(version_resolver(name) if version_resolver else "").strip()
        if expected_version:
            known_groups += 1
        for entry_name in sorted(os.listdir(abs_path)):
            entry_path = os.path.join(abs_path, entry_name)
            rel = os.path.relpath(entry_path, root).replace("\\", "/")
            if not os.path.isfile(entry_path):
                continue
            if not entry_name.endswith(".json"):
                orphaned_entries.append(rel)
                continue
            entries_scanned += 1
            try:
                with open(entry_path, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)
            except (OSError, ValueError):
                corrupt_entries.append({"path": rel, "error": "read_error"})
                continue
            if not isinstance(payload, dict):
                corrupt_entries.append({"path": rel, "error": "invalid_payload"})
                continue
            required = ("runner_id", "input_hash", "profile_id", "version_hash", "key_hash", "entry_hash")
            missing = [key for key in required if not str(payload.get(key, "")).strip()]
            if missing:
                corrupt_entries.append({"path": rel, "error": "missing_fields", "fields": missing})
                continue
            runner_id = str(payload.get("runner_id", "")).strip()
            input_hash = str(payload.get("input_hash", "")).strip()
            profile_id = str(payload.get("profile_id", "")).strip()
            version_hash = str(payload.get("version_hash", "")).strip()
            expected_key = _hash_key(runner_id, input_hash, profile_id, version_hash=version_hash)
            if expected_key != os.path.splitext(entry_name)[0] or expected_key != str(payload.get("key_hash", "")).strip():
                corrupt_entries.append({"path": rel, "error": "key_hash_mismatch"})
                continue
            payload_core = dict(payload)
            current_hash = str(payload_core.pop("entry_hash", "")).strip()
            if current_hash != _entry_hash(payload_core):
                corrupt_entries.append({"path": rel, "error": "entry_hash_mismatch"})
                continue
            if expected_version and version_hash != expected_version:
                stale_groups.add(name)
        if not expected_version:
            for entry_name in sorted(os.listdir(abs_path)):
                entry_path = os.path.join(abs_path, entry_name)
                if os.path.isfile(entry_path):
                    orphaned_entries.append(os.path.relpath(entry_path, root).replace("\\", "/"))

    report = {
        "cache_root": os.path.relpath(root, repo_root).replace("\\", "/"),
        "entries_scanned": int(entries_scanned),
        "known_groups": int(known_groups),
        "corrupt_entries": sorted(corrupt_entries, key=lambda row: (str(row.get("path", "")), str(row.get("error", "")))),
        "orphaned_entries": sorted(set(orphaned_entries)),
        "stale_groups": sorted(stale_groups),
    }
    report["ok"] = not bool(report["corrupt_entries"] or report["orphaned_entries"] or report["stale_groups"])
    return report
