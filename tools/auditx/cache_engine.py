#!/usr/bin/env python3
"""Incremental cache helpers for AuditX scans."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from typing import Dict, Iterable, List, Tuple


CACHE_VERSION = "1.0.0"
CACHE_ROOT_REL = os.path.join("tools", "auditx", "cache")


def _norm(path: str) -> str:
    return os.path.normpath(path)


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _write_json(path: str, payload) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _git_head_hash(repo_root: str) -> str:
    git_cmd = shutil.which("git")
    if not git_cmd:
        return "nogit"
    proc = subprocess.run(
        [git_cmd, "-C", repo_root, "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return "nogit"
    return (proc.stdout or "").strip() or "nogit"


def _hash_file_set(repo_root: str, rel_paths: Iterable[str]) -> str:
    h = hashlib.sha256()
    for rel in sorted(set(rel_paths)):
        abs_path = _norm(os.path.join(repo_root, rel.replace("/", os.sep)))
        if not os.path.isfile(abs_path):
            continue
        h.update(rel.replace("\\", "/").encode("utf-8"))
        h.update(b"\x00")
        h.update(_file_hash(abs_path).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _hash_text_values(values: Iterable[str]) -> str:
    h = hashlib.sha256()
    for item in sorted(set(values)):
        h.update(item.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _scan_rel_files(repo_root: str) -> List[str]:
    exts = {
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hh",
        ".hpp",
        ".hxx",
        ".py",
        ".json",
        ".schema",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
    }
    skip_dirs = {
        ".git",
        ".vs",
        "__pycache__",
        "build",
        "dist",
        "out",
        "tmp",
    }
    out: List[str] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = sorted([item for item in dirs if item not in skip_dirs])
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(root, name), repo_root).replace("\\", "/")
            if rel.startswith("tools/auditx/cache/"):
                continue
            if rel.startswith("docs/audit/auditx/"):
                continue
            ext = os.path.splitext(rel)[1].lower()
            if ext in exts:
                out.append(rel)
    return sorted(set(out))


def _registry_rel_files(repo_root: str) -> List[str]:
    roots = [
        os.path.join("data", "registries"),
        os.path.join("schema"),
        os.path.join("repo", "repox", "rulesets"),
    ]
    rels: List[str] = []
    for rel_root in roots:
        abs_root = _norm(os.path.join(repo_root, rel_root))
        if not os.path.isdir(abs_root):
            continue
        for root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                rel = os.path.relpath(os.path.join(root, name), repo_root).replace("\\", "/")
                rels.append(rel)
    return sorted(set(rels))


def _analyzer_rel_files(repo_root: str) -> List[str]:
    root = os.path.join(repo_root, "tools", "auditx")
    rels: List[str] = []
    if not os.path.isdir(root):
        return rels
    for walk_root, dirs, files in os.walk(root):
        dirs[:] = sorted([item for item in dirs if item != "cache" and item != "__pycache__"])
        for name in sorted(files):
            if not name.lower().endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(walk_root, name), repo_root).replace("\\", "/")
            rels.append(rel)
    return sorted(set(rels))


def _snapshot_hashes(repo_root: str, rel_paths: Iterable[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rel in sorted(set(rel_paths)):
        abs_path = _norm(os.path.join(repo_root, rel.replace("/", os.sep)))
        if not os.path.isfile(abs_path):
            continue
        out[rel] = _file_hash(abs_path)
    return out


def _diff_paths(old_hashes: Dict[str, str], new_hashes: Dict[str, str]) -> List[str]:
    changed = set()
    all_paths = set(old_hashes.keys()) | set(new_hashes.keys())
    for rel in sorted(all_paths):
        if old_hashes.get(rel) != new_hashes.get(rel):
            changed.add(rel)
    return sorted(changed)


class AuditXCache:
    def __init__(self, repo_root: str, workspace_id: str):
        self.repo_root = _norm(os.path.abspath(repo_root))
        self.workspace_id = workspace_id or "default"
        self.cache_root = _norm(os.path.join(self.repo_root, CACHE_ROOT_REL, self.workspace_id))
        self.entries_root = _norm(os.path.join(self.cache_root, "entries"))
        self.state_path = _norm(os.path.join(self.cache_root, "state.json"))
        os.makedirs(self.entries_root, exist_ok=True)

    def load_state(self) -> Dict[str, object]:
        payload = _load_json(self.state_path)
        if not isinstance(payload, dict):
            return {}
        return payload

    def save_state(self, payload: Dict[str, object]) -> None:
        out = dict(payload)
        out["cache_version"] = CACHE_VERSION
        _write_json(self.state_path, out)

    def entry_path(self, cache_key: str) -> str:
        return _norm(os.path.join(self.entries_root, "{}.json".format(cache_key)))

    def load_entry(self, cache_key: str):
        payload = _load_json(self.entry_path(cache_key))
        if not isinstance(payload, dict):
            return None
        return payload

    def save_entry(self, cache_key: str, payload: Dict[str, object]) -> None:
        out = dict(payload)
        out["cache_version"] = CACHE_VERSION
        _write_json(self.entry_path(cache_key), out)

    def load_trend_history(self) -> Dict[str, object]:
        payload = _load_json(_norm(os.path.join(self.cache_root, "trend_history.json")))
        if not isinstance(payload, dict):
            return {"history": []}
        history = payload.get("history")
        if not isinstance(history, list):
            return {"history": []}
        return {"history": history}

    def save_trend_history(self, payload: Dict[str, object]) -> None:
        _write_json(_norm(os.path.join(self.cache_root, "trend_history.json")), payload)


def build_cache_context(repo_root: str, changed_only: bool, scan_scope_paths: Iterable[str], config_payload: Dict[str, object]):
    rel_files = _scan_rel_files(repo_root)
    file_hashes = _snapshot_hashes(repo_root, rel_files)
    content_hash = _hash_text_values(["{}:{}".format(path, file_hashes[path]) for path in sorted(file_hashes.keys())])
    registry_hash = _hash_file_set(repo_root, _registry_rel_files(repo_root))
    analyzer_hash = _hash_file_set(repo_root, _analyzer_rel_files(repo_root))
    scan_scope_hash = _hash_text_values(scan_scope_paths)
    head_hash = _git_head_hash(repo_root)
    config_blob = json.dumps(config_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    config_hash = hashlib.sha256(config_blob.encode("utf-8")).hexdigest()
    key_blob = json.dumps(
        {
            "cache_version": CACHE_VERSION,
            "head_hash": head_hash,
            "registry_hash": registry_hash,
            "analyzer_hash": analyzer_hash,
            "config_hash": config_hash,
            "scan_scope_hash": scan_scope_hash,
            "content_hash": content_hash,
            "changed_only": bool(changed_only),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    cache_key = hashlib.sha256(key_blob.encode("utf-8")).hexdigest()
    return {
        "cache_key": cache_key,
        "head_hash": head_hash,
        "registry_hash": registry_hash,
        "analyzer_hash": analyzer_hash,
        "config_hash": config_hash,
        "scan_scope_hash": scan_scope_hash,
        "content_hash": content_hash,
        "file_hashes": file_hashes,
    }


def changed_paths_from_state(previous_state: Dict[str, object], current_hashes: Dict[str, str]) -> List[str]:
    old_hashes = previous_state.get("file_hashes")
    if not isinstance(old_hashes, dict):
        return sorted(current_hashes.keys())
    return _diff_paths(old_hashes, current_hashes)
