"""Deterministic GEO-6 path engine over topology-aware GEO cell graphs."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.domain_adapters import field_sampling_cell_key
from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key, geo_cell_key_from_position, geo_refine_cell_key
from src.geo.kernel.geo_kernel import (
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_PARTITION_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_list,
    _as_map,
    _dimension_from_topology,
    _metric_row,
    _partition_row,
    _query_record,
    _repo_root,
    _topology_row,
)
from src.geo.metric.metric_engine import geo_distance
from src.geo.metric.neighborhood_engine import geo_neighbors
from src.geo.path.shard_route_planner import build_shard_route_plan


REFUSAL_GEO_PATH_INVALID = "refusal.geo.path_invalid"
REFUSAL_GEO_PATH_NOT_FOUND = "refusal.geo.path_not_found"
REFUSAL_GEO_PATH_BOUNDED = "refusal.geo.path_bounded"

_TRAVERSAL_POLICY_REGISTRY_REL = os.path.join("data", "registries", "traversal_policy_registry.json")


def _load_json(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), rel_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, ValueError, TypeError):
        return {}


def _traversal_policy_registry_payload(registry_payload: Mapping[str, object] | None = None) -> dict:
    return _as_map(registry_payload) or _load_json(_TRAVERSAL_POLICY_REGISTRY_REL)


def traversal_policy_registry_hash(registry_payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_traversal_policy_registry_payload(registry_payload))


def _rows_from_registry(payload: Mapping[str, object] | None, row_key: str) -> List[dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    rows = record.get(row_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _traversal_policy_row(
    traversal_policy_id: str,
    registry_payload: Mapping[str, object] | None = None,
) -> dict:
    token = str(traversal_policy_id or "").strip()
    rows = _rows_from_registry(_traversal_policy_registry_payload(registry_payload), "traversal_policies")
    by_id: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("traversal_policy_id", ""))):
        row_id = str(row.get("traversal_policy_id", "")).strip()
        if row_id:
            by_id[row_id] = dict(row)
    return dict(by_id.get(token) or {})


def _sorted_unique_strings(values: object) -> List[str]:
    return sorted(set(str(item).strip() for item in _as_list(values) if str(item).strip()))


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


def _refusal(
    *,
    refusal_code: str,
    message: str,
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(refusal_code),
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_traversal_policy(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    traversal_policy_id = str(payload.get("traversal_policy_id", "")).strip()
    if not traversal_policy_id:
        raise ValueError("traversal_policy_id is required")
    infrastructure_preference = payload.get("infrastructure_preference")
    if infrastructure_preference is None:
        infrastructure_preference = {}
    if not isinstance(infrastructure_preference, Mapping):
        infrastructure_preference = {"overlay_kind": str(infrastructure_preference)}
    normalized = {
        "schema_version": "1.0.0",
        "traversal_policy_id": traversal_policy_id,
        "allowed_neighbor_kinds": _sorted_unique_strings(payload.get("allowed_neighbor_kinds")),
        "cost_weights": {
            str(key): int(_as_int(value, 0))
            for key, value in sorted(_as_map(payload.get("cost_weights")).items(), key=lambda item: str(item[0]))
        },
        "infrastructure_preference": {
            str(key): value
            for key, value in sorted(_as_map(infrastructure_preference).items(), key=lambda item: str(item[0]))
        },
        "max_expansions": int(max(1, _as_int(payload.get("max_expansions", 128), 128))),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    if not normalized["deterministic_fingerprint"]:
        normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def build_path_request(
    *,
    request_id: str,
    start_ref: Mapping[str, object],
    goal_ref: Mapping[str, object],
    traversal_policy_id: str,
    tier_mode: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "start_ref": dict(start_ref or {}),
        "goal_ref": dict(goal_ref or {}),
        "traversal_policy_id": str(traversal_policy_id or "").strip(),
        "tier_mode": str(tier_mode or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    return normalize_path_request(payload)


def normalize_path_request(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    request_id = str(payload.get("request_id", "")).strip()
    traversal_policy_id = str(payload.get("traversal_policy_id", "")).strip()
    tier_mode = str(payload.get("tier_mode", "")).strip().lower()
    if not request_id or not traversal_policy_id or tier_mode not in {"macro", "meso", "micro"}:
        raise ValueError("request_id, traversal_policy_id, and tier_mode are required")
    normalized = {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "start_ref": dict(_as_map(payload.get("start_ref"))),
        "goal_ref": dict(_as_map(payload.get("goal_ref"))),
        "traversal_policy_id": traversal_policy_id,
        "tier_mode": tier_mode,
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    if not normalized["deterministic_fingerprint"]:
        normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def path_request_hash(path_request: Mapping[str, object] | None) -> str:
    return canonical_sha256(normalize_path_request(path_request))


def _target_refinement_level(
    *,
    endpoint_ref: Mapping[str, object],
    tier_mode: str,
    partition_row: Mapping[str, object],
    current_cell_key: Mapping[str, object] | None = None,
) -> int:
    endpoint = _as_map(endpoint_ref)
    ext = _as_map(endpoint.get("extensions"))
    if current_cell_key:
        current_level = int(max(0, _as_int(_as_map(current_cell_key).get("refinement_level", 0), 0)))
        if "target_refinement_level" in endpoint:
            return int(max(0, _as_int(endpoint.get("target_refinement_level", current_level), current_level)))
        if "target_refinement_level" in ext:
            return int(max(0, _as_int(ext.get("target_refinement_level", current_level), current_level)))
        if str(tier_mode) == "macro" and "macro_target_refinement_level" in ext:
            return int(max(0, _as_int(ext.get("macro_target_refinement_level", current_level), current_level)))
        return current_level
    params = _as_map(partition_row.get("parameters"))
    default_level = int(max(0, _as_int(params.get("default_refinement_level", 0), 0)))
    if "target_refinement_level" in endpoint:
        return int(max(0, _as_int(endpoint.get("target_refinement_level", default_level), default_level)))
    if "target_refinement_level" in ext:
        return int(max(0, _as_int(ext.get("target_refinement_level", default_level), default_level)))
    if str(tier_mode) == "micro":
        return int(max(0, _as_int(ext.get("micro_target_refinement_level", default_level), default_level)))
    if str(tier_mode) == "macro":
        return int(max(0, _as_int(ext.get("macro_target_refinement_level", default_level), default_level)))
    return default_level


def _coarsen_cell_key(
    cell_key: Mapping[str, object],
    *,
    partition_row: Mapping[str, object],
    target_refinement_level: int,
) -> dict:
    row = _coerce_cell_key(cell_key)
    if not row:
        return {}
    current_level = int(max(0, _as_int(row.get("refinement_level", 0), 0)))
    target_level = int(max(0, int(target_refinement_level)))
    if target_level >= current_level:
        return dict(row)
    params = _as_map(partition_row.get("parameters"))
    branch_factor = int(max(2, _as_int(params.get("refinement_branch_factor", 2), 2)))
    delta = int(current_level - target_level)
    scale = int(branch_factor**delta)
    return {
        "schema_version": "1.0.0",
        "partition_profile_id": str(row.get("partition_profile_id", "")).strip(),
        "topology_profile_id": str(row.get("topology_profile_id", "")).strip(),
        "chart_id": str(row.get("chart_id", "")).strip(),
        "index_tuple": [int(value) // scale for value in list(row.get("index_tuple") or [])],
        "refinement_level": target_level,
        "deterministic_fingerprint": "",
        "extensions": dict(_as_map(row.get("extensions"))),
    }


def _tier_cell_key(
    cell_key: Mapping[str, object],
    *,
    target_refinement_level: int,
    partition_row: Mapping[str, object],
) -> dict:
    row = _coerce_cell_key(cell_key)
    if not row:
        return {}
    current_level = int(max(0, _as_int(row.get("refinement_level", 0), 0)))
    target_level = int(max(0, int(target_refinement_level)))
    if target_level == current_level:
        return row
    if target_level > current_level:
        refined = geo_refine_cell_key(row, target_level, partition_registry_payload={"record": {"partition_profiles": [dict(partition_row)]}})
        return _coerce_cell_key(_as_map(refined.get("child_cell_key")))
    return _coarsen_cell_key(row, partition_row=partition_row, target_refinement_level=target_level)


def _position_ref_cell_key(
    *,
    endpoint_ref: Mapping[str, object],
    topology_profile_id: str,
    partition_profile_id: str,
    tier_mode: str,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str,
    topology_registry_payload: Mapping[str, object] | None,
    partition_registry_payload: Mapping[str, object] | None,
) -> dict:
    endpoint = _as_map(endpoint_ref)
    ext = _as_map(endpoint.get("extensions"))
    partition_row = _partition_row(partition_profile_id, registry_payload=partition_registry_payload)
    target_level = _target_refinement_level(endpoint_ref=endpoint, tier_mode=tier_mode, partition_row=partition_row)
    position_ref = _as_map(endpoint.get("position_ref")) or (
        dict(endpoint) if ("frame_id" in endpoint and ("local_position" in endpoint or "coords" in endpoint)) else {}
    )
    if frame_nodes and frame_transform_rows and position_ref:
        target_frame_id = str(endpoint.get("target_frame_id", "")).strip() or str(position_ref.get("frame_id", "")).strip()
        cell_payload = field_sampling_cell_key(
            position_ref,
            target_frame_id,
            partition_profile_id,
            frame_nodes=frame_nodes,
            frame_transform_rows=frame_transform_rows,
            graph_version=graph_version,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
        cell_key = _coerce_cell_key(_as_map(cell_payload.get("cell_key")))
        if cell_key:
            return _tier_cell_key(cell_key, target_refinement_level=target_level, partition_row=partition_row)
    coords = _as_list(position_ref.get("local_position"))
    if not coords:
        coords = _as_list(endpoint.get("coords"))
    chart_id = str(endpoint.get("chart_id", "")).strip() or str(ext.get("chart_id", "")).strip() or "chart.global.r3"
    payload = {
        "coords": [int(_as_int(value, 0)) for value in coords],
        "refinement_level": target_level,
    }
    cell_payload = geo_cell_key_from_position(
        payload,
        topology_profile_id,
        partition_profile_id,
        chart_id,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    return _coerce_cell_key(_as_map(cell_payload.get("cell_key")))


def _endpoint_cell_key(
    *,
    endpoint_ref: Mapping[str, object],
    topology_profile_id: str,
    partition_profile_id: str,
    tier_mode: str,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str,
    topology_registry_payload: Mapping[str, object] | None,
    partition_registry_payload: Mapping[str, object] | None,
) -> dict:
    endpoint = _as_map(endpoint_ref)
    direct = _coerce_cell_key(endpoint) or _coerce_cell_key(endpoint.get("geo_cell_key")) or _coerce_cell_key(endpoint.get("cell_key"))
    partition_row = _partition_row(partition_profile_id, registry_payload=partition_registry_payload)
    if direct:
        target_level = _target_refinement_level(
            endpoint_ref=endpoint,
            tier_mode=tier_mode,
            partition_row=partition_row,
            current_cell_key=direct,
        )
        return _tier_cell_key(direct, target_refinement_level=target_level, partition_row=partition_row)
    return _position_ref_cell_key(
        endpoint_ref=endpoint,
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        tier_mode=tier_mode,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )


def _cell_center_position(
    cell_key: Mapping[str, object],
    *,
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
) -> dict:
    row = _coerce_cell_key(cell_key)
    if not row:
        return {"coords": []}
    params = _as_map(partition_row.get("parameters"))
    kind = str(partition_row.get("partition_kind", "grid")).strip().lower() or "grid"
    index_tuple = [int(value) for value in list(row.get("index_tuple") or [])]
    dimension = max(1, _dimension_from_topology(topology_row))
    refinement_level = int(max(0, _as_int(row.get("refinement_level", 0), 0)))
    coords: List[int] = []
    if kind in {"sphere_tiles", "atlas"}:
        u_idx = int(index_tuple[0] if len(index_tuple) > 0 else 0)
        v_idx = int(index_tuple[1] if len(index_tuple) > 1 else 0)
        if kind == "sphere_tiles":
            subdivision = int(max(0, _as_int(params.get("subdivision_level", 2), 2)))
            tiles_per_axis = int(max(1, 1 << int(subdivision + refinement_level)))
            lon_span = max(1, 360000 // tiles_per_axis)
            lat_span = max(1, 90000 // tiles_per_axis)
            lon_center = -180000 + (u_idx * lon_span) + (lon_span // 2)
            local_lat = (v_idx * lat_span) + (lat_span // 2)
            if "south" in str(row.get("chart_id", "")).lower():
                lat_center = -local_lat
            else:
                lat_center = local_lat
            coords = [int(lat_center), int(lon_center)]
        else:
            tile_resolution = int(max(1, _as_int(params.get("tile_resolution", 256), 256)))
            cell_span = max(1, tile_resolution // max(1, 1 << refinement_level))
            coords = [int((u_idx * cell_span) + (cell_span // 2)), int((v_idx * cell_span) + (cell_span // 2))]
    elif kind in {"octree", "quadtree"}:
        root_extent = int(max(1, _as_int(params.get("root_extent_mm", 1000000), 1000000)))
        cell_span = max(1, root_extent // max(1, 1 << refinement_level))
        coords = [int((value * cell_span) + (cell_span // 2)) for value in index_tuple]
    else:
        cell_size = int(max(1, _as_int(params.get("cell_size_mm", 10000), 10000)))
        cell_span = max(1, cell_size // max(1, 1 << refinement_level))
        coords = [int((value * cell_span) + (cell_span // 2)) for value in index_tuple]
    while len(coords) < dimension:
        coords.append(0)
    return {"coords": coords[:dimension]}


def _transition_neighbor_kinds(current_cell: Mapping[str, object], neighbor_cell: Mapping[str, object]) -> List[str]:
    current_row = _coerce_cell_key(current_cell)
    neighbor_row = _coerce_cell_key(neighbor_cell)
    if not current_row or not neighbor_row:
        return []
    kinds = {"neighbor.metric_radius"}
    current_index = tuple(int(item) for item in list(current_row.get("index_tuple") or []))
    neighbor_index = tuple(int(item) for item in list(neighbor_row.get("index_tuple") or []))
    if len(current_index) == len(neighbor_index):
        manhattan = sum(abs(neighbor_index[idx] - current_index[idx]) for idx in range(len(current_index)))
        if manhattan == 1:
            kinds.add("neighbor.cardinal")
    if (
        str(current_row.get("chart_id", "")).strip() != str(neighbor_row.get("chart_id", "")).strip()
        or sum(abs(neighbor_index[idx] - current_index[idx]) for idx in range(min(len(current_index), len(neighbor_index)))) > 1
    ):
        kinds.add("neighbor.portal")
    return sorted(kinds)


def _policy_allows_neighbor(policy_row: Mapping[str, object], current_cell: Mapping[str, object], neighbor_cell: Mapping[str, object]) -> bool:
    allowed = _sorted_unique_strings(policy_row.get("allowed_neighbor_kinds"))
    if not allowed:
        return True
    observed = _transition_neighbor_kinds(current_cell, neighbor_cell)
    return any(token in observed for token in allowed)


def _field_cost_modifier(
    *,
    current_cell: Mapping[str, object],
    neighbor_cell: Mapping[str, object],
    policy_row: Mapping[str, object],
    field_cost_data: Mapping[str, object] | None,
) -> tuple[int, dict]:
    payload = _as_map(field_cost_data)
    field_scale = int(max(0, _as_int(_as_map(policy_row.get("cost_weights")).get("field_cost", 0), 0)))
    if (not payload) or field_scale <= 0:
        return (0, {})
    terms = list(payload.get("field_terms") or [])
    if not terms:
        terms = [{"field_id": token, "weight": 1, "sample_from": "neighbor"} for token in _sorted_unique_strings(payload.get("field_ids"))]
    normalized_terms = []
    for row in sorted((dict(item) for item in terms if isinstance(item, Mapping)), key=lambda item: str(item.get("field_id", ""))):
        field_id = str(row.get("field_id", "")).strip()
        if not field_id:
            continue
        normalized_terms.append(
            {
                "field_id": field_id,
                "weight": int(max(1, _as_int(row.get("weight", 1), 1))),
                "sample_from": str(row.get("sample_from", "neighbor")).strip().lower() or "neighbor",
            }
        )
    if not normalized_terms:
        return (0, {})

    def _scalar_value(value: object) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, list):
            return int(sum(abs(_as_int(item, 0)) for item in value))
        if isinstance(value, Mapping):
            coords = _as_list(_as_map(value).get("coords"))
            if coords:
                return int(sum(abs(_as_int(item, 0)) for item in coords))
            return int(sum(abs(_as_int(item, 0)) for item in _as_map(value).values() if isinstance(item, (int, float))))
        return int(_as_int(value, 0))

    def _direct_value(field_id: str, cell_key: Mapping[str, object]) -> object:
        values_by_field_id = _as_map(payload.get("values_by_field_id"))
        by_field = _as_map(values_by_field_id.get(field_id))
        cell_hash = _geo_cell_key_hash(cell_key)
        if cell_hash and cell_hash in by_field:
            return by_field.get(cell_hash)
        values_by_cell_hash = _as_map(payload.get("values_by_cell_hash"))
        return values_by_cell_hash.get(cell_hash)

    def _field_value(field_id: str, cell_key: Mapping[str, object]) -> int:
        direct = _direct_value(field_id, cell_key)
        if direct is not None:
            return _scalar_value(direct)
        try:
            from src.fields.field_engine import field_get_value
        except Exception:
            return 0
        sample = field_get_value(
            field_id=field_id,
            geo_cell_key=cell_key,
            field_layer_rows=payload.get("field_layer_rows"),
            field_cell_rows=payload.get("field_cell_rows"),
            field_type_registry=_as_map(payload.get("field_type_registry")),
            field_binding_registry=_as_map(payload.get("field_binding_registry")),
            interpolation_policy_registry=_as_map(payload.get("interpolation_policy_registry")),
        )
        return _scalar_value(sample.get("value"))

    total = 0
    breakdown: Dict[str, int] = {}
    for row in normalized_terms:
        field_id = str(row.get("field_id", ""))
        current_value = _field_value(field_id, current_cell)
        neighbor_value = _field_value(field_id, neighbor_cell)
        sample_from = str(row.get("sample_from", "neighbor"))
        if sample_from == "current":
            sample_value = current_value
        elif sample_from == "max":
            sample_value = max(current_value, neighbor_value)
        elif sample_from == "delta":
            sample_value = abs(neighbor_value - current_value)
        else:
            sample_value = neighbor_value
        term_cost = int((abs(sample_value) * int(row.get("weight", 1)) * field_scale) // 1000)
        breakdown[field_id] = term_cost
        total += term_cost
    return (int(total), {"field_breakdown": dict((key, breakdown[key]) for key in sorted(breakdown.keys()))})


def _infrastructure_cost_modifier(
    *,
    current_cell: Mapping[str, object],
    neighbor_cell: Mapping[str, object],
    policy_row: Mapping[str, object],
    infrastructure_overlay: Mapping[str, object] | None,
) -> tuple[int, dict]:
    overlay = _as_map(infrastructure_overlay)
    if not overlay:
        return (0, {})
    policy_pref = _as_map(policy_row.get("infrastructure_preference"))
    preferred_tags = _sorted_unique_strings(policy_pref.get("prefer_tags"))
    default_bias = int(_as_int(_as_map(policy_row.get("cost_weights")).get("infrastructure_bias", 0), 0))
    overlay_kind = str(policy_pref.get("overlay_kind", "")).strip().lower()
    entries = list(overlay.get("entries") or overlay.get("edges") or [])
    current_hash = _geo_cell_key_hash(current_cell)
    neighbor_hash = _geo_cell_key_hash(neighbor_cell)
    pair_hash = tuple(sorted((current_hash, neighbor_hash)))
    matched: List[dict] = []
    for row in sorted((dict(item) for item in entries if isinstance(item, Mapping)), key=lambda item: canonical_sha256(item)):
        row_kind = str(row.get("overlay_kind", overlay.get("overlay_kind", ""))).strip().lower()
        if overlay_kind and overlay_kind not in {"none", row_kind} and row_kind:
            continue
        from_key = _coerce_cell_key(row.get("from_geo_cell_key")) or _coerce_cell_key(row.get("from_cell_key"))
        to_key = _coerce_cell_key(row.get("to_geo_cell_key")) or _coerce_cell_key(row.get("to_cell_key"))
        if not from_key or not to_key:
            continue
        row_pair = tuple(sorted((_geo_cell_key_hash(from_key), _geo_cell_key_hash(to_key))))
        if row_pair != pair_hash:
            continue
        matched.append(row)
    if not matched:
        return (0, {})
    matched_row = dict(sorted(matched, key=lambda item: (str(item.get("overlay_kind", "")), canonical_sha256(item)))[0])
    entry_tags = _sorted_unique_strings(matched_row.get("tags"))
    if preferred_tags and not any(tag in entry_tags for tag in preferred_tags):
        return (0, {})
    cost_delta = int(_as_int(matched_row.get("cost_delta", default_bias), default_bias))
    return (
        cost_delta,
        {
            "infrastructure_overlay_kind": str(matched_row.get("overlay_kind", overlay.get("overlay_kind", ""))).strip(),
            "infrastructure_tags": entry_tags,
        },
    )


def _portal_cost_modifier(
    *,
    current_cell: Mapping[str, object],
    neighbor_cell: Mapping[str, object],
    policy_row: Mapping[str, object],
) -> tuple[int, dict]:
    transition_kinds = _transition_neighbor_kinds(current_cell, neighbor_cell)
    if "neighbor.portal" not in transition_kinds:
        return (0, {})
    portal_cost = int(max(0, _as_int(_as_map(policy_row.get("cost_weights")).get("portal_cost", 0), 0)))
    return (portal_cost, {"portal_transition": True, "portal_cost": portal_cost})


def _step_cost(
    *,
    current_cell: Mapping[str, object],
    neighbor_cell: Mapping[str, object],
    topology_profile_id: str,
    metric_profile_id: str,
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
    policy_row: Mapping[str, object],
    field_cost_data: Mapping[str, object] | None,
    infrastructure_overlay: Mapping[str, object] | None,
) -> dict:
    base_distance = geo_distance(
        _cell_center_position(current_cell, topology_row=topology_row, partition_row=partition_row),
        _cell_center_position(neighbor_cell, topology_row=topology_row, partition_row=partition_row),
        topology_profile_id,
        metric_profile_id,
    )
    if str(base_distance.get("result", "")).strip() != "complete":
        return {"cost": 0, "components": {"base_distance_mm": 0}}
    base_weight = int(max(0, _as_int(_as_map(policy_row.get("cost_weights")).get("base_distance", 1000), 1000)))
    base_cost = int((int(max(0, _as_int(base_distance.get("distance_mm", 0), 0))) * base_weight) // 1000)
    field_cost, field_meta = _field_cost_modifier(
        current_cell=current_cell,
        neighbor_cell=neighbor_cell,
        policy_row=policy_row,
        field_cost_data=field_cost_data,
    )
    infrastructure_cost, infra_meta = _infrastructure_cost_modifier(
        current_cell=current_cell,
        neighbor_cell=neighbor_cell,
        policy_row=policy_row,
        infrastructure_overlay=infrastructure_overlay,
    )
    portal_cost, portal_meta = _portal_cost_modifier(
        current_cell=current_cell,
        neighbor_cell=neighbor_cell,
        policy_row=policy_row,
    )
    total = int(max(0, base_cost + int(field_cost) + int(infrastructure_cost) + int(portal_cost)))
    return {
        "cost": total,
        "components": {
            "base_distance_mm": base_cost,
            "field_cost": int(field_cost),
            "infrastructure_cost": int(infrastructure_cost),
            "portal_cost": int(portal_cost),
            **field_meta,
            **infra_meta,
            **portal_meta,
        },
    }


def _heuristic_cost(
    *,
    current_cell: Mapping[str, object],
    goal_cell: Mapping[str, object],
    topology_profile_id: str,
    metric_profile_id: str,
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
    policy_row: Mapping[str, object],
) -> int:
    del current_cell, goal_cell, topology_profile_id, metric_profile_id, topology_row, partition_row
    heuristic_policy = str(_as_map(policy_row.get("extensions")).get("heuristic_policy", "")).strip()
    if heuristic_policy == "geo.path.safe_metric_distance":
        return 0
    return 0


def _reconstruct_path(came_from: Mapping[str, str], node_by_hash: Mapping[str, dict], goal_hash: str) -> List[dict]:
    path_hashes: List[str] = []
    current_hash = str(goal_hash)
    while current_hash:
        path_hashes.append(current_hash)
        current_hash = str(came_from.get(current_hash, "")).strip()
    path_hashes.reverse()
    return [dict(node_by_hash[path_hash]) for path_hash in path_hashes if path_hash in node_by_hash]


def _best_open_candidate(
    open_hashes: Sequence[str],
    *,
    f_score: Mapping[str, int],
    g_score: Mapping[str, int],
    node_by_hash: Mapping[str, dict],
) -> str:
    ranked = sorted(
        [str(token) for token in list(open_hashes or []) if str(token) in node_by_hash],
        key=lambda token: (
            int(f_score.get(str(token), 0)),
            int(g_score.get(str(token), 0)),
            _geo_cell_key_sort_tuple(node_by_hash[str(token)]),
            str(token),
        ),
    )
    return str(ranked[0]) if ranked else ""


def _policy_partial_result(policy_row: Mapping[str, object]) -> str:
    token = str(_as_map(policy_row.get("extensions")).get("partial_result_policy", "refuse")).strip().lower()
    return token if token in {"partial", "refuse"} else "refuse"


def _path_result_row(
    *,
    request_row: Mapping[str, object],
    path_cells: Sequence[Mapping[str, object]],
    total_cost: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "result_id": "path_result.{}".format(canonical_sha256({"request_id": str(request_row.get("request_id", "")), "path_cells": list(path_cells)})),
        "request_id": str(request_row.get("request_id", "")).strip(),
        "path_cells": [dict(_coerce_cell_key(row) or {}) for row in list(path_cells or [])],
        "total_cost": int(total_cost),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def path_result_proof_surface(rows: Sequence[Mapping[str, object]] | None) -> dict:
    normalized_rows = []
    topology_ids: List[str] = []
    metric_ids: List[str] = []
    partition_ids: List[str] = []
    traversal_ids: List[str] = []
    traversal_registry_hashes: List[str] = []
    request_hashes: List[str] = []
    for row in list(rows or []):
        payload = _as_map(row)
        request_row = _as_map(payload.get("path_request"))
        result_row = _as_map(payload.get("path_result")) if "path_result" in payload else payload
        ext = _as_map(result_row.get("extensions"))
        request_hashes.append(path_request_hash(request_row) if request_row else "")
        topology_id = str(ext.get("topology_profile_id", "")).strip()
        metric_id = str(ext.get("metric_profile_id", "")).strip()
        partition_id = str(ext.get("partition_profile_id", "")).strip()
        traversal_id = str(ext.get("traversal_policy_id", "")).strip()
        traversal_registry_hash = str(ext.get("traversal_policy_registry_hash", "")).strip()
        if topology_id:
            topology_ids.append(topology_id)
        if metric_id:
            metric_ids.append(metric_id)
        if partition_id:
            partition_ids.append(partition_id)
        if traversal_id:
            traversal_ids.append(traversal_id)
        if traversal_registry_hash:
            traversal_registry_hashes.append(traversal_registry_hash)
        normalized_rows.append(
            {
                "request_id": str(request_row.get("request_id", result_row.get("request_id", ""))).strip(),
                "result_id": str(result_row.get("result_id", "")).strip(),
                "total_cost": int(_as_int(result_row.get("total_cost", 0), 0)),
                "path_cell_hashes": [_geo_cell_key_hash(cell) for cell in list(result_row.get("path_cells") or [])],
                "goal_reached": bool(ext.get("goal_reached", False)),
                "partial": bool(ext.get("partial", False)),
            }
        )
    normalized_rows = sorted(normalized_rows, key=lambda row: (str(row.get("request_id", "")), str(row.get("result_id", ""))))
    payload = {
        "topology_profile_ids": sorted(set(token for token in topology_ids if token)),
        "metric_profile_ids": sorted(set(token for token in metric_ids if token)),
        "partition_profile_ids": sorted(set(token for token in partition_ids if token)),
        "traversal_policy_ids": sorted(set(token for token in traversal_ids if token)),
        "traversal_policy_registry_hash": sorted(set(token for token in traversal_registry_hashes if token))[0]
        if traversal_registry_hashes
        else "",
        "path_request_hash_chain": canonical_sha256([token for token in request_hashes if token]),
        "path_result_hash_chain": canonical_sha256(normalized_rows),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def geo_path_query(
    path_request: Mapping[str, object] | None,
    *,
    topology_profile_id: str = "",
    metric_profile_id: str = "",
    partition_profile_id: str = "",
    traversal_policy_registry_payload: Mapping[str, object] | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    field_cost_data: Mapping[str, object] | None = None,
    infrastructure_overlay: Mapping[str, object] | None = None,
    shard_assignment: Mapping[str, object] | None = None,
) -> dict:
    del metric_registry_payload
    try:
        request_row = normalize_path_request(path_request)
    except ValueError as exc:
        return _refusal(refusal_code=REFUSAL_GEO_PATH_INVALID, message=str(exc))

    request_ext = _as_map(request_row.get("extensions"))
    topology_token = str(topology_profile_id or request_ext.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    metric_token = str(metric_profile_id or request_ext.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID
    partition_token = str(partition_profile_id or request_ext.get("partition_profile_id", "")).strip() or _DEFAULT_PARTITION_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    metric_row = _metric_row(metric_token)
    if not topology_row:
        return _refusal(
            refusal_code=REFUSAL_GEO_PATH_INVALID,
            message="topology_profile_id is invalid",
            details={"topology_profile_id": topology_token},
        )
    if not partition_row:
        return _refusal(
            refusal_code=REFUSAL_GEO_PATH_INVALID,
            message="partition_profile_id is invalid",
            details={"partition_profile_id": partition_token},
        )
    if not metric_row:
        return _refusal(
            refusal_code=REFUSAL_GEO_PATH_INVALID,
            message="metric_profile_id is invalid",
            details={"metric_profile_id": metric_token},
        )
    policy_row = _traversal_policy_row(str(request_row.get("traversal_policy_id", "")), traversal_policy_registry_payload)
    if not policy_row:
        return _refusal(
            refusal_code=REFUSAL_GEO_PATH_INVALID,
            message="traversal_policy_id is invalid",
            details={"traversal_policy_id": str(request_row.get("traversal_policy_id", ""))},
        )
    policy_row = normalize_traversal_policy(policy_row)
    max_expansions = int(
        max(
            1,
            min(
                _as_int(request_ext.get("max_expansions", policy_row.get("max_expansions", 128)), 128),
                _as_int(policy_row.get("max_expansions", 128), 128),
            ),
        )
    )
    start_cell = _endpoint_cell_key(
        endpoint_ref=_as_map(request_row.get("start_ref")),
        topology_profile_id=topology_token,
        partition_profile_id=partition_token,
        tier_mode=str(request_row.get("tier_mode", "meso")),
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=str(graph_version or ""),
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    goal_cell = _endpoint_cell_key(
        endpoint_ref=_as_map(request_row.get("goal_ref")),
        topology_profile_id=topology_token,
        partition_profile_id=partition_token,
        tier_mode=str(request_row.get("tier_mode", "meso")),
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=str(graph_version or ""),
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if not start_cell or not goal_cell:
        return _refusal(
            refusal_code=REFUSAL_GEO_PATH_INVALID,
            message="start_ref and goal_ref must resolve to canonical GEO cell keys",
            details={
                "start_ref": _as_map(request_row.get("start_ref")),
                "goal_ref": _as_map(request_row.get("goal_ref")),
            },
        )

    start_hash = _geo_cell_key_hash(start_cell)
    goal_hash = _geo_cell_key_hash(goal_cell)
    node_by_hash = {start_hash: dict(start_cell), goal_hash: dict(goal_cell)}
    if start_hash == goal_hash:
        shard_route_plan = build_shard_route_plan(
            request_id=str(request_row.get("request_id", "")),
            path_cells=[start_cell],
            shard_assignment=shard_assignment,
        )
        result_row = _path_result_row(
            request_row=request_row,
            path_cells=[start_cell],
            total_cost=0,
            extensions={
                "goal_reached": True,
                "partial": False,
                "expanded_count": 0,
                "max_expansions": max_expansions,
                "topology_profile_id": topology_token,
                "metric_profile_id": metric_token,
                "partition_profile_id": partition_token,
                "traversal_policy_id": str(policy_row.get("traversal_policy_id", "")),
                "tier_mode": str(request_row.get("tier_mode", "")),
                "traversal_policy_registry_hash": traversal_policy_registry_hash(traversal_policy_registry_payload),
                "shard_route_plan": shard_route_plan,
            },
        )
        outputs = {"path_result_hash": canonical_sha256(result_row), "goal_reached": True, "expanded_count": 0}
        payload = {
            "result": "complete",
            "path_request": request_row,
            "path_result": result_row,
            "expanded_count": 0,
            "goal_reached": True,
            "query_record": _query_record("geo_path_query", request_row, outputs),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    open_hashes: List[str] = [start_hash]
    closed_hashes: Dict[str, bool] = {}
    came_from: Dict[str, str] = {}
    predecessor_key: Dict[str, Tuple[str, Tuple[int, ...], int]] = {}
    g_score: Dict[str, int] = {start_hash: 0}
    f_score: Dict[str, int] = {
        start_hash: _heuristic_cost(
            current_cell=start_cell,
            goal_cell=goal_cell,
            topology_profile_id=topology_token,
            metric_profile_id=metric_token,
            topology_row=topology_row,
            partition_row=partition_row,
            policy_row=policy_row,
        )
    }
    expansions = 0
    best_candidate_hash = start_hash
    goal_reached = False

    while open_hashes:
        current_hash = _best_open_candidate(open_hashes, f_score=f_score, g_score=g_score, node_by_hash=node_by_hash)
        if not current_hash:
            break
        current_cell = dict(node_by_hash[current_hash])
        if current_hash == goal_hash:
            goal_reached = True
            best_candidate_hash = current_hash
            break
        open_hashes = [token for token in open_hashes if str(token) != current_hash]
        closed_hashes[current_hash] = True
        expansions += 1
        if expansions >= max_expansions:
            best_candidate_hash = current_hash
            break

        neighbor_payload = geo_neighbors(
            current_cell,
            1,
            topology_token,
            metric_token,
            partition_token,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
        if str(neighbor_payload.get("result", "")).strip() != "complete":
            continue
        neighbor_rows = [dict(row) for row in list(neighbor_payload.get("neighbors") or []) if _coerce_cell_key(row)]
        for neighbor_cell in sorted(neighbor_rows, key=_geo_cell_key_sort_tuple):
            if not _policy_allows_neighbor(policy_row, current_cell, neighbor_cell):
                continue
            neighbor_hash = _geo_cell_key_hash(neighbor_cell)
            if not neighbor_hash:
                continue
            node_by_hash[neighbor_hash] = dict(neighbor_cell)
            if bool(closed_hashes.get(neighbor_hash, False)):
                continue
            cost_row = _step_cost(
                current_cell=current_cell,
                neighbor_cell=neighbor_cell,
                topology_profile_id=topology_token,
                metric_profile_id=metric_token,
                topology_row=topology_row,
                partition_row=partition_row,
                policy_row=policy_row,
                field_cost_data=field_cost_data,
                infrastructure_overlay=infrastructure_overlay,
            )
            tentative_g = int(g_score.get(current_hash, 0)) + int(max(0, _as_int(cost_row.get("cost", 0), 0)))
            current_predecessor_key = _geo_cell_key_sort_tuple(current_cell)
            previous_g = g_score.get(neighbor_hash)
            previous_predecessor = predecessor_key.get(neighbor_hash)
            should_update = previous_g is None or tentative_g < int(previous_g)
            if (not should_update) and previous_g is not None and tentative_g == int(previous_g):
                should_update = previous_predecessor is None or current_predecessor_key < previous_predecessor
            if not should_update:
                continue
            came_from[neighbor_hash] = current_hash
            predecessor_key[neighbor_hash] = current_predecessor_key
            g_score[neighbor_hash] = tentative_g
            heuristic = _heuristic_cost(
                current_cell=neighbor_cell,
                goal_cell=goal_cell,
                topology_profile_id=topology_token,
                metric_profile_id=metric_token,
                topology_row=topology_row,
                partition_row=partition_row,
                policy_row=policy_row,
            )
            f_score[neighbor_hash] = tentative_g + int(heuristic)
            if neighbor_hash not in open_hashes:
                open_hashes.append(neighbor_hash)
            best_candidate_hash = _best_open_candidate(
                [best_candidate_hash, neighbor_hash],
                f_score=f_score,
                g_score=g_score,
                node_by_hash=node_by_hash,
            ) or best_candidate_hash

    partial_policy = _policy_partial_result(policy_row)
    if goal_reached:
        path_cells = _reconstruct_path(came_from, node_by_hash, goal_hash)
        total_cost = int(g_score.get(goal_hash, 0))
        shard_route_plan = build_shard_route_plan(
            request_id=str(request_row.get("request_id", "")),
            path_cells=path_cells,
            shard_assignment=shard_assignment,
        )
        result_row = _path_result_row(
            request_row=request_row,
            path_cells=path_cells,
            total_cost=total_cost,
            extensions={
                "goal_reached": True,
                "partial": False,
                "expanded_count": expansions,
                "max_expansions": max_expansions,
                "topology_profile_id": topology_token,
                "metric_profile_id": metric_token,
                "partition_profile_id": partition_token,
                "traversal_policy_id": str(policy_row.get("traversal_policy_id", "")),
                "tier_mode": str(request_row.get("tier_mode", "")),
                "traversal_policy_registry_hash": traversal_policy_registry_hash(traversal_policy_registry_payload),
                "shard_route_plan": shard_route_plan,
            },
        )
        outputs = {"path_result_hash": canonical_sha256(result_row), "goal_reached": True, "expanded_count": expansions}
        payload = {
            "result": "complete",
            "path_request": request_row,
            "path_result": result_row,
            "expanded_count": expansions,
            "goal_reached": True,
            "query_record": _query_record("geo_path_query", request_row, outputs),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    if expansions >= max_expansions and partial_policy == "partial" and best_candidate_hash:
        partial_cells = _reconstruct_path(came_from, node_by_hash, best_candidate_hash)
        shard_route_plan = build_shard_route_plan(
            request_id=str(request_row.get("request_id", "")),
            path_cells=partial_cells,
            shard_assignment=shard_assignment,
        )
        result_row = _path_result_row(
            request_row=request_row,
            path_cells=partial_cells,
            total_cost=int(g_score.get(best_candidate_hash, 0)),
            extensions={
                "goal_reached": False,
                "partial": True,
                "partial_reason": "max_expansions_exceeded",
                "expanded_count": expansions,
                "max_expansions": max_expansions,
                "topology_profile_id": topology_token,
                "metric_profile_id": metric_token,
                "partition_profile_id": partition_token,
                "traversal_policy_id": str(policy_row.get("traversal_policy_id", "")),
                "tier_mode": str(request_row.get("tier_mode", "")),
                "traversal_policy_registry_hash": traversal_policy_registry_hash(traversal_policy_registry_payload),
                "shard_route_plan": shard_route_plan,
            },
        )
        outputs = {"path_result_hash": canonical_sha256(result_row), "goal_reached": False, "expanded_count": expansions}
        payload = {
            "result": "partial",
            "path_request": request_row,
            "path_result": result_row,
            "expanded_count": expansions,
            "goal_reached": False,
            "query_record": _query_record("geo_path_query", request_row, outputs),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    refusal_code = REFUSAL_GEO_PATH_BOUNDED if expansions >= max_expansions else REFUSAL_GEO_PATH_NOT_FOUND
    message = "path search exceeded max_expansions" if expansions >= max_expansions else "no path found under traversal policy"
    return _refusal(
        refusal_code=refusal_code,
        message=message,
        details={
            "request_id": str(request_row.get("request_id", "")).strip(),
            "expanded_count": expansions,
            "max_expansions": max_expansions,
            "topology_profile_id": topology_token,
            "metric_profile_id": metric_token,
            "partition_profile_id": partition_token,
            "traversal_policy_id": str(policy_row.get("traversal_policy_id", "")),
        },
    )


__all__ = [
    "REFUSAL_GEO_PATH_BOUNDED",
    "REFUSAL_GEO_PATH_INVALID",
    "REFUSAL_GEO_PATH_NOT_FOUND",
    "build_path_request",
    "geo_path_query",
    "normalize_path_request",
    "path_request_hash",
    "path_result_proof_surface",
    "traversal_policy_registry_hash",
]
