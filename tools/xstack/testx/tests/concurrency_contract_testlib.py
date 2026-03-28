"""Shared CONCURRENCY-CONTRACT-0 TestX helpers."""

from __future__ import annotations

import os

from engine.concurrency.canonical_merge import (
    build_field_sort_key,
    canonical_merge_mapping_groups,
)
from tools.engine.concurrency_contract_common import build_concurrency_contract_report


_CACHE: dict[str, dict] = {}


def build_report(repo_root: str) -> dict:
    global _CACHE
    token = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    cached = dict(_CACHE.get(token) or {})
    if cached:
        return cached
    report = build_concurrency_contract_report(token)
    _CACHE[token] = dict(report)
    return dict(report)


def build_derived_rows() -> list[dict]:
    key_fn = build_field_sort_key(("tile_cell_key", "sub_index"), int_fields=("sub_index",))
    return canonical_merge_mapping_groups(
        [
            [
                {"tile_cell_key": "tile.003", "sub_index": 1, "artifact_id": "artifact.c"},
                {"tile_cell_key": "tile.001", "sub_index": 2, "artifact_id": "artifact.b"},
            ],
            [
                {"tile_cell_key": "tile.001", "sub_index": 1, "artifact_id": "artifact.a"},
                {"tile_cell_key": "tile.002", "sub_index": 1, "artifact_id": "artifact.d"},
            ],
        ],
        key_fn=key_fn,
    )


def build_validation_rows() -> list[dict]:
    key_fn = build_field_sort_key(("level", "runner_id", "node_id"), int_fields=("level",))
    return canonical_merge_mapping_groups(
        [
            [
                {"level": 1, "runner_id": "testx", "node_id": "node.beta"},
                {"level": 0, "runner_id": "auditx", "node_id": "node.alpha"},
            ],
            [
                {"level": 1, "runner_id": "testx", "node_id": "node.gamma"},
                {"level": 2, "runner_id": "repox", "node_id": "node.delta"},
            ],
        ],
        key_fn=key_fn,
    )


__all__ = [
    "build_derived_rows",
    "build_report",
    "build_validation_rows",
]
