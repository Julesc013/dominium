"""Helpers for META-STABILITY-0 TestX coverage."""

from __future__ import annotations

import json
import os
from typing import Mapping

from src.meta.stability import SCOPED_REGISTRY_PATHS, validate_scoped_registries


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload) if isinstance(payload, dict) else {}


def _detect_collection(payload: Mapping[str, object] | None) -> list[dict]:
    root = dict(payload or {})
    if isinstance(root.get("records"), list):
        return [dict(row) for row in list(root.get("records") or []) if isinstance(row, Mapping)]
    record = dict(root.get("record") or {})
    candidates = []
    for key, value in sorted(record.items(), key=lambda item: str(item[0])):
        if key == "extensions" or not isinstance(value, list):
            continue
        rows = [dict(row) for row in list(value) if isinstance(row, Mapping)]
        if len(rows) != len(value):
            continue
        candidates.append(rows)
    return candidates[0] if len(candidates) == 1 else []


def load_validation_report(repo_root: str) -> dict:
    return validate_scoped_registries(repo_root)


def error_codes(report: Mapping[str, object] | None) -> list[str]:
    codes: list[str] = []
    for registry_report in list(dict(report or {}).get("reports") or []):
        for error in list(dict(registry_report or {}).get("errors") or []):
            code = str(dict(error or {}).get("code", "")).strip()
            if code:
                codes.append(code)
    return sorted(codes)


def stability_class_counts(repo_root: str) -> dict[str, int]:
    counts = {"stable": 0, "provisional": 0, "experimental": 0}
    for rel_path in SCOPED_REGISTRY_PATHS:
        payload = _read_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        for row in _detect_collection(payload):
            stability = dict(row.get("stability") or {})
            token = str(stability.get("stability_class_id", "")).strip()
            if token in counts:
                counts[token] += 1
    return counts

