"""Shared PI-2 final prompt inventory TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.final_prompt_inventory_common import (
    FINAL_PROMPT_INVENTORY_REL,
    PI_2_FINAL_REL,
    PROMPT_DEPENDENCY_TREE_REL,
    PROMPT_RISK_MATRIX_REL,
    RECONCILIATION_RULES_REL,
    SNAPSHOT_MAPPING_TEMPLATE_REL,
    build_final_prompt_inventory_snapshot,
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


def committed_final_prompt_inventory(repo_root: str) -> dict:
    return _load_json(repo_root, FINAL_PROMPT_INVENTORY_REL)


def committed_snapshot_mapping_template(repo_root: str) -> dict:
    return _load_json(repo_root, SNAPSHOT_MAPPING_TEMPLATE_REL)


def committed_prompt_dependency_tree(repo_root: str) -> dict:
    return _load_json(repo_root, PROMPT_DEPENDENCY_TREE_REL)


def committed_prompt_risk_matrix(repo_root: str) -> dict:
    return _load_json(repo_root, PROMPT_RISK_MATRIX_REL)


def committed_reconciliation_rules(repo_root: str) -> dict:
    return _load_json(repo_root, RECONCILIATION_RULES_REL)


def committed_final_doc(repo_root: str) -> str:
    return _load_text(repo_root, PI_2_FINAL_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_final_prompt_inventory_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_final_doc",
    "committed_final_prompt_inventory",
    "committed_prompt_dependency_tree",
    "committed_prompt_risk_matrix",
    "committed_reconciliation_rules",
    "committed_snapshot_mapping_template",
    "fresh_snapshot",
]
