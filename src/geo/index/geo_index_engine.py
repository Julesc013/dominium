"""Deterministic GEO-1 spatial indexing engine."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.kernel.geo_kernel import (
    REFUSAL_GEO_PROFILE_MISSING,
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_PARTITION_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_map,
    _cache_lookup,
    _cache_store,
    _dimension_from_topology,
    _format_atlas_cell_key,
    _format_grid_cell_key,
    _normalize_position,
    _partition_row,
    _periodic_coord,
    _periods_from_topology,
    _query_cache_key,
    _refusal,
    _topology_row,
    geo_neighbors,
)


REFUSAL_GEO_CELL_KEY_INVALID = "refusal.geo.cell_key_invalid"


def _missing_profile(*, profile_kind: str, profile_id: str) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_PROFILE_MISSING,
        "message": "{} '{}' is missing".format(str(profile_kind), str(profile_id)),
        "details": {
            "profile_kind": str(profile_kind),
            "profile_id": str(profile_id),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _chart_ids(topology_row: Mapping[str, object]) -> List[str]:
    out: List[str] = []
    for row in list(_as_map(topology_row).get("chart_definitions") or []):
        if not isinstance(row, Mapping):
            continue
        chart_id = str(row.get("chart_id", "")).strip()
        if chart_id:
            out.append(chart_id)
    return out


def _canonical_chart_id(
    *,
    coords: Sequence[int],
    topology_row: Mapping[str, object],
    partition_kind: str,
    chart_id: str,
) -> str:
    chart_token = str(chart_id or "").strip()
    ids = _chart_ids(topology_row)
    if chart_token and chart_token in ids:
        return chart_token
    if not ids:
        return "chart.global"
    if str(partition_kind) == "sphere_tiles":
        north_chart = next((item for item in ids if "north" in item), ids[0])
        south_chart = next((item for item in ids if "south" in item), ids[-1])
        return north_chart if int(coords[0] if coords else 0) >= 0 else south_chart
    return ids[0]


def _canonical_cell_key_seed(
    *,
    partition_profile_id: str,
    topology_profile_id: str,
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "partition_profile_id": str(partition_profile_id),
        "topology_profile_id": str(topology_profile_id),
        "chart_id": str(chart_id),
        "index_tuple": [int(value) for value in list(index_tuple)],
        "refinement_level": int(max(0, int(refinement_level))),
    }


def _build_geo_cell_key(
    *,
    partition_profile_id: str,
    topology_profile_id: str,
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int,
    partition_kind: str,
    legacy_cell_alias: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = _canonical_cell_key_seed(
        partition_profile_id=partition_profile_id,
        topology_profile_id=topology_profile_id,
        chart_id=chart_id,
        index_tuple=index_tuple,
        refinement_level=refinement_level,
    )
    payload["deterministic_fingerprint"] = ""
    payload["extensions"] = {
        "partition_kind": str(partition_kind),
        "legacy_cell_alias": str(legacy_cell_alias),
        **_as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _semantic_cell_key(cell_key: Mapping[str, object]) -> dict:
    return _canonical_cell_key_seed(
        partition_profile_id=str(_as_map(cell_key).get("partition_profile_id", "")),
        topology_profile_id=str(_as_map(cell_key).get("topology_profile_id", "")),
        chart_id=str(_as_map(cell_key).get("chart_id", "")),
        index_tuple=list(_as_map(cell_key).get("index_tuple") or []),
        refinement_level=_as_int(_as_map(cell_key).get("refinement_level", 0), 0),
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


def _legacy_chart_token(chart_id: str) -> str:
    token = str(chart_id or "").strip()
    if "north" in token:
        return "north"
    if "south" in token:
        return "south"
    return token.replace(".", "_") or "default"


def _chart_id_from_legacy_token(*, legacy_chart_id: str, topology_row: Mapping[str, object], fallback_chart_id: str) -> str:
    token = str(legacy_chart_id or "").strip()
    ids = _chart_ids(topology_row)
    if token in ids:
        return token
    if token == "north":
        return next((item for item in ids if "north" in item), str(fallback_chart_id or ids[0] if ids else fallback_chart_id))
    if token == "south":
        return next((item for item in ids if "south" in item), str(fallback_chart_id or ids[-1] if ids else fallback_chart_id))
    for candidate in ids:
        if candidate.replace(".", "_") == token:
            return candidate
    return str(fallback_chart_id or (ids[0] if ids else "chart.global"))


def _legacy_cell_alias(cell_key: Mapping[str, object], partition_kind: str) -> str:
    payload = _as_map(cell_key)
    index_tuple = [int(value) for value in list(payload.get("index_tuple") or [])]
    if str(partition_kind) in {"atlas", "sphere_tiles"}:
        u_idx = int(index_tuple[0] if len(index_tuple) > 0 else 0)
        v_idx = int(index_tuple[1] if len(index_tuple) > 1 else 0)
        return _format_atlas_cell_key(_legacy_chart_token(str(payload.get("chart_id", ""))), u_idx, v_idx)
    return _format_grid_cell_key(index_tuple)


def _floor_div_index(value: object, divisor: int) -> int:
    return int(_as_int(value, 0)) // int(max(1, _as_int(divisor, 1)))


def _grid_index_tuple(
    *,
    coords: Sequence[int],
    partition_row: Mapping[str, object],
    topology_row: Mapping[str, object],
    refinement_level: int,
) -> List[int]:
    params = _as_map(partition_row.get("parameters"))
    cell_size_mm = max(1, _as_int(params.get("cell_size_mm", 10000), 10000))
    scale = 1 << int(max(0, int(refinement_level)))
    effective_cell_size = max(1, cell_size_mm // scale)
    out = [_floor_div_index(value, effective_cell_size) for value in coords]
    boundary_rule_id = str(_as_map(topology_row).get("boundary_rule_id", "")).strip().lower()
    if "periodic" in boundary_rule_id:
        periods = _periods_from_topology(topology_row, len(out))
        while len(periods) < len(out):
            periods.append(0)
        out = [_periodic_coord(out[idx], periods[idx]) for idx in range(len(out))]
    return out


def _tree_index_tuple(
    *,
    coords: Sequence[int],
    partition_row: Mapping[str, object],
    refinement_level: int,
) -> List[int]:
    params = _as_map(partition_row.get("parameters"))
    root_extent_mm = max(1, _as_int(params.get("root_extent_mm", 1000000), 1000000))
    scale = 1 << int(max(0, int(refinement_level)))
    cell_span = max(1, root_extent_mm // scale)
    return [_floor_div_index(value, cell_span) for value in coords]


def _atlas_index_tuple(
    *,
    coords: Sequence[int],
    partition_row: Mapping[str, object],
    topology_row: Mapping[str, object],
    chart_id: str,
    refinement_level: int,
) -> List[int]:
    del topology_row
    params = _as_map(partition_row.get("parameters"))
    tile_resolution = max(1, _as_int(params.get("tile_resolution", params.get("cell_size_mm", 256)), 256))
    scale = 1 << int(max(0, int(refinement_level)))
    cell_size = max(1, tile_resolution // scale)
    u_idx = _floor_div_index(coords[0] if coords else 0, cell_size)
    v_idx = _floor_div_index(coords[1] if len(coords) > 1 else 0, cell_size)
    if str(chart_id).strip():
        return [u_idx, v_idx]
    return [u_idx, v_idx]


def _sphere_tile_index_tuple(
    *,
    coords: Sequence[int],
    partition_row: Mapping[str, object],
    chart_id: str,
    refinement_level: int,
) -> List[int]:
    params = _as_map(partition_row.get("parameters"))
    subdivision_level = max(0, _as_int(params.get("subdivision_level", 2), 2))
    tiles_per_axis = max(1, 1 << int(subdivision_level + max(0, int(refinement_level))))
    lat_mdeg = int(coords[0] if coords else 0)
    lon_mdeg = int(coords[1] if len(coords) > 1 else 0)
    lon_norm = int((lon_mdeg + 180000) % 360000)
    if "south" in str(chart_id):
        local_lat = max(0, min(90000, -lat_mdeg))
    else:
        local_lat = max(0, min(90000, lat_mdeg))
    u_idx = min(tiles_per_axis - 1, int((lon_norm * tiles_per_axis) // 360000))
    v_idx = min(tiles_per_axis - 1, int((local_lat * tiles_per_axis) // 90000))
    return [u_idx, v_idx]


def geo_cell_key_from_position(
    pos: Mapping[str, object] | None,
    topology_profile_id: str,
    partition_profile_id: str,
    chart_id: str,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_token = str(partition_profile_id or "").strip() or _DEFAULT_PARTITION_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    if not partition_row:
        return _missing_profile(profile_kind="partition_profile_id", profile_id=partition_token)

    dimension = _dimension_from_topology(topology_row)
    coords = _normalize_position(pos, dimension)
    params = _as_map(partition_row.get("parameters"))
    partition_kind = str(partition_row.get("partition_kind", "grid")).strip().lower()
    refinement_level = int(max(0, _as_int(_as_map(pos).get("refinement_level", params.get("default_refinement_level", 0)), 0)))
    chart_token = _canonical_chart_id(
        coords=coords,
        topology_row=topology_row,
        partition_kind=partition_kind,
        chart_id=chart_id or str(_as_map(pos).get("chart_id", "")),
    )
    seed = {
        "query_kind": "geo_cell_key_from_position",
        "topology_profile_id": topology_token,
        "partition_profile_id": partition_token,
        "chart_id": chart_token,
        "coords": list(coords),
        "refinement_level": refinement_level,
    }
    cache_key = _query_cache_key("geo_cell_key_from_position", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    if partition_kind == "sphere_tiles":
        index_tuple = _sphere_tile_index_tuple(
            coords=coords,
            partition_row=partition_row,
            chart_id=chart_token,
            refinement_level=refinement_level,
        )
    elif partition_kind == "atlas":
        index_tuple = _atlas_index_tuple(
            coords=coords,
            partition_row=partition_row,
            topology_row=topology_row,
            chart_id=chart_token,
            refinement_level=refinement_level,
        )
    elif partition_kind in {"octree", "quadtree"}:
        spatial_dimension = 3 if partition_kind == "octree" else 2
        index_tuple = _tree_index_tuple(
            coords=coords[:spatial_dimension],
            partition_row=partition_row,
            refinement_level=refinement_level,
        )
    else:
        index_tuple = _grid_index_tuple(
            coords=coords,
            partition_row=partition_row,
            topology_row=topology_row,
            refinement_level=refinement_level,
        )

    cell_key = _build_geo_cell_key(
        partition_profile_id=partition_token,
        topology_profile_id=topology_token,
        chart_id=chart_token,
        index_tuple=index_tuple,
        refinement_level=refinement_level,
        partition_kind=partition_kind,
        legacy_cell_alias="",
        extensions={"source": "GEO1-4"},
    )
    legacy_cell_alias = _legacy_cell_alias(cell_key, partition_kind)
    cell_key = _build_geo_cell_key(
        partition_profile_id=partition_token,
        topology_profile_id=topology_token,
        chart_id=chart_token,
        index_tuple=index_tuple,
        refinement_level=refinement_level,
        partition_kind=partition_kind,
        legacy_cell_alias=legacy_cell_alias,
        extensions={"source": "GEO1-4"},
    )
    payload = {
        "result": "complete",
        "topology_profile_id": topology_token,
        "partition_profile_id": partition_token,
        "partition_kind": partition_kind,
        "chart_id": chart_token,
        "cell_key": cell_key,
        "legacy_cell_alias": legacy_cell_alias,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def _cell_key_from_legacy_alias(
    *,
    alias: str,
    template_cell_key: Mapping[str, object],
    partition_row: Mapping[str, object],
    topology_row: Mapping[str, object],
) -> dict | None:
    token = str(alias or "").strip()
    template = _coerce_cell_key(template_cell_key)
    if template is None:
        return None
    partition_kind = str(_as_map(partition_row).get("partition_kind", "grid")).strip().lower()
    if str(partition_kind) in {"atlas", "sphere_tiles"}:
        parts = token.split(".")
        if len(parts) != 4 or parts[0] != "atlas":
            return None
        try:
            chart_id = _chart_id_from_legacy_token(
                legacy_chart_id=str(parts[1]),
                topology_row=topology_row,
                fallback_chart_id=str(template.get("chart_id", "")),
            )
            index_tuple = [int(parts[2]), int(parts[3])]
        except ValueError:
            return None
    else:
        if not token.startswith("cell."):
            return None
        parts = token.split(".")[1:]
        try:
            index_tuple = [int(part) for part in parts]
        except ValueError:
            return None
        chart_id = str(template.get("chart_id", ""))
    return _build_geo_cell_key(
        partition_profile_id=str(template.get("partition_profile_id", "")),
        topology_profile_id=str(template.get("topology_profile_id", "")),
        chart_id=chart_id,
        index_tuple=index_tuple,
        refinement_level=_as_int(template.get("refinement_level", 0), 0),
        partition_kind=partition_kind,
        legacy_cell_alias=token,
        extensions={"source": "GEO1-4"},
    )


def geo_cell_key_neighbors(
    cell_key: Mapping[str, object] | None,
    radius: int,
    *,
    metric_profile_id: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    key_row = _coerce_cell_key(cell_key)
    if key_row is None:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_GEO_CELL_KEY_INVALID,
            "message": "cell_key is invalid",
            "deterministic_fingerprint": canonical_sha256(
                {
                    "result": "refused",
                    "refusal_code": REFUSAL_GEO_CELL_KEY_INVALID,
                    "message": "cell_key is invalid",
                    "deterministic_fingerprint": "",
                }
            ),
        }
    partition_row = _partition_row(str(key_row.get("partition_profile_id", "")), registry_payload=partition_registry_payload)
    if not partition_row:
        return _missing_profile(
            profile_kind="partition_profile_id",
            profile_id=str(key_row.get("partition_profile_id", "")),
        )
    topology_row = _topology_row(str(key_row.get("topology_profile_id", "")), registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(
            profile_kind="topology_profile_id",
            profile_id=str(key_row.get("topology_profile_id", "")),
        )
    topology_token = str(key_row.get("topology_profile_id", "")).strip()
    metric_token = str(metric_profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    legacy_alias = str(_as_map(key_row.get("extensions")).get("legacy_cell_alias", "")).strip() or _legacy_cell_alias(
        key_row,
        str(partition_row.get("partition_kind", "grid")),
    )
    seed = {
        "query_kind": "geo_cell_key_neighbors",
        "cell_key": _semantic_cell_key(key_row),
        "radius": int(max(0, int(radius))),
        "metric_profile_id": metric_token,
    }
    cache_key = _query_cache_key("geo_cell_key_neighbors", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    neighbor_payload = geo_neighbors(
        legacy_alias,
        topology_token,
        int(radius),
        metric_token,
        topology_registry_payload=topology_registry_payload,
        metric_registry_payload=metric_registry_payload,
    )
    if str(neighbor_payload.get("result", "")) != "complete":
        return neighbor_payload
    neighbors = []
    for alias in list(neighbor_payload.get("neighbors") or []):
        row = _cell_key_from_legacy_alias(
            alias=str(alias),
            template_cell_key=key_row,
            partition_row=partition_row,
            topology_row=topology_row,
        )
        if row is not None:
            neighbors.append(row)
    payload = {
        "result": "complete",
        "cell_key": key_row,
        "radius": int(max(0, int(radius))),
        "neighbors": neighbors,
        "legacy_neighbors": list(neighbor_payload.get("neighbors") or []),
        "count": len(neighbors),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def _refined_index_tuple(
    *,
    cell_key: Mapping[str, object],
    partition_row: Mapping[str, object],
    target_refinement_level: int,
) -> List[int]:
    current_level = int(max(0, _as_int(_as_map(cell_key).get("refinement_level", 0), 0)))
    delta = int(target_refinement_level) - current_level
    if delta <= 0:
        return [int(value) for value in list(_as_map(cell_key).get("index_tuple") or [])]
    params = _as_map(partition_row.get("parameters"))
    branch_factor = max(2, _as_int(params.get("refinement_branch_factor", 2), 2))
    scale = int(branch_factor**delta)
    return [int(value) * scale for value in list(_as_map(cell_key).get("index_tuple") or [])]


def geo_refine_cell_key(
    cell_key: Mapping[str, object] | None,
    target_refinement_level: int,
    *,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    key_row = _coerce_cell_key(cell_key)
    if key_row is None:
        return _refusal(message="cell_key is invalid")
    partition_row = _partition_row(str(key_row.get("partition_profile_id", "")), registry_payload=partition_registry_payload)
    if not partition_row:
        return _missing_profile(
            profile_kind="partition_profile_id",
            profile_id=str(key_row.get("partition_profile_id", "")),
        )
    current_level = int(max(0, _as_int(key_row.get("refinement_level", 0), 0)))
    target_level = int(max(0, int(target_refinement_level)))
    if target_level < current_level:
        return _refusal(
            message="target_refinement_level must be >= current refinement_level",
            details={
                "current_refinement_level": current_level,
                "target_refinement_level": target_level,
            },
        )
    partition_kind = str(partition_row.get("partition_kind", "grid")).strip().lower()
    seed = {
        "query_kind": "geo_refine_cell_key",
        "cell_key": _semantic_cell_key(key_row),
        "target_refinement_level": target_level,
    }
    cache_key = _query_cache_key("geo_refine_cell_key", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    index_tuple = _refined_index_tuple(
        cell_key=key_row,
        partition_row=partition_row,
        target_refinement_level=target_level,
    )
    child_cell_key = _build_geo_cell_key(
        partition_profile_id=str(key_row.get("partition_profile_id", "")),
        topology_profile_id=str(key_row.get("topology_profile_id", "")),
        chart_id=str(key_row.get("chart_id", "")),
        index_tuple=index_tuple,
        refinement_level=target_level,
        partition_kind=partition_kind,
        legacy_cell_alias="",
        extensions={"source": "GEO1-4"},
    )
    child_alias = _legacy_cell_alias(child_cell_key, partition_kind)
    child_cell_key = _build_geo_cell_key(
        partition_profile_id=str(key_row.get("partition_profile_id", "")),
        topology_profile_id=str(key_row.get("topology_profile_id", "")),
        chart_id=str(key_row.get("chart_id", "")),
        index_tuple=index_tuple,
        refinement_level=target_level,
        partition_kind=partition_kind,
        legacy_cell_alias=child_alias,
        extensions={"source": "GEO1-4"},
    )
    relation = {
        "schema_version": "1.0.0",
        "parent_cell_key": key_row,
        "child_cell_key": child_cell_key,
        "deterministic_fingerprint": "",
        "extensions": {
            "partition_kind": partition_kind,
            "source": "GEO1-4",
        },
    }
    relation["deterministic_fingerprint"] = canonical_sha256(dict(relation, deterministic_fingerprint=""))
    payload = {
        "result": "complete",
        "partition_kind": partition_kind,
        "parent_cell_key": key_row,
        "child_cell_key": child_cell_key,
        "relation": relation,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)
