"""Deterministic GEO-3 metric query cache."""

from __future__ import annotations

import copy
from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_DEFAULT_CACHE_MAX_ENTRIES = 512
_METRIC_CACHE_VERSION = "GEO3-5"
_CACHE_ROWS: Dict[str, dict] = {}
_CACHE_ACCESS_ORDINALS: Dict[str, int] = {}
_CACHE_ACCESS_COUNTER = 0


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _deepcopy(payload: object) -> object:
    return copy.deepcopy(payload)


def metric_cache_enabled(*, cache_enabled: bool | None = None, reference_mode: str = "") -> bool:
    if cache_enabled is False:
        return False
    return str(reference_mode or "").strip().upper() != "FULL"


def metric_cache_key(namespace: str, seed: Mapping[str, object], *, version: str = "") -> str:
    payload = {
        "namespace": str(namespace or "").strip(),
        "version": str(version or "").strip() or _METRIC_CACHE_VERSION,
        "seed": _as_map(seed),
    }
    return canonical_sha256(payload)


def _touch(cache_key: str) -> None:
    global _CACHE_ACCESS_COUNTER
    _CACHE_ACCESS_COUNTER += 1
    _CACHE_ACCESS_ORDINALS[str(cache_key)] = int(_CACHE_ACCESS_COUNTER)


def _evict(max_entries: int) -> None:
    limit = int(max(1, int(max_entries)))
    if len(_CACHE_ROWS) <= limit:
        return
    ranked_keys = sorted(
        _CACHE_ROWS.keys(),
        key=lambda key: (int(_CACHE_ACCESS_ORDINALS.get(str(key), 0)), str(key)),
    )
    while len(ranked_keys) > limit:
        evicted_key = str(ranked_keys.pop(0))
        _CACHE_ROWS.pop(evicted_key, None)
        _CACHE_ACCESS_ORDINALS.pop(evicted_key, None)


def metric_cache_lookup(
    namespace: str,
    seed: Mapping[str, object],
    *,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    version: str = "",
) -> dict | None:
    if not metric_cache_enabled(cache_enabled=cache_enabled, reference_mode=reference_mode):
        return None
    cache_key = metric_cache_key(namespace, seed, version=version)
    payload = _CACHE_ROWS.get(str(cache_key))
    if not isinstance(payload, dict):
        return None
    _touch(cache_key)
    return dict(_deepcopy(payload) or {})


def metric_cache_store(
    namespace: str,
    seed: Mapping[str, object],
    payload: Mapping[str, object],
    *,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    version: str = "",
    max_entries: int | None = None,
) -> dict:
    if not metric_cache_enabled(cache_enabled=cache_enabled, reference_mode=reference_mode):
        return dict(_deepcopy(payload) or {})
    cache_key = metric_cache_key(namespace, seed, version=version)
    _CACHE_ROWS[str(cache_key)] = dict(_deepcopy(payload) or {})
    _touch(cache_key)
    _evict(_DEFAULT_CACHE_MAX_ENTRIES if max_entries is None else int(max_entries))
    return dict(_deepcopy(payload) or {})


def metric_cache_clear() -> None:
    global _CACHE_ACCESS_COUNTER
    _CACHE_ROWS.clear()
    _CACHE_ACCESS_ORDINALS.clear()
    _CACHE_ACCESS_COUNTER = 0


def metric_cache_snapshot() -> dict:
    return {
        "cache_entry_count": int(len(_CACHE_ROWS)),
        "cache_keys": [str(key) for key in sorted(_CACHE_ROWS.keys())],
        "deterministic_fingerprint": canonical_sha256(
            {
                "cache_entry_count": int(len(_CACHE_ROWS)),
                "cache_keys": [str(key) for key in sorted(_CACHE_ROWS.keys())],
            }
        ),
    }


__all__ = [
    "metric_cache_clear",
    "metric_cache_enabled",
    "metric_cache_key",
    "metric_cache_lookup",
    "metric_cache_snapshot",
    "metric_cache_store",
]
