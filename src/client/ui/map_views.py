"""Deterministic UX-0 map and minimap surfaces over GEO-5 view artifacts."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Mapping

from src.geo import (
    build_lens_request,
    build_position_ref,
    build_projected_view_artifact,
    build_projected_view_layer_buffers,
    build_projection_request,
    plan_geo_degradation_actions,
    project_view_cells,
    render_projected_view_ascii,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


COMPUTE_BUDGET_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "compute_budget_profile_registry.json")
DEFAULT_TOPOLOGY_PROFILE_ID = "geo.topology.r3_infinite"
DEFAULT_PARTITION_PROFILE_ID = "geo.partition.grid_zd"
DEFAULT_METRIC_PROFILE_ID = "geo.metric.euclidean"
DEFAULT_COMPUTE_PROFILE_ID = "compute.default"
DEFAULT_MAP_VIEW_TYPE_ID = "view.map_ortho"
DEFAULT_MINIMAP_VIEW_TYPE_ID = "view.minimap"
DEFAULT_MAP_LAYERS = [
    "layer.orbits",
    "layer.terrain_stub",
    "layer.water_ocean",
    "layer.water_river",
    "layer.water_lake",
    "layer.refinement_status",
    "layer.temperature",
    "layer.tide_height_proxy",
    "layer.tide_offset",
    "layer.wind_vector",
    "layer.pollution",
    "layer.geometry_occupancy",
    "layer.infrastructure_stub",
    "layer.entity_markers_stub",
]
DEFAULT_MINIMAP_LAYERS = [
    "layer.orbits",
    "layer.terrain_stub",
    "layer.water_ocean",
    "layer.water_river",
    "layer.water_lake",
    "layer.refinement_status",
    "layer.temperature",
    "layer.tide_height_proxy",
    "layer.wind_vector",
    "layer.geometry_occupancy",
]
_MAP_VIEW_CACHE: dict[str, dict] = {}
_MAP_VIEW_CACHE_MAX = 128


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


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


def _compute_profile_rows() -> dict[str, dict]:
    payload = _as_map(_registry_payload(COMPUTE_BUDGET_PROFILE_REGISTRY_REL))
    rows = list(payload.get("compute_budget_profiles") or _as_map(payload.get("record")).get("compute_budget_profiles") or [])
    out = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("compute_profile_id", ""))):
        token = str(row.get("compute_profile_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def debug_view_limit_for_compute_profile(compute_profile_id: str) -> int:
    row = dict(_compute_profile_rows().get(str(compute_profile_id or DEFAULT_COMPUTE_PROFILE_ID).strip()) or {})
    evaluation_cap = int(max(1, _as_int(row.get("evaluation_cap_per_tick", 256), 256)))
    return int(max(1, min(4, evaluation_cap // 128)))


def _view_budget_payload(*, compute_profile_id: str, view_type_id: str) -> dict:
    row = dict(_compute_profile_rows().get(str(compute_profile_id or DEFAULT_COMPUTE_PROFILE_ID).strip()) or {})
    evaluation_cap = int(max(1, _as_int(row.get("evaluation_cap_per_tick", 256), 256)))
    max_projection_cells = int(max(9, min(144, evaluation_cap // 2)))
    if str(view_type_id or "").strip() == DEFAULT_MINIMAP_VIEW_TYPE_ID:
        max_projection_cells = int(max(9, min(49, max_projection_cells // 2)))
    return {
        "max_projection_cells_per_view": int(max_projection_cells),
        "max_neighbor_radius_noncritical": 4 if str(view_type_id or "").strip() == DEFAULT_MAP_VIEW_TYPE_ID else 2,
        "max_path_expansions": int(max(16, min(128, evaluation_cap))),
        "allow_defer_derived_views": False,
    }


def _cache_lookup(cache_key: str) -> dict | None:
    cached = _MAP_VIEW_CACHE.get(str(cache_key))
    if not isinstance(cached, dict):
        return None
    return copy.deepcopy(dict(cached))


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _MAP_VIEW_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_MAP_VIEW_CACHE) > _MAP_VIEW_CACHE_MAX:
        for stale_key in sorted(_MAP_VIEW_CACHE.keys())[:-_MAP_VIEW_CACHE_MAX]:
            _MAP_VIEW_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


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
    compute_profile_id: str = DEFAULT_COMPUTE_PROFILE_ID,
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
    requested_resolution_spec = {**_default_resolution_spec(view_type_id), **_as_map(resolution_spec)}
    requested_extent_spec = {**_default_extent_spec(view_type_id), **_as_map(extent_spec), "axis_order": ["x", "y"]}
    normalized_perceived = _normalized_perceived_model(perceived_model, lens_id=str(lens_id or "").strip())
    current_tick = int(max(0, _as_int(_as_map(_as_map(normalized_perceived).get("time_state")).get("tick", 0), 0)))
    budget_plan = plan_geo_degradation_actions(
        suite_id="ux0.{}".format(role),
        current_tick=current_tick,
        budget_payload=_view_budget_payload(
            compute_profile_id=str(compute_profile_id or DEFAULT_COMPUTE_PROFILE_ID).strip() or DEFAULT_COMPUTE_PROFILE_ID,
            view_type_id=view_type_id,
        ),
        requested_resolution_spec=requested_resolution_spec,
        requested_neighbor_radius=int(max(0, _as_int(requested_extent_spec.get("radius_cells", 0), 0))),
        requested_path_max_expansions=64,
        projected_cell_estimate=int(
            max(1, _as_int(requested_resolution_spec.get("width", 1), 1) * _as_int(requested_resolution_spec.get("height", 1), 1))
        ),
        view_type_id=str(view_type_id or DEFAULT_MAP_VIEW_TYPE_ID).strip() or DEFAULT_MAP_VIEW_TYPE_ID,
    )
    effective_resolution_spec = {**requested_resolution_spec, **_as_map(budget_plan.get("effective_resolution_spec"))}
    cache_key = canonical_sha256(
        {
            "truth_hash_anchor": str(truth_hash_anchor or "").strip(),
            "role": role,
            "view_type_id": str(view_type_id or DEFAULT_MAP_VIEW_TYPE_ID).strip() or DEFAULT_MAP_VIEW_TYPE_ID,
            "origin_position_ref": dict(origin),
            "lens_id": str(lens_id or "").strip(),
            "selected_layer_ids": list(layers),
            "compute_profile_id": str(compute_profile_id or DEFAULT_COMPUTE_PROFILE_ID).strip() or DEFAULT_COMPUTE_PROFILE_ID,
            "effective_resolution_spec": dict(effective_resolution_spec),
            "extent_spec": dict(requested_extent_spec),
            "perceived_model_hash": canonical_sha256(normalized_perceived),
            "authority_context_hash": canonical_sha256(dict(authority_context or {})),
            "layer_source_hash": canonical_sha256(dict(layer_source_payloads or {})),
        }
    )
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached
    projection_request = build_projection_request(
        request_id="projection_request.{}".format(role),
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec=dict(requested_extent_spec),
        resolution_spec=dict(effective_resolution_spec),
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
        "budget_plan": dict(budget_plan),
        "cache_key": cache_key,
        "cache_policy_id": "cache.truth_anchor_keyed",
        "worldgen_requests": [
            dict(row)
            for row in list(_as_map(projection_result).get("worldgen_requests") or [])
            if isinstance(row, Mapping)
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


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
    compute_profile_id: str = DEFAULT_COMPUTE_PROFILE_ID,
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
        compute_profile_id=compute_profile_id,
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
        compute_profile_id=compute_profile_id,
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
    "DEFAULT_COMPUTE_PROFILE_ID",
    "DEFAULT_MINIMAP_LAYERS",
    "DEFAULT_MINIMAP_VIEW_TYPE_ID",
    "build_map_view_set",
    "build_map_view_surface",
    "debug_view_limit_for_compute_profile",
]
