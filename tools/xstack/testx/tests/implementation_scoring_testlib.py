"""Shared XI-2 implementation scoring TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.implementation_scoring_common import (
    DUPLICATE_CLUSTER_RANKINGS_REL,
    IMPLEMENTATION_SCORES_REL,
    build_implementation_scoring_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("{} is not a JSON object".format(rel_path))
    return payload


def committed_implementation_scores(repo_root: str) -> dict:
    return _load_json(repo_root, IMPLEMENTATION_SCORES_REL)


def committed_duplicate_cluster_rankings(repo_root: str) -> dict:
    return _load_json(repo_root, DUPLICATE_CLUSTER_RANKINGS_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_implementation_scoring_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_duplicate_cluster_rankings",
    "committed_implementation_scores",
    "fresh_snapshot",
]
