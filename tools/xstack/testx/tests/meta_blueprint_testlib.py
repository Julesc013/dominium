"""Shared Π-0 meta-blueprint TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.meta_blueprint_common import (
    CAPABILITY_LADDER_REL,
    FOUNDATION_READINESS_REL,
    LIVE_OPS_DIAGRAM_REL,
    META_BLUEPRINT_INDEX_REL,
    META_BLUEPRINT_SUMMARY_REL,
    DIST_ARCHIVE_DIAGRAM_REL,
    PIPE_DREAMS_MATRIX_REL,
    PIPE_DREAMS_REL,
    PI_0_FINAL_REL,
    READINESS_MATRIX_REL,
    REPO_GOV_DIAGRAM_REL,
    RUNTIME_ARCH_DIAGRAM_REL,
    SERIES_DEP_GRAPH_REL,
    SERIES_DEP_MAP_REL,
    SNAPSHOT_MAPPING_NOTES_REL,
    build_meta_blueprint_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _load_text(repo_root: str, rel_path: str) -> str:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def committed_series_dependency_graph(repo_root: str) -> dict:
    return _load_json(repo_root, SERIES_DEP_GRAPH_REL)


def committed_readiness_matrix(repo_root: str) -> dict:
    return _load_json(repo_root, READINESS_MATRIX_REL)


def committed_pipe_dreams_matrix(repo_root: str) -> dict:
    return _load_json(repo_root, PIPE_DREAMS_MATRIX_REL)


def committed_docs(repo_root: str) -> dict[str, str]:
    rel_paths = [
        META_BLUEPRINT_INDEX_REL,
        META_BLUEPRINT_SUMMARY_REL,
        RUNTIME_ARCH_DIAGRAM_REL,
        REPO_GOV_DIAGRAM_REL,
        DIST_ARCHIVE_DIAGRAM_REL,
        LIVE_OPS_DIAGRAM_REL,
        SERIES_DEP_MAP_REL,
        CAPABILITY_LADDER_REL,
        FOUNDATION_READINESS_REL,
        PIPE_DREAMS_REL,
        SNAPSHOT_MAPPING_NOTES_REL,
        PI_0_FINAL_REL,
    ]
    return {rel_path: _load_text(repo_root, rel_path) for rel_path in rel_paths}


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_meta_blueprint_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_docs",
    "committed_pipe_dreams_matrix",
    "committed_readiness_matrix",
    "committed_series_dependency_graph",
    "fresh_snapshot",
]
