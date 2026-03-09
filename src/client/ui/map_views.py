"""Deterministic UX-0 map and minimap surfaces over GEO-5 view artifacts."""

from __future__ import annotations

from typing import Mapping

from src.geo import (
    build_lens_request,
    build_position_ref,
    build_projected_view_artifact,
    build_projected_view_layer_buffers,
    build_projection_request,
    project_view_cells,
    render_projected_view_ascii,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_TOPOLOGY_PROFILE_ID = "geo.topology.r3_infinite"
DEFAULT_PARTITION_PROFILE_ID = "geo.partition.grid_zd"
DEFAULT_METRIC_PROFILE_ID = "geo.metric.euclidean"
DEFAULT_MAP_VIEW_TYPE_ID = "view.map_ortho"
DEFAULT_MINIMAP_VIEW_TYPE_ID = "view.minimap"
DEFAULT_MAP_LAYERS = [
    "layer.terrain_stub",
    "layer.temperature",
    "layer.pollution",
    "layer.geometry_occupancy",
    "layer.infrastructure_stub",
    "layer.entity_markers_stub",
]
DEFAULT_MINIMAP_LAYERS = [
    "layer.terrain_stub",
    "layer.temperature",
    "layer.geometry_occupancy",
]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _default_position_ref(role: str) -> dict:
    return build_position_ref(
        object_id="camera.main",
        frame_id="frame.surface_local",
        local_position=[0, 0, 0],
        extensions={"source": "UX0-5", "role": str(role or "map").strip() or "map"},
    )


def _normalized_position_ref(origin_position_ref: Mapping[str, object] | None, role: str) -> dict:
    payload = _as_map(origin_position_ref)
    if not payload:
        return _default_position_ref(role)
    local_position = payload.get("local_position")
    if not isinstance(local_position, list):
        point = _as_map(payload.get("position_mm"))
        local_position = [
            int(_as_int(point.get("x", 0), 0)),
            int(_as_int(point.get("y", 0), 0)),
            int(_as_int(point.get("z", 0), 0)),
        ]
    return build_position_ref(
        object_id=str(payload.get("object_id", "")).strip() or "camera.main",
        frame_id=str(payload.get("frame_id", "")).strip() or "frame.surface_local",
        local_position=[int(_as_int(item, 0)) for item in list(local_position or [0, 0, 0])],
        extensions={
            "source": "UX0-5",
            "role": str(role or "map").strip() or "map",
            **_as_map(payload.get("extensions")),
        },
    )


def _normalized_perceived_model(
    perceived_model: Mapping[str, object] | None,
    *,
    lens_id: str,
) -> dict:
    payload = _as_map(perceived_model)
    metadata = _as_map(payload.get("metadata"))
    token = str(lens_id or "").strip()
    lens_type = str(metadata.get("lens_type", "")).strip().lower()
    if not lens_type:
        lens_type = "diegetic" if token.startswith("lens.diegetic.") else "nondiegetic"
    return {
        **payload,
        "lens_id": token or str(payload.get("lens_id", "")).strip(),
        "metadata": {
            **metadata,
            "lens_type": lens_type,
            "epistemic_policy_id": str(metadata.get("epistemic_policy_id", "")).strip()
            or ("epistemic.diegetic_default" if lens_type == "diegetic" else "epistemic.admin_full"),
        },
    }


def _default_resolution_spec(view_type_id: str) -> dict:
    token = str(view_type_id or "").strip()
    if token == DEFAULT_MINIMAP_VIEW_TYPE_ID:
        return {"width": 9, "height": 9}
    return {"width": 17, "height": 17}


def _default_extent_spec(view_type_id: str) -> dict:
    token = str(view_type_id or "").strip()
    return {"radius_cells": 2 if token == DEFAULT_MINIMAP_VIEW_TYPE_ID else 4, "axis_order": ["x", "y"]}


def _display_payload(
    *,
    ui_mode: str,
    projected_view_artifact: Mapping[str, object] | None,
    preferred_layer_order: object,
) -> dict:
    ascii_payload = render_projected_view_ascii(
        projected_view_artifact,
        preferred_layer_order=_sorted_strings(preferred_layer_order),
    )
    buffer_payload = build_projected_view_layer_buffers(projected_view_artifact)
    mode = str(ui_mode or "").strip().lower() or "gui"
    preferred = "ascii" if mode in {"cli", "tui"} else "buffer"
    return {
        "preferred_presentation": preferred,
        "ascii": dict(ascii_payload),
        "buffer": dict(buffer_payload),
    }


def build_map_view_surface(
    *,
    view_id: str,
    view_type_id: str,
    origin_position_ref: Mapping[str, object] | None,
    lens_id: str,
    included_layers: object,
    perceived_model: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None = None,
    layer_source_payloads: Mapping[str, object] | None = None,
    topology_profile_id: str = DEFAULT_TOPOLOGY_PROFILE_ID,
    partition_profile_id: str = DEFAULT_PARTITION_PROFILE_ID,
    metric_profile_id: str = DEFAULT_METRIC_PROFILE_ID,
    resolution_spec: Mapping[str, object] | None = None,
    extent_spec: Mapping[str, object] | None = None,
    ui_mode: str = "gui",
    truth_hash_anchor: str = "",
) -> dict:
    role = str(view_id or "").strip() or "map"
    origin = _normalized_position_ref(origin_position_ref, role)
    layers = _sorted_strings(included_layers)
    if not layers:
        layers = list(DEFAULT_MAP_LAYERS if str(view_type_id) != DEFAULT_MINIMAP_VIEW_TYPE_ID else DEFAULT_MINIMAP_LAYERS)
    projection_request = build_projection_request(
        request_id="projection_request.{}".format(role),
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec={**_default_extent_spec(view_type_id), **_as_map(extent_spec), "axis_order": ["x", "y"]},
        resolution_spec={**_default_resolution_spec(view_type_id), **_as_map(resolution_spec)},
        extensions={
            "view_type_id": str(view_type_id or DEFAULT_MAP_VIEW_TYPE_ID).strip() or DEFAULT_MAP_VIEW_TYPE_ID,
            "topology_profile_id": str(topology_profile_id or DEFAULT_TOPOLOGY_PROFILE_ID).strip() or DEFAULT_TOPOLOGY_PROFILE_ID,
            "partition_profile_id": str(partition_profile_id or DEFAULT_PARTITION_PROFILE_ID).strip()
            or DEFAULT_PARTITION_PROFILE_ID,
            "metric_profile_id": str(metric_profile_id or DEFAULT_METRIC_PROFILE_ID).strip() or DEFAULT_METRIC_PROFILE_ID,
            "chart_id": str(_as_map(origin.get("extensions")).get("chart_id", "")).strip() or "chart.global.r3",
            "worldgen_refinement_level": 0,
            "worldgen_reason": "roi",
        },
    )
    projection_result = project_view_cells(
        projection_request,
        topology_profile_id=str(topology_profile_id or DEFAULT_TOPOLOGY_PROFILE_ID).strip() or DEFAULT_TOPOLOGY_PROFILE_ID,
        partition_profile_id=str(partition_profile_id or DEFAULT_PARTITION_PROFILE_ID).strip() or DEFAULT_PARTITION_PROFILE_ID,
        metric_profile_id=str(metric_profile_id or DEFAULT_METRIC_PROFILE_ID).strip() or DEFAULT_METRIC_PROFILE_ID,
    )
    normalized_perceived = _normalized_perceived_model(perceived_model, lens_id=str(lens_id or "").strip())
    lens_request = build_lens_request(
        lens_request_id="lens_request.{}".format(role),
        lens_profile_id=str(lens_id or "").strip() or "lens.diegetic.sensor",
        included_layers=list(layers),
        extensions={"view_type_id": str(view_type_id or DEFAULT_MAP_VIEW_TYPE_ID).strip() or DEFAULT_MAP_VIEW_TYPE_ID},
    )
    projected_view_artifact = build_projected_view_artifact(
        projection_result=projection_result,
        lens_request=lens_request,
        perceived_model=normalized_perceived,
        layer_source_payloads=dict(layer_source_payloads or {}),
        authority_context=dict(authority_context or {}),
        truth_hash_anchor=str(truth_hash_anchor or "").strip(),
    )
    display = _display_payload(
        ui_mode=str(ui_mode or "gui"),
        projected_view_artifact=projected_view_artifact,
        preferred_layer_order=list(layers),
    )
    payload = {
        "result": "complete",
        "view_id": role,
        "view_type_id": str(view_type_id or DEFAULT_MAP_VIEW_TYPE_ID).strip() or DEFAULT_MAP_VIEW_TYPE_ID,
        "origin_position_ref": dict(origin),
        "projection_request": dict(projection_request),
        "projection_result": dict(projection_result),
        "lens_request": dict(lens_request),
        "projected_view_artifact": dict(projected_view_artifact),
        "display": dict(display),
        "selected_layer_ids": list(layers),
        "worldgen_requests": [
            dict(row)
            for row in list(_as_map(projection_result).get("worldgen_requests") or [])
            if isinstance(row, Mapping)
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_map_view_set(
    *,
    perceived_model: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None = None,
    map_origin_position_ref: Mapping[str, object] | None = None,
    minimap_origin_position_ref: Mapping[str, object] | None = None,
    layer_source_payloads: Mapping[str, object] | None = None,
    map_layer_ids: object = None,
    minimap_layer_ids: object = None,
    lens_id: str = "lens.diegetic.sensor",
    topology_profile_id: str = DEFAULT_TOPOLOGY_PROFILE_ID,
    partition_profile_id: str = DEFAULT_PARTITION_PROFILE_ID,
    metric_profile_id: str = DEFAULT_METRIC_PROFILE_ID,
    map_resolution_spec: Mapping[str, object] | None = None,
    minimap_resolution_spec: Mapping[str, object] | None = None,
    map_extent_spec: Mapping[str, object] | None = None,
    minimap_extent_spec: Mapping[str, object] | None = None,
    ui_mode: str = "gui",
    truth_hash_anchor: str = "",
) -> dict:
    map_view = build_map_view_surface(
        view_id="map",
        view_type_id=DEFAULT_MAP_VIEW_TYPE_ID,
        origin_position_ref=map_origin_position_ref,
        lens_id=str(lens_id or "").strip() or "lens.diegetic.sensor",
        included_layers=map_layer_ids or DEFAULT_MAP_LAYERS,
        perceived_model=perceived_model,
        authority_context=authority_context,
        layer_source_payloads=layer_source_payloads,
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        metric_profile_id=metric_profile_id,
        resolution_spec=map_resolution_spec,
        extent_spec=map_extent_spec,
        ui_mode=ui_mode,
        truth_hash_anchor=truth_hash_anchor,
    )
    minimap_view = build_map_view_surface(
        view_id="minimap",
        view_type_id=DEFAULT_MINIMAP_VIEW_TYPE_ID,
        origin_position_ref=minimap_origin_position_ref or map_origin_position_ref,
        lens_id=str(lens_id or "").strip() or "lens.diegetic.sensor",
        included_layers=minimap_layer_ids or DEFAULT_MINIMAP_LAYERS,
        perceived_model=perceived_model,
        authority_context=authority_context,
        layer_source_payloads=layer_source_payloads,
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        metric_profile_id=metric_profile_id,
        resolution_spec=minimap_resolution_spec,
        extent_spec=minimap_extent_spec,
        ui_mode=ui_mode,
        truth_hash_anchor=truth_hash_anchor,
    )
    payload = {
        "result": "complete",
        "map_view": dict(map_view),
        "minimap_view": dict(minimap_view),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_MAP_LAYERS",
    "DEFAULT_MAP_VIEW_TYPE_ID",
    "DEFAULT_MINIMAP_LAYERS",
    "DEFAULT_MINIMAP_VIEW_TYPE_ID",
    "build_map_view_set",
    "build_map_view_surface",
]
