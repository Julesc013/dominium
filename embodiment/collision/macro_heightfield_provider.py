"""Deterministic EARTH-6 macro heightfield terrain collision provider."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key, geo_cell_key_from_position, geo_cell_key_neighbors
from worldgen.mw.mw_surface_refiner_l3 import normalize_surface_tile_artifact_rows


DEFAULT_COLLISION_PROVIDER_ID = "collision.macro_heightfield_default"
DEFAULT_MOVEMENT_SLOPE_PARAMS_ID = "slope.mvp_default"
COLLISION_PROVIDER_REGISTRY_REL = os.path.join("data", "registries", "collision_provider_registry.json")
MOVEMENT_SLOPE_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "movement_slope_params_registry.json")
MACRO_HEIGHTFIELD_PROVIDER_VERSION = "EARTH6-3"
_HEIGHTFIELD_SAMPLE_CACHE: Dict[str, dict] = {}


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, TypeError, ValueError):
        return {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _vector3_int(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


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


def collision_provider_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(COLLISION_PROVIDER_REGISTRY_REL),
        row_key="collision_providers",
        id_key="provider_id",
    )


def movement_slope_params_rows_by_id(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(MOVEMENT_SLOPE_PARAMS_REGISTRY_REL),
        row_key="movement_slope_params",
        id_key="slope_params_id",
    )


def _sorted_unique_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _tile_hash(cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(cell_key) or {}
    return canonical_sha256(_semantic_cell_key(key_row)) if key_row else ""


def _effective_height_proxy(artifact_row: Mapping[str, object], geometry_row: Mapping[str, object] | None = None) -> int:
    geometry = _as_map(geometry_row)
    if geometry:
        height_value = _as_int(geometry.get("height_proxy", 0), 0)
        if height_value > 0:
            return int(height_value)
    extensions = _as_map(_as_map(artifact_row).get("extensions"))
    elevation = _as_map(_as_map(artifact_row).get("elevation_params_ref"))
    return int(
        max(
            0,
            _as_int(
                extensions.get(
                    "hydrology_effective_height_proxy",
                    elevation.get("height_proxy", 0),
                ),
                0,
            ),
        )
    )


def _artifact_rows_by_cell_hash(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_surface_tile_artifact_rows(rows):
        cell_hash = _tile_hash(row.get("tile_cell_key"))
        if cell_hash:
            out[cell_hash] = dict(row)
    return out


def _position_hint_extensions(*, body_row: Mapping[str, object] | None, body_state_row: Mapping[str, object] | None) -> dict:
    body_ext = _as_map(_as_map(body_row).get("extensions"))
    state_ext = _as_map(_as_map(body_state_row).get("extensions"))
    return {
        **body_ext,
        **state_ext,
    }


def _candidate_tile_key(
    *,
    position_mm: Mapping[str, object],
    body_row: Mapping[str, object] | None,
    body_state_row: Mapping[str, object] | None,
    provider_row: Mapping[str, object] | None,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    hints = _position_hint_extensions(body_row=body_row, body_state_row=body_state_row)
    for key_name in (
        "surface_tile_cell_key",
        "geo_cell_key",
        "observer_tile_cell_key",
    ):
        candidate = _coerce_cell_key(hints.get(key_name))
        if candidate:
            return candidate

    provider_ext = _as_map(_as_map(provider_row).get("extensions"))
    chart_id = str(hints.get("surface_chart_id", "")).strip() or str(provider_ext.get("chart_id", "")).strip()
    topology_profile_id = str(hints.get("topology_profile_id", "")).strip() or str(
        provider_ext.get("topology_profile_id", "geo.topology.sphere_surface_s2")
    ).strip()
    partition_profile_id = str(hints.get("partition_profile_id", "")).strip() or str(
        provider_ext.get("partition_profile_id", "geo.partition.atlas_tiles")
    ).strip()
    if not chart_id:
        chart_id = "chart.atlas.north" if int(_as_int(position_mm.get("y", 0), 0)) >= 0 else "chart.atlas.south"
    resolution = geo_cell_key_from_position(
        {
            "x": int(_as_int(position_mm.get("x", 0), 0)),
            "y": int(_as_int(position_mm.get("y", 0), 0)),
            "refinement_level": int(max(0, _as_int(hints.get("refinement_level", 0), 0))),
            "chart_id": chart_id,
        },
        topology_profile_id=topology_profile_id,
        partition_profile_id=partition_profile_id,
        chart_id=chart_id,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    return _coerce_cell_key(resolution) or {}


def _approx_magnitude_permille(x_permille: int, y_permille: int) -> int:
    abs_x = abs(int(x_permille))
    abs_y = abs(int(y_permille))
    high = max(abs_x, abs_y)
    low = min(abs_x, abs_y)
    return int(high + (low // 2))


def _approx_slope_angle_mdeg(gradient_permille: int) -> int:
    magnitude = int(max(0, int(gradient_permille)))
    if magnitude <= 1000:
        return int((magnitude * 45_000) // 1000)
    return int(_clamp(45_000 + (((magnitude - 1000) * 30_000) // 3000), 0, 78_000))


def _neighbor_rows(
    *,
    tile_cell_key: Mapping[str, object],
    artifact_rows_by_hash: Mapping[str, object],
    geometry_rows_by_key: Mapping[str, object] | None,
) -> dict:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    base_index = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(base_index) < 2:
        base_index.append(0)
    base_u = int(base_index[0])
    base_v = int(base_index[1])
    neighbor_payload = geo_cell_key_neighbors(key_row, 1)
    neighbors = [
        _coerce_cell_key(item)
        for item in list(_as_map(neighbor_payload).get("neighbors") or [])
        if _coerce_cell_key(item)
    ]
    neighbors = sorted(
        neighbors,
        key=lambda row: (
            str(row.get("chart_id", "")),
            int(_as_int(row.get("refinement_level", 0), 0)),
            list(row.get("index_tuple") or []),
        ),
    )
    geometry_by_hash = dict((str(key), dict(value)) for key, value in dict(geometry_rows_by_key or {}).items())
    resolved = {}
    for candidate in neighbors:
        candidate_index = [int(item) for item in list(candidate.get("index_tuple") or [])]
        while len(candidate_index) < 2:
            candidate_index.append(0)
        delta_u = int(candidate_index[0]) - base_u
        delta_v = int(candidate_index[1]) - base_v
        direction = ""
        if delta_u > 0 and abs(delta_u) >= abs(delta_v):
            direction = "east"
        elif delta_u < 0 and abs(delta_u) >= abs(delta_v):
            direction = "west"
        elif delta_v > 0:
            direction = "north"
        elif delta_v < 0:
            direction = "south"
        if not direction or direction in resolved:
            continue
        cell_hash = _tile_hash(candidate)
        artifact = _as_map(artifact_rows_by_hash.get(cell_hash))
        geometry_row = _as_map(geometry_by_hash.get(cell_hash))
        if artifact:
            resolved[direction] = {
                "tile_cell_key": dict(candidate),
                "height_proxy": int(_effective_height_proxy(artifact, geometry_row)),
            }
    return resolved


def _cached_heightfield_sample(cache_key: str) -> dict:
    cached = _HEIGHTFIELD_SAMPLE_CACHE.get(str(cache_key))
    return dict(cached) if isinstance(cached, dict) else {}


def invalidate_macro_heightfield_cache_for_tiles(tile_cell_keys: object) -> dict:
    dirty_hashes = set(_tile_hash(row) for row in list(tile_cell_keys or []) if _tile_hash(row))
    if not dirty_hashes:
        payload = {"result": "complete", "invalidated_entries": 0, "dirty_tile_count": 0, "deterministic_fingerprint": ""}
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    removed = 0
    for cache_key in list(_HEIGHTFIELD_SAMPLE_CACHE.keys()):
        row = _as_map(_HEIGHTFIELD_SAMPLE_CACHE.get(cache_key))
        cache_hashes = set(_sorted_unique_strings(_as_map(row.get("extensions")).get("tile_hashes")))
        if dirty_hashes.intersection(cache_hashes):
            _HEIGHTFIELD_SAMPLE_CACHE.pop(cache_key, None)
            removed += 1
    payload = {
        "result": "complete",
        "invalidated_entries": int(removed),
        "dirty_tile_count": int(len(dirty_hashes)),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def resolve_macro_heightfield_sample(
    *,
    position_mm: Mapping[str, object] | None,
    body_row: Mapping[str, object] | None = None,
    body_state_row: Mapping[str, object] | None = None,
    surface_tile_rows: object = None,
    geometry_rows_by_key: Mapping[str, object] | None = None,
    provider_row: Mapping[str, object] | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    provider = _as_map(provider_row) or _as_map(collision_provider_rows_by_id().get(DEFAULT_COLLISION_PROVIDER_ID))
    provider_id = str(provider.get("provider_id", "")).strip() or DEFAULT_COLLISION_PROVIDER_ID
    provider_ext = _as_map(provider.get("extensions"))
    if str(provider.get("kind", "")).strip() != "macro_heightfield":
        payload = {
            "result": "refused",
            "provider_id": provider_id,
            "message": "provider '{}' is not a macro heightfield provider".format(provider_id),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    position = _vector3_int(position_mm)
    tile_cell_key = _candidate_tile_key(
        position_mm=position,
        body_row=body_row,
        body_state_row=body_state_row,
        provider_row=provider,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if not tile_cell_key:
        payload = {
            "result": "refused",
            "provider_id": provider_id,
            "message": "surface tile key could not be resolved for macro collision sample",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    artifact_rows_by_hash = _artifact_rows_by_cell_hash(surface_tile_rows)
    tile_hash = _tile_hash(tile_cell_key)
    artifact_row = _as_map(artifact_rows_by_hash.get(tile_hash))
    if not artifact_row:
        payload = {
            "result": "refused",
            "provider_id": provider_id,
            "tile_cell_key": dict(tile_cell_key),
            "message": "surface tile artifact is missing for collision sample",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    geometry_by_hash = dict((str(key), dict(value)) for key, value in dict(geometry_rows_by_key or {}).items())
    current_height = int(_effective_height_proxy(artifact_row, geometry_by_hash.get(tile_hash)))
    neighbors = _neighbor_rows(
        tile_cell_key=tile_cell_key,
        artifact_rows_by_hash=artifact_rows_by_hash,
        geometry_rows_by_key=geometry_rows_by_key,
    )
    east_height = int(_as_int(_as_map(neighbors.get("east")).get("height_proxy", current_height), current_height))
    west_height = int(_as_int(_as_map(neighbors.get("west")).get("height_proxy", current_height), current_height))
    north_height = int(_as_int(_as_map(neighbors.get("north")).get("height_proxy", current_height), current_height))
    south_height = int(_as_int(_as_map(neighbors.get("south")).get("height_proxy", current_height), current_height))

    sample_mode = "nearest"
    if bool(provider_ext.get("bilinear_stub_enabled", False)) and str(provider_ext.get("height_sample_mode", "")).strip() == "bilinear_stub":
        sample_mode = "bilinear_stub"
    quantization_mm = int(max(1, _as_int(provider_ext.get("cache_quantization_mm", 256), 256)))
    interpolation_span_mm = int(max(1, _as_int(provider_ext.get("interpolation_span_mm", 4096), 4096)))
    cache_key = canonical_sha256(
        {
            "provider_id": provider_id,
            "tile_hash": tile_hash,
            "position_quant": {
                "x": int(position["x"]) // quantization_mm,
                "y": int(position["y"]) // quantization_mm,
                "z": int(position["z"]) // quantization_mm,
            },
            "sample_mode": sample_mode,
            "neighbor_heights": {
                "current": int(current_height),
                "east": int(east_height),
                "west": int(west_height),
                "north": int(north_height),
                "south": int(south_height),
            },
        }
    )
    cached = _cached_heightfield_sample(cache_key)
    if cached:
        return cached

    terrain_height_mm = int(current_height)
    if sample_mode == "bilinear_stub":
        local_x = int(position["x"]) % interpolation_span_mm
        local_y = int(position["y"]) % interpolation_span_mm
        weight_x = int(_clamp((local_x * 1000) // interpolation_span_mm, 0, 1000))
        weight_y = int(_clamp((local_y * 1000) // interpolation_span_mm, 0, 1000))
        x_blend = int(((current_height * (1000 - weight_x)) + (east_height * weight_x)) // 1000)
        y_blend = int(((current_height * (1000 - weight_y)) + (north_height * weight_y)) // 1000)
        terrain_height_mm = int((x_blend + y_blend) // 2)

    sample_offset_mm = int(max(1, _as_int(provider_ext.get("slope_sample_offset_mm", 2048), 2048)))
    grad_x_permille = int(((east_height - west_height) * 1000) // max(1, sample_offset_mm * 2))
    grad_y_permille = int(((north_height - south_height) * 1000) // max(1, sample_offset_mm * 2))
    gradient_permille = int(_approx_magnitude_permille(grad_x_permille, grad_y_permille))
    slope_angle_mdeg = int(_approx_slope_angle_mdeg(gradient_permille))
    payload = {
        "result": "complete",
        "provider_id": provider_id,
        "tile_object_id": str(artifact_row.get("tile_object_id", "")).strip(),
        "tile_cell_key": dict(tile_cell_key),
        "terrain_height_mm": int(terrain_height_mm),
        "sample_mode": sample_mode,
        "slope_gradient_permille": {"x": int(grad_x_permille), "y": int(grad_y_permille)},
        "downhill_vector_permille": {"x": int(-grad_x_permille), "y": int(-grad_y_permille)},
        "slope_angle_mdeg": int(slope_angle_mdeg),
        "sampling_bounded": True,
        "deterministic_fingerprint": "",
        "extensions": {
            "cache_key": cache_key,
            "tile_hashes": _sorted_unique_strings(
                [
                    tile_hash,
                    _tile_hash(_as_map(neighbors.get("east")).get("tile_cell_key")),
                    _tile_hash(_as_map(neighbors.get("west")).get("tile_cell_key")),
                    _tile_hash(_as_map(neighbors.get("north")).get("tile_cell_key")),
                    _tile_hash(_as_map(neighbors.get("south")).get("tile_cell_key")),
                ]
            ),
            "neighbor_heights": {
                "current": int(current_height),
                "east": int(east_height),
                "west": int(west_height),
                "north": int(north_height),
                "south": int(south_height),
            },
            "sample_offset_mm": int(sample_offset_mm),
            "interpolation_span_mm": int(interpolation_span_mm),
            "contact_snap_tolerance_mm": int(max(0, _as_int(provider_ext.get("contact_snap_tolerance_mm", 180), 180))),
            "source": MACRO_HEIGHTFIELD_PROVIDER_VERSION,
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    _HEIGHTFIELD_SAMPLE_CACHE[cache_key] = dict(payload)
    return payload


__all__ = [
    "DEFAULT_COLLISION_PROVIDER_ID",
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID",
    "collision_provider_rows_by_id",
    "invalidate_macro_heightfield_cache_for_tiles",
    "movement_slope_params_rows_by_id",
    "resolve_macro_heightfield_sample",
]
