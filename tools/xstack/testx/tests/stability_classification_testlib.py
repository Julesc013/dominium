"""Helpers for META-STABILITY TestX coverage."""

from __future__ import annotations

from collections import Counter
from typing import Mapping

from meta.stability import ALL_REGISTRY_PATHS, registry_entry_rows, validate_all_registries


def load_validation_report(repo_root: str) -> dict:
    return validate_all_registries(repo_root)


def error_codes(report: Mapping[str, object] | None) -> list[str]:
    codes: list[str] = []
    for registry_report in list(dict(report or {}).get("reports") or []):
        for error in list(dict(registry_report or {}).get("errors") or []):
            code = str(dict(error or {}).get("code", "")).strip()
            if code:
                codes.append(code)
    return sorted(codes)


def stability_class_counts(repo_root: str) -> dict[str, int]:
    del repo_root
    counts = Counter({"stable": 0, "provisional": 0, "experimental": 0})
    for rel_path in ALL_REGISTRY_PATHS:
        payload = registry_entry_rows(rel_path)
        for row in list(payload.get("entries") or []):
            stability = dict(dict(dict(row or {}).get("row") or {}).get("stability") or {})
            token = str(stability.get("stability_class_id", "")).strip()
            if token in counts:
                counts[token] += 1
    return dict(counts)


def duplicate_item_errors(report: Mapping[str, object] | None) -> list[dict]:
    rows: list[dict] = []
    for registry_report in list(dict(report or {}).get("reports") or []):
        rel_path = str(dict(registry_report or {}).get("file_path", "")).replace("\\", "/")
        for error in list(dict(registry_report or {}).get("errors") or []):
            error_row = dict(error or {})
            if str(error_row.get("code", "")).strip() != "duplicate_item_id":
                continue
            rows.append(
                {
                    "file_path": rel_path,
                    "item_id": str(error_row.get("item_id", "")).strip(),
                    "path": str(error_row.get("path", "")).strip(),
                }
            )
    return sorted(rows, key=lambda row: (row["file_path"], row["item_id"], row["path"]))
