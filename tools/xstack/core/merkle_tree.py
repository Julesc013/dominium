"""Deterministic subtree Merkle hashing for incremental gate planning."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Tuple

from .artifact_contract import load_artifact_contract
from .profiler import end_phase, start_phase


DEFAULT_SUBTREES: Tuple[str, ...] = (
    "engine",
    "game",
    "client",
    "server",
    "tools",
    "schema",
    "data",
    "docs",
    "scripts",
    "repo",
    "tests",
)
MERKLE_ROOTS_CACHE_REL = os.path.join("merkle", "roots.json")
MERKLE_FILE_HASH_CACHE_REL = os.path.join("merkle", "file_hashes.json")
DEFAULT_SKIP_PREFIXES: Tuple[str, ...] = (
    ".xstack_cache/",
    "build/",
    "dist/",
    "tmp/",
    "tools/auditx/cache/",
    "tools/compatx/cache/",
    "tools/performx/cache/",
    "tools/securex/cache/",
)


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_hash(path: str) -> str:
    handle = open(path, "rb")
    try:
        digest = hashlib.sha256()
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    finally:
        handle.close()


def _iter_files(root: str) -> List[str]:
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in {".git", ".vs", "__pycache__", ".mypy_cache", ".xstack_cache"}
        )
        for filename in sorted(filenames):
            out.append(os.path.join(dirpath, filename))
    return out


def _mtime_ns(stat_result) -> int:
    raw = getattr(stat_result, "st_mtime_ns", None)
    if raw is not None:
        return int(raw)
    return int(float(stat_result.st_mtime) * 1000000000.0)


def _cached_hash_for_path(path: str, rel: str, hash_cache: Dict[str, dict]) -> Tuple[str, dict]:
    stat_result = os.stat(path)
    size = int(stat_result.st_size)
    mtime_ns = _mtime_ns(stat_result)
    previous = hash_cache.get(rel, {})
    if (
        isinstance(previous, dict)
        and int(previous.get("size", -1)) == size
        and int(previous.get("mtime_ns", -1)) == mtime_ns
        and str(previous.get("hash", "")).strip()
    ):
        digest = str(previous.get("hash", "")).strip()
    else:
        digest = _file_hash(path)
    return digest, {"size": size, "mtime_ns": mtime_ns, "hash": digest}


def _subtree_hash(
    repo_root: str,
    subtree_rel: str,
    hash_cache: Dict[str, dict],
    next_hash_cache: Dict[str, dict],
    skip_paths: set,
    skip_prefixes: Tuple[str, ...],
) -> Dict[str, object]:
    phase = "merkle.subtree.{}".format(subtree_rel)
    start_phase(phase)
    abs_root = os.path.join(repo_root, subtree_rel)
    if not os.path.isdir(abs_root):
        result = {"subtree": subtree_rel, "exists": False, "hash": _sha256_bytes(b""), "file_count": 0}
        end_phase(phase, {"file_count": 0, "exists": False})
        return result

    nodes: List[str] = []
    file_count = 0
    for path in _iter_files(abs_root):
        rel = _norm(os.path.relpath(path, repo_root))
        if rel in skip_paths:
            continue
        if any(rel.startswith(prefix) for prefix in skip_prefixes):
            continue
        if rel.startswith("tools/") and "/cache/" in rel:
            continue
        digest, cache_row = _cached_hash_for_path(path, rel, hash_cache)
        next_hash_cache[rel] = cache_row
        file_count += 1
        nodes.append("{}:{}".format(rel, digest))
    digest = _sha256_bytes("\n".join(nodes).encode("utf-8"))
    result = {"subtree": subtree_rel, "exists": True, "hash": digest, "file_count": file_count}
    end_phase(phase, {"file_count": file_count, "exists": True})
    return result


def _cache_path(repo_root: str, cache_root: str, rel_path: str) -> str:
    root = cache_root or os.path.join(repo_root, ".xstack_cache")
    return os.path.join(root, rel_path)


def _load_json_cache(repo_root: str, cache_root: str, rel_path: str) -> Dict[str, object]:
    path = _cache_path(repo_root, cache_root, rel_path)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _store_json_cache(repo_root: str, cache_root: str, rel_path: str, payload: Dict[str, object]) -> str:
    path = _cache_path(repo_root, cache_root, rel_path)
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def _artifact_skip_paths(
    repo_root: str,
    include_artifact_classes: Tuple[str, ...] | None = None,
    exclude_artifact_classes: Tuple[str, ...] | None = None,
) -> set:
    contract = load_artifact_contract(repo_root)
    skip = set()
    include_classes = {str(item).strip().upper() for item in (include_artifact_classes or ()) if str(item).strip()}
    exclude_classes = {str(item).strip().upper() for item in (exclude_artifact_classes or ()) if str(item).strip()}
    for row in contract.values():
        rel = str(row.get("path", "")).replace("\\", "/").strip("/")
        if not rel:
            continue
        artifact_class = str(row.get("artifact_class", "")).strip().upper()
        if include_classes and artifact_class not in include_classes:
            skip.add(rel)
            continue
        if exclude_classes and artifact_class in exclude_classes:
            skip.add(rel)
    return skip


def build_skip_prefixes(extra_excluded_prefixes: Tuple[str, ...] | None = None) -> Tuple[str, ...]:
    prefixes = set(DEFAULT_SKIP_PREFIXES)
    for value in (extra_excluded_prefixes or ()):
        token = _norm(str(value))
        if not token:
            continue
        if not token.endswith("/"):
            token += "/"
        prefixes.add(token)
    return tuple(sorted(prefixes))


def compute_subtree_roots(
    repo_root: str,
    subtrees: List[str] | None = None,
    hash_cache: Dict[str, dict] | None = None,
    skip_paths: set | None = None,
    skip_prefixes: Tuple[str, ...] | None = None,
) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    roots: Dict[str, dict] = {}
    next_hash_cache: Dict[str, dict] = {}
    current_cache = hash_cache or {}
    effective_skip = skip_paths or set()
    effective_prefixes = tuple(skip_prefixes or ())
    for subtree in (subtrees or list(DEFAULT_SUBTREES)):
        token = _norm(str(subtree))
        if not token:
            continue
        roots[token] = _subtree_hash(
            repo_root,
            token,
            current_cache,
            next_hash_cache,
            effective_skip,
            effective_prefixes,
        )
    return roots, next_hash_cache


def _repo_state_hash(roots: Dict[str, dict]) -> str:
    entries = []
    for key in sorted(roots.keys()):
        row = roots[key]
        entries.append("{}:{}".format(key, str(row.get("hash", ""))))
    return _sha256_bytes("\n".join(entries).encode("utf-8"))


def load_cached_roots(repo_root: str, cache_root: str = "") -> Dict[str, object]:
    return _load_json_cache(repo_root, cache_root, MERKLE_ROOTS_CACHE_REL)


def store_cached_roots(repo_root: str, payload: Dict[str, object], cache_root: str = "") -> str:
    return _store_json_cache(repo_root, cache_root, MERKLE_ROOTS_CACHE_REL, payload)


def load_file_hash_cache(repo_root: str, cache_root: str = "") -> Dict[str, dict]:
    payload = _load_json_cache(repo_root, cache_root, MERKLE_FILE_HASH_CACHE_REL)
    rows = payload.get("hashes", {})
    return rows if isinstance(rows, dict) else {}


def store_file_hash_cache(repo_root: str, hashes: Dict[str, dict], cache_root: str = "") -> str:
    payload = {"schema_version": "1.0.0", "hashes": hashes}
    return _store_json_cache(repo_root, cache_root, MERKLE_FILE_HASH_CACHE_REL, payload)


def compute_repo_state_hash(
    repo_root: str,
    cache_root: str = "",
    subtrees: List[str] | None = None,
    include_artifact_classes: Tuple[str, ...] | None = None,
    exclude_artifact_classes: Tuple[str, ...] | None = ("RUN_META", "DERIVED_VIEW"),
    extra_excluded_prefixes: Tuple[str, ...] | None = None,
) -> Dict[str, object]:
    start_phase("merkle.compute_repo_state_hash")
    hash_cache = load_file_hash_cache(repo_root, cache_root=cache_root)
    skip_paths = _artifact_skip_paths(
        repo_root,
        include_artifact_classes=include_artifact_classes,
        exclude_artifact_classes=exclude_artifact_classes,
    )
    skip_prefixes = build_skip_prefixes(extra_excluded_prefixes=extra_excluded_prefixes)
    try:
        roots, next_hash_cache = compute_subtree_roots(
            repo_root,
            subtrees=subtrees,
            hash_cache=hash_cache,
            skip_paths=skip_paths,
            skip_prefixes=skip_prefixes,
        )
        state_hash = _repo_state_hash(roots)
        payload = {
            "schema_version": "1.0.0",
            "repo_state_hash": state_hash,
            "roots": roots,
        }
        store_cached_roots(repo_root, payload, cache_root=cache_root)
        store_file_hash_cache(repo_root, next_hash_cache, cache_root=cache_root)
        return payload
    finally:
        end_phase("merkle.compute_repo_state_hash")
