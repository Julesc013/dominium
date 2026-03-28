"""Deterministic GEO-6 shard route planner for staged GEO path segments."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from geo.kernel.geo_kernel import _as_int, _as_map


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int]:
    row = _coerce_cell_key(value)
    if not row:
        return ("", tuple(), 0)
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(item) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
    )


def _geo_cell_key_hash(value: object) -> str:
    row = _coerce_cell_key(value)
    return canonical_sha256(_semantic_cell_key(row)) if row else ""


def resolve_cell_shard_id(
    cell_key: Mapping[str, object] | None,
    *,
    shard_assignment: Mapping[str, object] | None = None,
) -> str:
    row = _coerce_cell_key(cell_key)
    assignment = _as_map(shard_assignment)
    default_shard_id = str(assignment.get("default_shard_id", "shard.local")).strip() or "shard.local"
    if not row:
        return default_shard_id
    cell_hash = _geo_cell_key_hash(row)
    cell_shard_map = _as_map(assignment.get("cell_shard_map"))
    direct = str(cell_shard_map.get(cell_hash, "")).strip()
    if direct:
        return direct
    cells = list(assignment.get("cells") or [])
    for item in sorted((dict(entry) for entry in cells if isinstance(entry, Mapping)), key=lambda entry: canonical_sha256(entry)):
        mapped_key = _coerce_cell_key(item.get("geo_cell_key") or item.get("cell_key"))
        if mapped_key and _geo_cell_key_hash(mapped_key) == cell_hash:
            shard_id = str(item.get("shard_id", "")).strip()
            if shard_id:
                return shard_id
    ranges = list(assignment.get("cell_ranges") or [])
    for item in sorted((dict(entry) for entry in ranges if isinstance(entry, Mapping)), key=lambda entry: canonical_sha256(entry)):
        chart_id = str(item.get("chart_id", "")).strip()
        if chart_id and chart_id != str(row.get("chart_id", "")).strip():
            continue
        axis = int(max(0, _as_int(item.get("axis", 0), 0)))
        index_tuple = [int(value) for value in list(row.get("index_tuple") or [])]
        if axis >= len(index_tuple):
            continue
        start = int(_as_int(item.get("start", 0), 0))
        end = int(_as_int(item.get("end", start), start))
        observed = int(index_tuple[axis])
        if start <= observed <= end:
            shard_id = str(item.get("shard_id", "")).strip()
            if shard_id:
                return shard_id
    return default_shard_id


def build_shard_route_plan(
    *,
    request_id: str,
    path_cells: object,
    shard_assignment: Mapping[str, object] | None = None,
) -> dict:
    cells = [_coerce_cell_key(item) for item in list(path_cells or []) if _coerce_cell_key(item)]
    assignment = _as_map(shard_assignment)
    if not cells:
        payload = {
            "schema_version": "1.0.0",
            "request_id": str(request_id or "").strip(),
            "partitioned": False,
            "segments": [],
            "boundary_hops": [],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    segments: List[dict] = []
    boundary_hops: List[dict] = []
    current_segment: Dict[str, object] | None = None
    current_shard_id = ""
    for cell in cells:
        shard_id = resolve_cell_shard_id(cell, shard_assignment=assignment)
        if current_segment is None or shard_id != current_shard_id:
            if current_segment is not None:
                segments.append(dict(current_segment))
                boundary_hops.append(
                    {
                        "boundary_index": int(len(boundary_hops)),
                        "boundary_cell_key": dict(cell),
                        "from_shard_id": str(current_shard_id),
                        "to_shard_id": str(shard_id),
                    }
                )
            current_segment = {
                "segment_index": int(len(segments)),
                "shard_id": str(shard_id),
                "path_cells": [dict(cell)],
            }
            current_shard_id = str(shard_id)
        else:
            current_segment["path_cells"].append(dict(cell))
    if current_segment is not None:
        segments.append(dict(current_segment))

    normalized_segments = []
    for row in segments:
        normalized_segments.append(
            {
                "segment_index": int(_as_int(row.get("segment_index", 0), 0)),
                "shard_id": str(row.get("shard_id", "")).strip(),
                "path_cells": [dict(cell) for cell in (_coerce_cell_key(item) for item in list(row.get("path_cells") or [])) if cell],
            }
        )
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "partitioned": len(normalized_segments) > 1,
        "segments": sorted(normalized_segments, key=lambda item: int(_as_int(item.get("segment_index", 0), 0))),
        "boundary_hops": [
            {
                "boundary_index": int(_as_int(item.get("boundary_index", 0), 0)),
                "boundary_cell_key": dict(_coerce_cell_key(item.get("boundary_cell_key")) or {}),
                "from_shard_id": str(item.get("from_shard_id", "")).strip(),
                "to_shard_id": str(item.get("to_shard_id", "")).strip(),
            }
            for item in boundary_hops
        ],
        "deterministic_fingerprint": "",
        "extensions": {
            "default_shard_id": str(assignment.get("default_shard_id", "shard.local")).strip() or "shard.local",
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = ["build_shard_route_plan", "resolve_cell_shard_id"]
