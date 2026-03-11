"""Lightweight deterministic AppShell config/profile listing helpers."""

from __future__ import annotations

import json
import os
from typing import List, Tuple


def resolve_repo_root(repo_root: str, repo_root_hint: str = ".") -> str:
    token = str(repo_root or "").strip()
    if token and token not in {".", "./"}:
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(repo_root_hint or "."))


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def list_profile_bundles(repo_root: str) -> List[dict]:
    out: List[dict] = []
    roots = (
        os.path.join(repo_root, "profiles", "bundles"),
        os.path.join(repo_root, "dist", "profiles"),
    )
    seen = set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(entry for entry in os.listdir(root) if entry.endswith(".json")):
            path = os.path.join(root, name)
            payload, error = _read_json(path)
            if error:
                continue
            bundle_id = str(payload.get("bundle_id", "")).strip() or str(payload.get("profile_bundle_id", "")).strip()
            if not bundle_id or bundle_id in seen:
                continue
            seen.add(bundle_id)
            out.append(
                {
                    "bundle_id": bundle_id,
                    "path": os.path.relpath(path, repo_root).replace("\\", "/"),
                    "profile_bundle_hash": str(payload.get("profile_bundle_hash", "")).strip(),
                }
            )
    return sorted(out, key=lambda item: item["bundle_id"])


def list_pack_manifests(repo_root: str, root: str = "") -> List[dict]:
    base = os.path.join(repo_root, str(root).strip()) if str(root).strip() else os.path.join(repo_root, "packs")
    base = os.path.normpath(os.path.abspath(base))
    out: List[dict] = []
    seen = set()
    if not os.path.isdir(base):
        return []
    for dirpath, _dirnames, filenames in os.walk(base):
        if "pack.json" not in filenames:
            continue
        manifest_path = os.path.join(dirpath, "pack.json")
        payload, error = _read_json(manifest_path)
        if error:
            continue
        pack_id = str(payload.get("pack_id", "")).strip()
        version = str(payload.get("version", "")).strip()
        key = (pack_id, version)
        if not pack_id or key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "pack_id": pack_id,
                "pack_version": version,
                "path": os.path.relpath(manifest_path, repo_root).replace("\\", "/"),
            }
        )
    return sorted(out, key=lambda item: (item["pack_id"], item["pack_version"]))


__all__ = ["list_pack_manifests", "list_profile_bundles", "resolve_repo_root"]
