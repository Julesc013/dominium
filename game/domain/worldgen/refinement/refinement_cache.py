"""Deterministic MW-4 refinement cache helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from engine.serialization.canonical_json import canonical_sha256


DEFAULT_REFINEMENT_CACHE_LIMITS = {
    0: 256,
    1: 256,
    2: 192,
    3: 384,
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canonical_cell_key_seed(
    *,
    partition_profile_id: str,
    topology_profile_id: str,
    chart_id: str,
    index_tuple: object,
    refinement_level: int,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "partition_profile_id": str(partition_profile_id),
        "topology_profile_id": str(topology_profile_id),
        "chart_id": str(chart_id),
        "index_tuple": [int(value) for value in list(index_tuple or [])],
        "refinement_level": int(max(0, int(refinement_level))),
    }


def _semantic_cell_key(cell_key: Mapping[str, object]) -> dict:
    row = _as_map(cell_key)
    return _canonical_cell_key_seed(
        partition_profile_id=str(row.get("partition_profile_id", "")),
        topology_profile_id=str(row.get("topology_profile_id", "")),
        chart_id=str(row.get("chart_id", "")),
        index_tuple=list(row.get("index_tuple") or []),
        refinement_level=_as_int(row.get("refinement_level", 0), 0),
    )


def _coerce_cell_key(cell_key: Mapping[str, object] | None) -> dict | None:
    payload = _as_map(cell_key)
    if not payload:
        return None
    partition_profile_id = str(payload.get("partition_profile_id", "")).strip()
    topology_profile_id = str(payload.get("topology_profile_id", "")).strip()
    chart_id = str(payload.get("chart_id", "")).strip()
    index_tuple = payload.get("index_tuple")
    if not partition_profile_id or not topology_profile_id or not chart_id or not isinstance(index_tuple, list) or not index_tuple:
        return None
    row = {
        "schema_version": "1.0.0",
        "partition_profile_id": partition_profile_id,
        "topology_profile_id": topology_profile_id,
        "chart_id": chart_id,
        "index_tuple": [int(value) for value in index_tuple],
        "refinement_level": int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": _as_map(payload.get("extensions")),
    }
    if not row["deterministic_fingerprint"]:
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _geo_sort_tuple(cell_key: Mapping[str, object] | None) -> tuple:
    row = _coerce_cell_key(cell_key) or {}
    chart_id = str(row.get("chart_id", "")).strip()
    index_tuple = [int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        chart_id,
        int(_as_int(row.get("refinement_level", 0), 0)),
        int(index_tuple[0]),
        int(index_tuple[1]),
        int(index_tuple[2]),
    )


def _normalized_extensions(extensions: Mapping[str, object] | None) -> dict:
    return dict((str(key), value) for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0])))


def _coerced_cell_key(cell_key: Mapping[str, object] | None) -> dict:
    return _coerce_cell_key(cell_key) or {}


def _semantic_geo_cell_key(cell_key: Mapping[str, object] | None) -> dict:
    row = _coerced_cell_key(cell_key)
    return _semantic_cell_key(row) if row else {}


def build_refinement_cache_key(
    *,
    universe_identity_hash: str,
    universe_contract_bundle_hash: str,
    generator_version_id: str,
    realism_profile_id: str,
    overlay_manifest_hash: str,
    mod_policy_id: str,
    geo_cell_key: Mapping[str, object] | None,
    refinement_level: int,
) -> str:
    return canonical_sha256(
        {
            "universe_identity_hash": str(universe_identity_hash or "").strip(),
            "universe_contract_bundle_hash": str(universe_contract_bundle_hash or "").strip(),
            "generator_version_id": str(generator_version_id or "").strip(),
            "realism_profile_id": str(realism_profile_id or "").strip(),
            "overlay_manifest_hash": str(overlay_manifest_hash or "").strip(),
            "mod_policy_id": str(mod_policy_id or "").strip(),
            "geo_cell_key": _semantic_geo_cell_key(geo_cell_key),
            "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        }
    )


def build_refinement_cache_entry(
    *,
    cache_key: str,
    geo_cell_key: Mapping[str, object] | None,
    refinement_level: int,
    last_used_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerced_cell_key(geo_cell_key)
    payload = {
        "cache_key": str(cache_key or "").strip(),
        "geo_cell_key": dict(cell_key),
        "refinement_level": int(max(0, _as_int(refinement_level, 0))),
        "last_used_tick": int(max(0, _as_int(last_used_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _normalized_extensions(extensions),
    }
    if not payload["cache_key"] or not payload["geo_cell_key"]:
        raise ValueError("cache_key and geo_cell_key are required")
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_refinement_cache_entry_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for raw in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("cache_key", ""))):
        try:
            normalized = build_refinement_cache_entry(
                cache_key=str(raw.get("cache_key", "")).strip(),
                geo_cell_key=_as_map(raw.get("geo_cell_key")),
                refinement_level=int(max(0, _as_int(raw.get("refinement_level", 0), 0))),
                last_used_tick=int(max(0, _as_int(raw.get("last_used_tick", 0), 0))),
                extensions=_as_map(raw.get("extensions")),
            )
        except ValueError:
            continue
        out[str(normalized.get("cache_key", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def touch_refinement_cache_entries(
    *,
    existing_rows: object,
    cache_key: str,
    geo_cell_key: Mapping[str, object] | None,
    refinement_level: int,
    current_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> List[dict]:
    merged = dict(
        (str(row.get("cache_key", "")).strip(), dict(row))
        for row in normalize_refinement_cache_entry_rows(existing_rows)
    )
    merged[str(cache_key or "").strip()] = build_refinement_cache_entry(
        cache_key=str(cache_key or "").strip(),
        geo_cell_key=geo_cell_key,
        refinement_level=int(max(0, _as_int(refinement_level, 0))),
        last_used_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=extensions,
    )
    return normalize_refinement_cache_entry_rows(list(merged.values()))


def evict_refinement_cache_entries(
    *,
    cache_entry_rows: object,
    max_entries_by_level: Mapping[int, int] | None = None,
) -> dict:
    rows = normalize_refinement_cache_entry_rows(cache_entry_rows)
    limits = dict(DEFAULT_REFINEMENT_CACHE_LIMITS)
    for key, value in sorted(_as_map(max_entries_by_level).items(), key=lambda item: int(_as_int(item[0], 0))):
        try:
            limits[int(key)] = int(max(0, _as_int(value, 0)))
        except (TypeError, ValueError):
            continue
    kept: List[dict] = []
    evicted: List[dict] = []
    rows_by_level: Dict[int, List[dict]] = {}
    for row in rows:
        level = int(max(0, _as_int(row.get("refinement_level", 0), 0)))
        rows_by_level.setdefault(level, []).append(dict(row))
    for level in sorted(rows_by_level.keys()):
        level_rows = sorted(
            rows_by_level[level],
            key=lambda item: (
                int(max(0, _as_int(item.get("last_used_tick", 0), 0))),
                str(item.get("cache_key", "")),
            ),
        )
        limit = int(max(0, _as_int(limits.get(level, 0), 0)))
        if limit <= 0:
            evicted.extend(dict(row) for row in level_rows)
            continue
        overflow = max(0, len(level_rows) - limit)
        evicted.extend(dict(row) for row in level_rows[:overflow])
        kept.extend(dict(row) for row in level_rows[overflow:])
    kept = sorted(
        kept,
        key=lambda item: (
            int(max(0, _as_int(item.get("refinement_level", 0), 0))),
            -int(max(0, _as_int(item.get("last_used_tick", 0), 0))),
            _geo_sort_tuple(item.get("geo_cell_key")),
            str(item.get("cache_key", "")),
        ),
    )
    evicted = sorted(
        evicted,
        key=lambda item: (
            int(max(0, _as_int(item.get("refinement_level", 0), 0))),
            int(max(0, _as_int(item.get("last_used_tick", 0), 0))),
            _geo_sort_tuple(item.get("geo_cell_key")),
            str(item.get("cache_key", "")),
        ),
    )
    payload = {
        "result": "complete",
        "cache_entry_rows": normalize_refinement_cache_entry_rows(kept),
        "evicted_rows": normalize_refinement_cache_entry_rows(evicted),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_REFINEMENT_CACHE_LIMITS",
    "build_refinement_cache_entry",
    "build_refinement_cache_key",
    "evict_refinement_cache_entries",
    "normalize_refinement_cache_entry_rows",
    "touch_refinement_cache_entries",
]
