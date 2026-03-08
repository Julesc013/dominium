"""Deterministic GEO-5 projection request engine."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.frame_engine import _frame_nodes_by_id, position_to_frame
from src.geo.index.geo_index_engine import _build_geo_cell_key, _coerce_cell_key, geo_cell_key_from_position
from src.geo.kernel.geo_kernel import (
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_PARTITION_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_list,
    _as_map,
    _default_registry_payload,
    _dimension_from_topology,
    _partition_row,
    _periodic_coord,
    _periods_from_topology,
    _projection_row,
    _topology_row,
)
from src.geo.metric.neighborhood_engine import geo_neighbors


REFUSAL_GEO_PROJECTION_REQUEST_INVALID = "refusal.geo.projection_request_invalid"
_REQUEST_VERSION = "GEO5-3"
_VIEW_TYPE_REGISTRY_REL = "data/registries/view_type_registry.json"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _rows_by_id(payload: Mapping[str, object] | None, *, row_key: str, id_key: str) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(row_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _axis_labels(dimension: int) -> List[str]:
    base = ["x", "y", "z", "w", "v", "u"]
    if dimension <= len(base):
        return base[:dimension]
    return base + ["a{}".format(idx) for idx in range(len(base), int(dimension))]


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int]:
    row = _coerce_cell_key(value)
    if not row:
        return ("", tuple(), 0)
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
    )


def _refusal(message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_PROJECTION_REQUEST_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _view_type_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_VIEW_TYPE_REGISTRY_REL),
        row_key="view_types",
        id_key="view_type_id",
    )


def build_projection_request(
    *,
    request_id: str,
    projection_profile_id: str,
    origin_position_ref: Mapping[str, object] | None,
    extent_spec: Mapping[str, object] | None,
    resolution_spec: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "projection_profile_id": str(projection_profile_id or "").strip(),
        "origin_position_ref": _as_map(origin_position_ref),
        "extent_spec": _as_map(extent_spec),
        "resolution_spec": _as_map(resolution_spec),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_projection_request(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    view_type_id = str(_as_map(payload.get("extensions")).get("view_type_id", "")).strip()
    view_row = dict(_view_type_rows().get(view_type_id) or {})
    view_ext = _as_map(view_row.get("extensions"))
    default_resolution = _as_map(view_ext.get("default_resolution"))
    resolution_spec = _as_map(payload.get("resolution_spec"))
    width = int(max(1, _as_int(resolution_spec.get("width", default_resolution.get("width", 9)), 9)))
    height = int(max(1, _as_int(resolution_spec.get("height", default_resolution.get("height", 9)), 9)))
    return build_projection_request(
        request_id=str(payload.get("request_id", "")).strip()
        or "projection_request.{}".format(canonical_sha256({"seed": payload})[:16]),
        projection_profile_id=str(payload.get("projection_profile_id", "")).strip()
        or str(view_row.get("projection_profile_id", "geo.projection.ortho_2d")).strip()
        or "geo.projection.ortho_2d",
        origin_position_ref=_as_map(payload.get("origin_position_ref")),
        extent_spec={
            "radius_cells": int(max(0, _as_int(_as_map(payload.get("extent_spec")).get("radius_cells", 0), 0))),
            "slice_axes": _sorted_strings(_as_map(payload.get("extent_spec")).get("slice_axes")),
            "axis_order": _sorted_strings(_as_map(payload.get("extent_spec")).get("axis_order")),
            **_as_map(payload.get("extent_spec")),
        },
        resolution_spec={
            "width": width,
            "height": height,
            **resolution_spec,
        },
        extensions={
            "view_type_id": view_type_id or str(view_row.get("view_type_id", "")).strip() or None,
            **_as_map(payload.get("extensions")),
        },
    )


def projection_request_hash(row: Mapping[str, object] | None) -> str:
    payload = normalize_projection_request(row)
    semantic = {
        "request_id": str(payload.get("request_id", "")).strip(),
        "projection_profile_id": str(payload.get("projection_profile_id", "")).strip(),
        "origin_position_ref": _as_map(payload.get("origin_position_ref")),
        "extent_spec": _as_map(payload.get("extent_spec")),
        "resolution_spec": _as_map(payload.get("resolution_spec")),
        "extensions": _as_map(payload.get("extensions")),
    }
    return canonical_sha256(semantic)


def _projection_context(
    *,
    request: Mapping[str, object],
    topology_profile_id: str,
    partition_profile_id: str,
    metric_profile_id: str,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str,
    topology_registry_payload: Mapping[str, object] | None,
    partition_registry_payload: Mapping[str, object] | None,
) -> dict:
    normalized = normalize_projection_request(request)
    extensions = _as_map(normalized.get("extensions"))
    target_frame_id = str(extensions.get("target_frame_id", "")).strip()
    explicit_cell_key = _coerce_cell_key(extensions.get("origin_geo_cell_key"))
    topology_token = str(topology_profile_id or "").strip() or str(extensions.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_token = str(partition_profile_id or "").strip() or str(extensions.get("partition_profile_id", "")).strip() or _DEFAULT_PARTITION_PROFILE_ID
    metric_token = str(metric_profile_id or "").strip() or str(extensions.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    if not topology_row or not partition_row:
        return {}
    chart_id = str(extensions.get("chart_id", "")).strip() or "chart.global"
    origin_position_ref = _as_map(normalized.get("origin_position_ref"))
    local_position = list(_as_list(origin_position_ref.get("local_position")))
    effective_frame_id = str(origin_position_ref.get("frame_id", "")).strip()
    if origin_position_ref and frame_nodes and frame_transform_rows:
        target_token = target_frame_id or effective_frame_id
        if target_token:
            converted = position_to_frame(
                origin_position_ref,
                target_token,
                frame_nodes=frame_nodes,
                frame_transform_rows=frame_transform_rows,
                graph_version=str(graph_version or "").strip(),
                topology_registry_payload=topology_registry_payload,
            )
            if str(converted.get("result", "")) == "complete":
                target_position = _as_map(converted.get("target_position_ref"))
                local_position = list(target_position.get("local_position") or local_position)
                effective_frame_id = str(target_position.get("frame_id", effective_frame_id)).strip() or effective_frame_id
                nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
                frame_row = dict(nodes.get(effective_frame_id) or {})
                if frame_row:
                    chart_id = str(frame_row.get("chart_id", chart_id)).strip() or chart_id
                    topology_token = str(frame_row.get("topology_profile_id", topology_token)).strip() or topology_token
                    metric_token = str(frame_row.get("metric_profile_id", metric_token)).strip() or metric_token
                    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
                    if not topology_row:
                        return {}
    dimension = max(1, _dimension_from_topology(topology_row))
    while len(local_position) < dimension:
        local_position.append(0)
    center_cell_key = explicit_cell_key
    if not center_cell_key:
        cell_key_result = geo_cell_key_from_position(
            {
                "coords": [int(_as_int(value, 0)) for value in local_position[:dimension]],
                "chart_id": chart_id,
                "refinement_level": int(max(0, _as_int(extensions.get("refinement_level", 0), 0))),
            },
            topology_token,
            partition_token,
            chart_id,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
        if str(_as_map(cell_key_result).get("result", "")).strip() == "complete":
            center_cell_key = _as_map(cell_key_result).get("cell_key")
    center_row = _coerce_cell_key(center_cell_key)
    if not center_row:
        return {}
    return {
        "request": normalized,
        "topology_profile_id": topology_token,
        "partition_profile_id": partition_token,
        "metric_profile_id": metric_token,
        "topology_row": topology_row,
        "partition_row": partition_row,
        "center_cell_key": center_row,
    }


def _axis_indices(spec_axes: object, dimension: int, default_axes: Sequence[int]) -> List[int]:
    labels = _axis_labels(dimension)
    label_to_index = dict((labels[idx], idx) for idx in range(len(labels)))
    out: List[int] = []
    for item in list(spec_axes or []):
        if isinstance(item, int):
            idx = int(item)
        else:
            idx = int(label_to_index.get(str(item).strip(), -1))
        if 0 <= idx < dimension and idx not in out:
            out.append(idx)
    if out:
        return out
    return [idx for idx in default_axes if 0 <= int(idx) < dimension]


def _range_for_axis(resolution: int) -> List[int]:
    width = int(max(1, resolution))
    radius = int(width // 2)
    if width % 2 == 0:
        return list(range(-radius, radius))
    return list(range(-radius, radius + 1))


def _grid_projected_cells(
    *,
    center_cell_key: Mapping[str, object],
    topology_row: Mapping[str, object],
    partition_row: Mapping[str, object],
    projection_profile_id: str,
    extent_spec: Mapping[str, object],
    resolution_spec: Mapping[str, object],
) -> List[dict]:
    center = _coerce_cell_key(center_cell_key)
    if not center:
        return []
    index_tuple = [int(_as_int(value, 0)) for value in list(center.get("index_tuple") or [])]
    dimension = len(index_tuple)
    projection_row = _projection_row(projection_profile_id, registry_payload=_default_registry_payload("projection"))
    projection_kind = str(projection_row.get("projection_kind", "ortho_2d")).strip().lower() or "ortho_2d"
    projection_params = _as_map(projection_row.get("parameters"))
    slice_axes = _axis_indices(_as_map(extent_spec).get("slice_axes"), dimension, default_axes=[])
    varying_axes = _axis_indices(
        _as_map(extent_spec).get("axis_order") or projection_params.get("axis_order"),
        dimension,
        default_axes=[0, 1] if dimension >= 2 else [0],
    )
    if projection_kind == "slice_nd_stub":
        varying_axes = [idx for idx in range(dimension) if idx not in set(slice_axes)] or [0]
    while len(varying_axes) < 2 and dimension > len(varying_axes):
        candidate = next((idx for idx in range(dimension) if idx not in set(varying_axes) and idx not in set(slice_axes)), None)
        if candidate is None:
            break
        varying_axes.append(int(candidate))
    width_offsets = _range_for_axis(int(max(1, _as_int(_as_map(resolution_spec).get("width", 9), 9))))
    height_offsets = _range_for_axis(int(max(1, _as_int(_as_map(resolution_spec).get("height", 9), 9))))
    boundary_rule_id = str(_as_map(topology_row).get("boundary_rule_id", "")).strip().lower()
    periods = _periods_from_topology(topology_row, dimension)
    while len(periods) < dimension:
        periods.append(0)
    out = []
    for y_index, dy in enumerate(height_offsets):
        for x_index, dx in enumerate(width_offsets):
            next_tuple = list(index_tuple)
            next_tuple[varying_axes[0]] = int(index_tuple[varying_axes[0]] + int(dx))
            if len(varying_axes) > 1:
                next_tuple[varying_axes[1]] = int(index_tuple[varying_axes[1]] + int(dy))
            if "periodic" in boundary_rule_id:
                next_tuple = [_periodic_coord(next_tuple[idx], periods[idx]) for idx in range(dimension)]
            geo_cell_key = _build_geo_cell_key(
                partition_profile_id=str(center.get("partition_profile_id", "")).strip(),
                topology_profile_id=str(center.get("topology_profile_id", "")).strip(),
                chart_id=str(center.get("chart_id", "")).strip(),
                index_tuple=next_tuple,
                refinement_level=int(max(0, _as_int(center.get("refinement_level", 0), 0))),
                partition_kind=str(_as_map(partition_row).get("partition_kind", "grid")).strip().lower() or "grid",
                legacy_cell_alias="cell.{}".format(".".join(str(int(value)) for value in next_tuple)),
                extensions={"source": _REQUEST_VERSION},
            )
            out.append(
                {
                    "geo_cell_key": geo_cell_key,
                    "projected_coord": {
                        "x_index": int(x_index),
                        "y_index": int(y_index),
                        "x_offset": int(dx),
                        "y_offset": int(dy),
                    },
                    "slice_axes": list(_axis_labels(dimension)[idx] for idx in slice_axes),
                }
            )
    return sorted(
        (dict(row) for row in out),
        key=lambda row: (
            int(_as_map(row.get("projected_coord")).get("y_index", 0)),
            int(_as_map(row.get("projected_coord")).get("x_index", 0)),
            _geo_cell_key_sort_tuple(row.get("geo_cell_key")),
        ),
    )


def _atlas_projected_cells(
    *,
    center_cell_key: Mapping[str, object],
    topology_row: Mapping[str, object],
    resolution_spec: Mapping[str, object],
) -> List[dict]:
    center = _coerce_cell_key(center_cell_key)
    if not center:
        return []
    width = int(max(1, _as_int(_as_map(resolution_spec).get("width", 9), 9)))
    height = int(max(1, _as_int(_as_map(resolution_spec).get("height", 9), 9)))
    radius = int(max(width, height) // 2)
    neighbor_payload = geo_neighbors(
        center,
        radius,
        str(center.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID,
        metric_profile_id="geo.metric.spherical_geodesic_stub",
        partition_profile_id=str(center.get("partition_profile_id", "")).strip() or _DEFAULT_PARTITION_PROFILE_ID,
    )
    rows = [_coerce_cell_key(row) for row in list(neighbor_payload.get("neighbors") or []) if isinstance(row, Mapping)]
    rows.append(center)
    chart_ids = sorted(
        str(dict(item).get("chart_id", "")).strip()
        for item in list(_as_map(topology_row).get("chart_definitions") or [])
        if isinstance(item, Mapping) and str(dict(item).get("chart_id", "")).strip()
    )
    chart_order = dict((chart_id, idx) for idx, chart_id in enumerate(chart_ids))
    out = []
    for row in sorted((item for item in rows if item), key=_geo_cell_key_sort_tuple):
        index_tuple = [int(_as_int(value, 0)) for value in list(row.get("index_tuple") or [])]
        out.append(
            {
                "geo_cell_key": dict(row),
                "projected_coord": {
                    "chart_slot": int(chart_order.get(str(row.get("chart_id", "")).strip(), 0)),
                    "u_index": int(index_tuple[0] if len(index_tuple) > 0 else 0),
                    "v_index": int(index_tuple[1] if len(index_tuple) > 1 else 0),
                },
                "slice_axes": [],
            }
        )
    return sorted(
        (dict(row) for row in out),
        key=lambda row: (
            int(_as_map(row.get("projected_coord")).get("chart_slot", 0)),
            int(_as_map(row.get("projected_coord")).get("v_index", 0)),
            int(_as_map(row.get("projected_coord")).get("u_index", 0)),
            _geo_cell_key_sort_tuple(row.get("geo_cell_key")),
        ),
    )


def project_view_cells(
    projection_request: Mapping[str, object] | None,
    *,
    topology_profile_id: str = "",
    partition_profile_id: str = "",
    metric_profile_id: str = "",
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    request = normalize_projection_request(projection_request)
    if not str(request.get("projection_profile_id", "")).strip():
        return _refusal("projection_profile_id is required")
    context = _projection_context(
        request=request,
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        metric_profile_id=metric_profile_id,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if not context:
        return _refusal("projection request context is invalid or incomplete")
    projection_profile_id = str(request.get("projection_profile_id", "")).strip()
    projection_row = _projection_row(projection_profile_id, registry_payload=_default_registry_payload("projection"))
    if not projection_row:
        return _refusal("projection profile is missing", {"projection_profile_id": projection_profile_id})
    partition_kind = str(_as_map(context.get("partition_row")).get("partition_kind", "grid")).strip().lower() or "grid"
    projection_kind = str(projection_row.get("projection_kind", "ortho_2d")).strip().lower() or "ortho_2d"
    resolution_spec = _as_map(request.get("resolution_spec"))
    extent_spec = _as_map(request.get("extent_spec"))
    if partition_kind in {"atlas", "sphere_tiles"} or projection_kind == "atlas_unwrap":
        projected_cells = _atlas_projected_cells(
            center_cell_key=_as_map(context.get("center_cell_key")),
            topology_row=_as_map(context.get("topology_row")),
            resolution_spec=resolution_spec,
        )
    else:
        projected_cells = _grid_projected_cells(
            center_cell_key=_as_map(context.get("center_cell_key")),
            topology_row=_as_map(context.get("topology_row")),
            partition_row=_as_map(context.get("partition_row")),
            projection_profile_id=projection_profile_id,
            extent_spec=extent_spec,
            resolution_spec=resolution_spec,
        )
    mapping_descriptor = {
        "projection_kind": projection_kind,
        "partition_kind": partition_kind,
        "center_cell_key": _as_map(context.get("center_cell_key")),
        "resolution_spec": dict(resolution_spec),
        "extent_spec": dict(extent_spec),
        "version": _REQUEST_VERSION,
    }
    payload = {
        "result": "complete",
        "projection_request": dict(request),
        "projection_request_hash": projection_request_hash(request),
        "topology_profile_id": str(context.get("topology_profile_id", "")).strip(),
        "partition_profile_id": str(context.get("partition_profile_id", "")).strip(),
        "metric_profile_id": str(context.get("metric_profile_id", "")).strip(),
        "mapping_descriptor": mapping_descriptor,
        "projected_cells": [dict(row) for row in list(projected_cells or [])],
        "projected_cell_keys": [dict(_as_map(row.get("geo_cell_key"))) for row in list(projected_cells or [])],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
