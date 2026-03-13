"""Shared DIST-4 platform matrix TestX helpers."""

from __future__ import annotations

import os

from tools.dist.dist_platform_matrix_common import (
    DEFAULT_BUILD_OUTPUT_ROOT,
    DEFAULT_PLATFORM_TAGS,
    build_platform_matrix_report,
    load_dist_platform_matrix_report,
)


def load_report(repo_root: str) -> dict:
    report = load_dist_platform_matrix_report(repo_root)
    if report:
        return report
    return build_platform_matrix_report(
        repo_root,
        platform_tags=DEFAULT_PLATFORM_TAGS,
        build_output_root=os.path.join(repo_root, DEFAULT_BUILD_OUTPUT_ROOT.replace("/", os.sep)),
    )


def build_report(repo_root: str) -> dict:
    return build_platform_matrix_report(
        repo_root,
        platform_tags=DEFAULT_PLATFORM_TAGS,
        build_output_root=os.path.join(repo_root, DEFAULT_BUILD_OUTPUT_ROOT.replace("/", os.sep)),
    )


def context_rows(report: dict, *, platform_tag: str = "win64") -> list[dict]:
    rows = []
    for platform_row in list(dict(report or {}).get("platform_rows") or []):
        item = dict(platform_row or {})
        if str(item.get("platform_tag", "")).strip() != platform_tag:
            continue
        rows.extend([dict(row or {}) for row in list(item.get("context_rows") or [])])
    return sorted(rows, key=lambda row: (str(row.get("product_id", "")).strip(), str(row.get("context_id", "")).strip()))


def fallback_rows(report: dict, *, platform_tag: str = "win64") -> list[dict]:
    rows = []
    for platform_row in list(dict(report or {}).get("platform_rows") or []):
        item = dict(platform_row or {})
        if str(item.get("platform_tag", "")).strip() != platform_tag:
            continue
        rows.extend([dict(row or {}) for row in list(item.get("fallback_rows") or [])])
    return sorted(rows, key=lambda row: (str(row.get("product_id", "")).strip(), str(row.get("requested_mode_id", "")).strip()))


__all__ = [
    "build_report",
    "context_rows",
    "fallback_rows",
    "load_report",
]
