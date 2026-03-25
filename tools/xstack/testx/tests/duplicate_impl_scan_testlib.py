"""Shared XI-1 duplicate implementation scan TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.duplicate_impl_scan_common import (
    DUPLICATE_IMPLS_REL,
    SRC_DIRECTORY_REPORT_REL,
    build_duplicate_impl_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError("{} is not a JSON object".format(rel_path))
    return payload


def committed_duplicate_impls(repo_root: str) -> dict:
    return _load_json(repo_root, DUPLICATE_IMPLS_REL)


def committed_src_directory_report(repo_root: str) -> dict:
    return _load_json(repo_root, SRC_DIRECTORY_REPORT_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_duplicate_impl_snapshot(key)
        _CACHE[key] = cached
    return cached


__all__ = [
    "committed_duplicate_impls",
    "committed_src_directory_report",
    "fresh_snapshot",
]
