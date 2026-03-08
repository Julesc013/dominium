"""Deterministic GEO-3 neighborhood enumeration engine."""

from __future__ import annotations

import itertools
from typing import List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import (
    _build_geo_cell_key,
    _cell_key_from_legacy_alias,
    _chart_id_from_legacy_token,
    _coerce_cell_key,
    _legacy_cell_alias,
    _legacy_chart_token,
    _semantic_cell_key,
)
from src.geo.kernel.geo_kernel import (
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_PARTITION_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_map,
    _format_atlas_cell_key,
    _format_grid_cell_key,
    _parse_atlas_cell_key,
    _parse_grid_cell_key,
    _partition_row,
    _periodic_coord,
    _periods_from_topology,
    _query_record,
    _topology_row,
)
from src.geo.metric.metric_cache import metric_cache_lookup, metric_cache_store


def _refusal(*, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": "refusal.geo.neighborhood_invalid",
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _chart_ids(topology_row: Mapping[str, object]) -> List[str]:
    out: List[str] = []
    for row in list(_as_map(topology_row).get("chart_definitions") or []):
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("chart_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


def _default_chart_id(topology_row: Mapping[str, object]) -> str:
    ids = _chart_ids(topology_row)
    return ids[0] if ids else "chart.global"


def _default_partition_profile_id(alias: str) -> str:
    token = str(alias or "").strip()
    if token.startswith("atlas."):
        return "geo.partition.sphere_tiles_stub"
    return _DEFAULT_PARTITION_PROFILE_ID


def _seed_legacy_template(
    *,
    alias: str,
    topology_profile_id: str,
    partition_profile_id: str,
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
) -> dict:
    token = str(alias or "").strip()
    partition_kind = str(_as_map(partition_row).get("partition_kind", "grid")).strip().lower() or "grid"
    chart_id = _default_chart_id(topology_row)
    index_tuple: List[int] = [0]
    if token.startswith("cell."):
        parsed = _parse_grid_cell_key(token)
        if parsed is None:
            return {}
        index_tuple = [int(value) for value in parsed]
    elif token.startswith("atlas."):
        parsed = _parse_atlas_cell_key(token)
        if parsed is None:
            return {}
        legacy_chart_id, u_idx, v_idx = parsed
        chart_id = _chart_id_from_legacy_token(
            legacy_chart_id=str(legacy_chart_id),
            topology_row=topology_row,
            fallback_chart_id=chart_id,
        )
        index_tuple = [int(u_idx), int(v_idx)]
    else:
        return {}
    return _build_geo_cell_key(
        partition_profile_id=str(partition_profile_id),
        topology_profile_id=str(topology_profile_id),
        chart_id=str(chart_id),
        index_tuple=index_tuple,
        refinement_level=0,
        partition_kind=partition_kind,
        legacy_cell_alias=token,
        extensions={"source": "GEO3-4"},
    )


def _canonical_cell_key(
    *,
    cell_key: object,
    topology_profile_id: str,
    partition_profile_id: str,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict | None:
    key_row = _coerce_cell_key(cell_key)
    if key_row is not None:
        return key_row
    alias = str(cell_key or "").strip()
    if not alias:
        return None
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_token = str(partition_profile_id or "").strip() or _default_partition_profile_id(alias)
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    if not topology_row or not partition_row:
        return None
    template = _seed_legacy_template(
        alias=alias,
        topology_profile_id=topology_token,
        partition_profile_id=partition_token,
        topology_row=topology_row,
        partition_row=partition_row,
    )
    if not template:
        return None
    return _cell_key_from_legacy_alias(
        alias=alias,
        template_cell_key=template,
        partition_row=partition_row,
        topology_row=topology_row,
    )


def _neighbor_args(
    radius: object,
    topology_profile_id: object,
    metric_profile_id: object,
    partition_profile_id: object,
) -> tuple[int, str, str, str]:
    radius_token = str(radius or "").strip()
    if radius_token.startswith("geo.topology."):
        return (
            int(max(0, _as_int(topology_profile_id, 0))),
            radius_token,
            str(metric_profile_id or "").strip(),
            str(partition_profile_id or "").strip(),
        )
    return (
        int(max(0, _as_int(radius, 0))),
        str(topology_profile_id or "").strip(),
        str(metric_profile_id or "").strip(),
        str(partition_profile_id or "").strip(),
    )


def _grid_distance_sq(offset: Sequence[int]) -> int:
    return int(sum(int(value) * int(value) for value in offset))


def _wrapped_delta_cells(delta: int, period: int) -> int:
    if int(period) <= 0:
        return int(delta)
    raw = int(delta) % int(period)
    if raw > (int(period) // 2):
        raw -= int(period)
    return int(raw)


def _grid_neighbors(
    *,
    cell_key_row: Mapping[str, object],
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
    radius: int,
) -> List[dict]:
    index_tuple = [int(value) for value in list(_as_map(cell_key_row).get("index_tuple") or [])]
    if not index_tuple:
        return []
    refinement_level = int(max(0, _as_int(_as_map(cell_key_row).get("refinement_level", 0), 0)))
    chart_id = str(_as_map(cell_key_row).get("chart_id", "")).strip() or _default_chart_id(topology_row)
    topology_profile_id = str(_as_map(cell_key_row).get("topology_profile_id", "")).strip()
    partition_profile_id = str(_as_map(cell_key_row).get("partition_profile_id", "")).strip()
    dimension = len(index_tuple)
    periods = _periods_from_topology(topology_row, dimension)
    while len(periods) < dimension:
        periods.append(0)
    boundary_rule_id = str(_as_map(topology_row).get("boundary_rule_id", "")).strip().lower()
    offsets = list(itertools.product(range(-int(radius), int(radius) + 1), repeat=dimension))
    neighbor_rows: List[tuple[int, dict]] = []
    for offset in offsets:
        if not any(int(value) != 0 for value in offset):
            continue
        effective_offset = [
            _wrapped_delta_cells(int(offset[idx]), int(periods[idx])) if "periodic" in boundary_rule_id else int(offset[idx])
            for idx in range(dimension)
        ]
        distance_sq = _grid_distance_sq(effective_offset)
        if distance_sq > int(radius * radius):
            continue
        next_index = [int(index_tuple[idx]) + int(offset[idx]) for idx in range(dimension)]
        if "periodic" in boundary_rule_id:
            next_index = [_periodic_coord(next_index[idx], periods[idx]) for idx in range(dimension)]
        neighbor_rows.append(
            (
                int(distance_sq),
                _build_geo_cell_key(
                    partition_profile_id=partition_profile_id,
                    topology_profile_id=topology_profile_id,
                    chart_id=chart_id,
                    index_tuple=next_index,
                    refinement_level=refinement_level,
                    partition_kind=str(_as_map(partition_row).get("partition_kind", "grid")).strip().lower() or "grid",
                    legacy_cell_alias=_format_grid_cell_key(next_index),
                    extensions={"source": "GEO3-4"},
                ),
            )
        )
    return [
        row
        for _, row in sorted(
            [
                (distance_sq, _coerce_cell_key(cell_key_row))
                for distance_sq, cell_key_row in neighbor_rows
                if _coerce_cell_key(cell_key_row) is not None
            ],
            key=lambda item: (
                int(item[0]),
                str(_as_map(item[1]).get("chart_id", "")),
                tuple(int(value) for value in list(_as_map(item[1]).get("index_tuple") or [])),
            ),
        )
        if row is not None
    ]


def _atlas_neighbor_ids(chart_id: str, u_idx: int, v_idx: int, atlas_resolution: int) -> List[tuple[str, int, int]]:
    seam_pair = {
        "chart.atlas.north": "chart.atlas.south",
        "chart.atlas.south": "chart.atlas.north",
    }
    out = []
    for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        next_chart = str(chart_id)
        next_u = int(u_idx + du)
        next_v = int(v_idx + dv)
        if next_u < 0 or next_u >= atlas_resolution or next_v < 0 or next_v >= atlas_resolution:
            next_chart = seam_pair.get(str(chart_id), str(chart_id))
            next_u = int(next_u % atlas_resolution)
            next_v = int(next_v % atlas_resolution)
        out.append((str(next_chart), int(next_u), int(next_v)))
    return sorted(set(out), key=lambda row: (str(row[0]), int(row[1]), int(row[2])))


def _atlas_neighbors(
    *,
    cell_key_row: Mapping[str, object],
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
    radius: int,
) -> List[dict]:
    index_tuple = [int(value) for value in list(_as_map(cell_key_row).get("index_tuple") or [])]
    if len(index_tuple) < 2:
        return []
    refinement_level = int(max(0, _as_int(_as_map(cell_key_row).get("refinement_level", 0), 0)))
    start_chart_id = str(_as_map(cell_key_row).get("chart_id", "")).strip() or _default_chart_id(topology_row)
    topology_profile_id = str(_as_map(cell_key_row).get("topology_profile_id", "")).strip()
    partition_profile_id = str(_as_map(cell_key_row).get("partition_profile_id", "")).strip()
    atlas_resolution = int(
        max(
            2,
            _as_int(
                _as_map(_as_map(topology_row).get("extensions")).get(
                    "atlas_resolution",
                    _as_map(_as_map(partition_row).get("parameters")).get("tile_resolution", 4),
                ),
                4,
            ),
        )
    )
    frontier = [(str(start_chart_id), int(index_tuple[0]), int(index_tuple[1]))]
    visited = {(str(start_chart_id), int(index_tuple[0]), int(index_tuple[1])): 0}
    for depth in range(1, int(max(0, radius)) + 1):
        next_frontier = []
        for chart_id, u_idx, v_idx in frontier:
            for neighbor in _atlas_neighbor_ids(chart_id, u_idx, v_idx, atlas_resolution):
                if neighbor in visited and int(visited[neighbor]) <= depth:
                    continue
                visited[neighbor] = depth
                next_frontier.append(neighbor)
        frontier = sorted(set(next_frontier), key=lambda row: (str(row[0]), int(row[1]), int(row[2])))
    neighbors = []
    for (chart_id, u_idx, v_idx), depth in sorted(
        visited.items(),
        key=lambda item: (int(item[1]), str(item[0][0]), int(item[0][1]), int(item[0][2])),
    ):
        if int(depth) <= 0:
            continue
        neighbors.append(
            _build_geo_cell_key(
                partition_profile_id=partition_profile_id,
                topology_profile_id=topology_profile_id,
                chart_id=str(chart_id),
                index_tuple=[int(u_idx), int(v_idx)],
                refinement_level=refinement_level,
                partition_kind=str(_as_map(partition_row).get("partition_kind", "atlas")).strip().lower() or "atlas",
                legacy_cell_alias=_format_atlas_cell_key(_legacy_chart_token(str(chart_id)), int(u_idx), int(v_idx)),
                extensions={"source": "GEO3-4", "atlas_distance": int(depth)},
            )
        )
    return [_coerce_cell_key(row) for row in neighbors if _coerce_cell_key(row) is not None]


def _cap_neighbors(
    rows: Sequence[Mapping[str, object]],
    *,
    partition_row: Mapping[str, object],
    explicit_max_neighbors: int | None,
) -> List[dict]:
    partition_max = int(max(1, _as_int(_as_map(_as_map(partition_row).get("extensions")).get("max_neighbors", 256), 256)))
    limit = partition_max
    if explicit_max_neighbors is not None:
        limit = min(limit, int(max(1, int(explicit_max_neighbors))))
    return [dict(row) for row in list(rows or [])[:limit]]


def geo_neighbors(
    cell_key: object,
    radius: int,
    topology_profile_id: str = "",
    metric_profile_id: str = "",
    partition_profile_id: str = "",
    *,
    chart_id: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    max_neighbors: int | None = None,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    cache_max_entries: int | None = None,
) -> dict:
    del metric_registry_payload
    radius_value, topology_arg, metric_arg, partition_arg = _neighbor_args(
        radius,
        topology_profile_id,
        metric_profile_id,
        partition_profile_id,
    )
    legacy_input = isinstance(cell_key, str)
    key_row = _canonical_cell_key(
        cell_key=cell_key,
        topology_profile_id=topology_arg,
        partition_profile_id=partition_arg,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if key_row is None:
        return _refusal(
            message="cell_key is invalid",
            details={
                "cell_key": str(cell_key),
                "chart_id": str(chart_id),
            },
        )
    topology_token = str(topology_arg or _as_map(key_row).get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_token = str(partition_arg or _as_map(key_row).get("partition_profile_id", "")).strip() or _DEFAULT_PARTITION_PROFILE_ID
    metric_token = str(metric_arg or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _refusal(message="topology_profile_id is missing", details={"topology_profile_id": topology_token})
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    if not partition_row:
        return _refusal(message="partition_profile_id is missing", details={"partition_profile_id": partition_token})
    radius_cap = int(max(0, _as_int(_as_map(_as_map(topology_row).get("extensions")).get("radius_cap", 8), 8)))
    radius_value = min(radius_value, radius_cap)
    partition_kind = str(_as_map(partition_row).get("partition_kind", "grid")).strip().lower() or "grid"
    if partition_kind in {"atlas", "sphere_tiles"}:
        canonical_neighbors = _atlas_neighbors(
            cell_key_row=key_row,
            topology_row=topology_row,
            partition_row=partition_row,
            radius=radius_value,
        )
    else:
        canonical_neighbors = _grid_neighbors(
            cell_key_row=key_row,
            topology_row=topology_row,
            partition_row=partition_row,
            radius=radius_value,
        )
    canonical_neighbors = _cap_neighbors(
        canonical_neighbors,
        partition_row=partition_row,
        explicit_max_neighbors=max_neighbors,
    )
    legacy_neighbors = [
        str(_as_map(row.get("extensions")).get("legacy_cell_alias", "")).strip() or _legacy_cell_alias(row, partition_kind)
        for row in canonical_neighbors
    ]
    seed = {
        "query_kind": "neighbors",
        "cell_key": _semantic_cell_key(key_row),
        "topology_profile_id": topology_token,
        "partition_profile_id": partition_token,
        "metric_profile_id": metric_token,
        "radius": int(radius_value),
        "legacy_input": bool(legacy_input),
        "engine_version": "GEO3-4",
    }
    cached = metric_cache_lookup(
        "geo.metric.neighbors",
        seed,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        version="GEO3-5",
    )
    if cached is not None:
        return cached
    outputs = {
        "count": len(canonical_neighbors),
        "neighbor_hashes": [canonical_sha256(_semantic_cell_key(row)) for row in canonical_neighbors],
    }
    payload = {
        "result": "complete",
        "query_kind": "neighbors",
        "cell_key": key_row,
        "topology_profile_id": topology_token,
        "partition_profile_id": partition_token,
        "metric_profile_id": metric_token,
        "radius": int(radius_value),
        "neighbors": legacy_neighbors if legacy_input else canonical_neighbors,
        "canonical_neighbors": canonical_neighbors,
        "legacy_neighbors": legacy_neighbors,
        "count": len(canonical_neighbors),
        "query_record": _query_record("neighbors", seed, outputs),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return metric_cache_store(
        "geo.metric.neighbors",
        seed,
        payload,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        version="GEO3-5",
        max_entries=cache_max_entries,
    )


__all__ = ["geo_neighbors"]
