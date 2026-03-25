"""Shared XI-3 convergence planning TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.convergence_plan_common import (
    CONVERGENCE_ACTIONS_REL,
    CONVERGENCE_PLAN_REL,
    CONVERGENCE_RISK_MAP_REL,
    build_convergence_plan_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_convergence_plan(repo_root: str) -> dict:
    return _load_json(repo_root, CONVERGENCE_PLAN_REL)


def committed_convergence_actions(repo_root: str) -> dict:
    return _load_json(repo_root, CONVERGENCE_ACTIONS_REL)


def committed_convergence_risk_map(repo_root: str) -> dict:
    return _load_json(repo_root, CONVERGENCE_RISK_MAP_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_convergence_plan_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_convergence_actions",
    "committed_convergence_plan",
    "committed_convergence_risk_map",
    "fresh_snapshot",
]
