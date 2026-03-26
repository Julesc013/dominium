"""Shared XI-4 convergence execution TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.convergence_execution_common import (
    BUILD_GRAPH_REL,
    CONVERGENCE_EXECUTION_LOG_REL,
    CONVERGENCE_PLAN_REL,
    build_convergence_execution_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("{} is not a JSON object".format(rel_path))
    return payload


def committed_build_graph(repo_root: str) -> dict:
    return _load_json(repo_root, BUILD_GRAPH_REL)


def committed_convergence_execution_log(repo_root: str) -> dict:
    return _load_json(repo_root, CONVERGENCE_EXECUTION_LOG_REL)


def committed_convergence_plan(repo_root: str) -> dict:
    return _load_json(repo_root, CONVERGENCE_PLAN_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_convergence_execution_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_build_graph",
    "committed_convergence_execution_log",
    "committed_convergence_plan",
    "fresh_snapshot",
]
