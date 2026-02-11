"""Canonicalization helpers for PerformX artifacts."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List


FORBIDDEN_CANONICAL_KEYS = {
    "generated_utc",
    "timestamp",
    "timestamps",
    "machine_id",
    "machine_name",
    "host_name",
    "run_id",
    "duration_ms",
    "measured_at",
    "started_utc",
    "finished_utc",
}


def _sort_key_for_dict(item: Dict[str, Any]) -> tuple:
    primary_keys = (
        "envelope_id",
        "metric_id",
        "regression_id",
        "profile_id",
        "baseline_id",
        "artifact_id",
    )
    for key in primary_keys:
        value = item.get(key)
        if value is not None:
            return (key, str(value))
    return ("", json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True))


def _canonicalize_list(values: Iterable[Any], forbidden: set) -> List[Any]:
    canonical_items = [canonicalize_json_payload(value, forbidden) for value in values]
    if all(isinstance(item, dict) for item in canonical_items):
        return sorted(canonical_items, key=_sort_key_for_dict)
    if all(isinstance(item, str) for item in canonical_items):
        return sorted(canonical_items)
    return canonical_items


def canonicalize_json_payload(payload: Any, forbidden_keys: Iterable[str] | None = None) -> Any:
    forbidden = set(forbidden_keys or FORBIDDEN_CANONICAL_KEYS)
    if isinstance(payload, dict):
        out: Dict[str, Any] = {}
        for key in sorted(payload.keys()):
            if key in forbidden:
                continue
            out[key] = canonicalize_json_payload(payload[key], forbidden)
        return out
    if isinstance(payload, list):
        return _canonicalize_list(payload, forbidden)
    return payload


def canonical_json_string(payload: Any, forbidden_keys: Iterable[str] | None = None) -> str:
    canonical = canonicalize_json_payload(payload, forbidden_keys=forbidden_keys)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_sha256(payload: Any, forbidden_keys: Iterable[str] | None = None) -> str:
    return hashlib.sha256(canonical_json_string(payload, forbidden_keys=forbidden_keys).encode("utf-8")).hexdigest()

