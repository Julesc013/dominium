"""Shared Ξ-0 architecture graph TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.architecture_graph_bootstrap_common import (
    ARCHITECTURE_GRAPH_REL,
    MODULE_REGISTRY_REL,
    SYMBOL_INDEX_REL,
    build_architecture_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("{} is not a JSON object".format(rel_path))
    return payload


def committed_architecture_graph(repo_root: str) -> dict:
    return _load_json(repo_root, ARCHITECTURE_GRAPH_REL)


def committed_module_registry(repo_root: str) -> dict:
    return _load_json(repo_root, MODULE_REGISTRY_REL)


def committed_symbol_index(repo_root: str) -> dict:
    return _load_json(repo_root, SYMBOL_INDEX_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_architecture_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_architecture_graph",
    "committed_module_registry",
    "committed_symbol_index",
    "fresh_snapshot",
]
