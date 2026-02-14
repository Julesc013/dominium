"""Deterministic non-blocking execution ledger for XStack runs."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, Iterable, List

from .artifact_contract import classify_paths


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _ledger_root(repo_root: str, cache_root: str = "") -> str:
    root = cache_root or os.path.join(repo_root, ".xstack_cache")
    return os.path.join(root, "ledger")


def canonical_artifact_hashes(repo_root: str, artifact_paths: Iterable[str]) -> Dict[str, str]:
    normalized = sorted(set(_norm(str(item)) for item in artifact_paths if str(item).strip()))
    classified = classify_paths(repo_root, normalized)
    out: Dict[str, str] = {}
    for rel in sorted(classified.get("CANONICAL") or []):
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        out[rel] = _sha256_file(abs_path)
    return out


def build_entry(
    repo_state_hash: str,
    plan_hash: str,
    profile: str,
    runner_ids: Iterable[str],
    cache_hits: int,
    cache_misses: int,
    artifact_hashes: Dict[str, str],
    failure_class: str,
    duration_s: float,
    workspace_id: str,
) -> Dict[str, object]:
    payload = {
        "schema_version": "1.0.0",
        "repo_state_hash": str(repo_state_hash or ""),
        "plan_hash": str(plan_hash or ""),
        "profile": str(profile or ""),
        "runner_ids_executed": sorted(set(str(item).strip() for item in runner_ids if str(item).strip())),
        "cache_hits": int(cache_hits),
        "cache_misses": int(cache_misses),
        "artifact_hashes": {str(key): str(value) for key, value in sorted((artifact_hashes or {}).items())},
        "failure_class": str(failure_class or ""),
        "duration_s": float(max(0.0, duration_s)),
        "workspace_id": str(workspace_id or ""),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["entry_hash"] = _sha256_text(canonical)
    return payload


def append_entry(repo_root: str, entry: Dict[str, object], cache_root: str = "") -> Dict[str, str]:
    """Persist a ledger entry and return metadata; never raises."""

    try:
        root = _ledger_root(repo_root, cache_root=cache_root)
        os.makedirs(root, exist_ok=True)
        entry_hash = str(entry.get("entry_hash", "")).strip()
        if not entry_hash:
            canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
            entry_hash = _sha256_text(canonical)
            entry = dict(entry)
            entry["entry_hash"] = entry_hash
        out_path = os.path.join(root, "{}.json".format(entry_hash))
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(entry, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return {
            "entry_hash": entry_hash,
            "entry_path": out_path,
        }
    except Exception:
        return {}


def load_entries(repo_root: str, cache_root: str = "") -> List[Dict[str, object]]:
    root = _ledger_root(repo_root, cache_root=cache_root)
    if not os.path.isdir(root):
        return []
    entries: List[Dict[str, object]] = []
    for name in sorted(os.listdir(root)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(root, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    entries.sort(key=lambda row: str(row.get("entry_hash", "")))
    return entries


def export_snapshot_markdown(
    repo_root: str,
    out_path: str,
    cache_root: str = "",
    max_rows: int = 20,
) -> str:
    """Export deterministic ledger summary markdown for snapshot mode."""

    entries = load_entries(repo_root, cache_root=cache_root)
    rows = entries[-int(max(1, max_rows)) :]
    parent = os.path.dirname(out_path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: 2026-02-14\n")
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# Execution Ledger Snapshot\n\n")
        handle.write("- entry_count: `{}`\n".format(len(entries)))
        handle.write("- rendered_entries: `{}`\n".format(len(rows)))
        handle.write("\n## Entries\n\n")
        if not rows:
            handle.write("- none\n")
        for row in rows:
            handle.write("- entry_hash: `{}`\n".format(str(row.get("entry_hash", ""))))
            handle.write("  - plan_hash: `{}`\n".format(str(row.get("plan_hash", ""))))
            handle.write("  - profile: `{}`\n".format(str(row.get("profile", ""))))
            handle.write("  - workspace_id: `{}`\n".format(str(row.get("workspace_id", ""))))
            handle.write("  - cache_hits: `{}`\n".format(int(row.get("cache_hits", 0))))
            handle.write("  - cache_misses: `{}`\n".format(int(row.get("cache_misses", 0))))
            handle.write("  - failure_class: `{}`\n".format(str(row.get("failure_class", "")) or "none"))
    return out_path
