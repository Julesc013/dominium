"""Shared PI-1 series execution strategy TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.series_execution_strategy_common import (
    FOUNDATION_PHASES_REL,
    MANUAL_REVIEW_GATES_REL,
    SERIES_EXECUTION_STRATEGY_REL,
    STOP_CONDITIONS_REL,
    build_series_execution_strategy_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_series_execution_strategy(repo_root: str) -> dict:
    return _load_json(repo_root, SERIES_EXECUTION_STRATEGY_REL)


def committed_foundation_phases(repo_root: str) -> dict:
    return _load_json(repo_root, FOUNDATION_PHASES_REL)


def committed_stop_conditions(repo_root: str) -> dict:
    return _load_json(repo_root, STOP_CONDITIONS_REL)


def committed_manual_review_gates(repo_root: str) -> dict:
    return _load_json(repo_root, MANUAL_REVIEW_GATES_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_series_execution_strategy_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_foundation_phases",
    "committed_manual_review_gates",
    "committed_series_execution_strategy",
    "committed_stop_conditions",
    "fresh_snapshot",
]
