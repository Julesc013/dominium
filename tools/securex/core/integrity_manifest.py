"""Integrity manifest generation helpers."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Iterable, List


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _entry(item_id: str, path: str, repo_root: str) -> Dict[str, str]:
    rel = os.path.relpath(path, repo_root).replace("\\", "/")
    return {
        "id": str(item_id).strip(),
        "sha256": _sha256_file(path),
        "source": rel,
    }


def _collect(entries: Iterable[tuple[str, str]], repo_root: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for item_id, path in entries:
        norm = os.path.normpath(path)
        if not os.path.isfile(norm):
            continue
        out.append(_entry(item_id, norm, repo_root))
    out.sort(key=lambda row: (row["id"], row["source"]))
    return out


def _load_identity_hash(identity_path: str) -> str:
    if not os.path.isfile(identity_path):
        return ""
    try:
        with open(identity_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return ""
    if not isinstance(payload, dict):
        return ""
    value = str(payload.get("fingerprint_sha256", "")).strip().lower()
    return value


def generate_manifest(
    repo_root: str,
    schema_files: Iterable[tuple[str, str]],
    pack_files: Iterable[tuple[str, str]],
    tool_files: Iterable[tuple[str, str]],
    canonical_artifacts: Iterable[tuple[str, str]],
    identity_path: str,
) -> Dict[str, Any]:
    identity_hash = _load_identity_hash(identity_path)
    return {
        "artifact_class": "CANONICAL",
        "schema_id": "dominium.schema.governance.integrity_manifest",  # schema_version: 1.0.0
        "schema_version": "1.0.0",
        "record": {
            "manifest_id": "securex.integrity_manifest",
            "manifest_version": "1.0.0",
            "schema_version_ref": "dominium.schema.governance.integrity_manifest@1.0.0",
            "identity_fingerprint_sha256": identity_hash,
            "schema_hashes": _collect(schema_files, repo_root),
            "pack_hashes": _collect(pack_files, repo_root),
            "tool_hashes": _collect(tool_files, repo_root),
            "canonical_artifact_hashes": _collect(canonical_artifacts, repo_root),
            "extensions": {},
        },
    }


def write_manifest(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
