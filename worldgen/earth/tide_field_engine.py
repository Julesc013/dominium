"""Deterministic EARTH-3 tide field helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key

from .climate_field_engine import is_earth_surface_tile
from .tide_phase_engine import (
    EARTH_TIDE_PHASE_SCALE,
    lunar_phase_from_params,
    phase_carrier_permille,
    rotation_phase_from_params,
)


DEFAULT_TIDE_PARAMS_ID = "tide.earth_stub_default"
TIDE_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "tide_params_registry.json")
EARTH_TIDE_ENGINE_VERSION = "EARTH3-4"


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


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


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


def tide_params_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(TIDE_PARAMS_REGISTRY_REL),
        row_key="tide_params",
        id_key="tide_params_id",
    )


def _legacy_cell_alias_from_tile_key(tile_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    extensions = _as_map(key_row.get("extensions"))
    alias = str(extensions.get("legacy_cell_alias", "")).strip()
    if alias:
        return alias
    base_chart_id = str(extensions.get("base_chart_id", "")).strip().lower()
    chart_token = "north"
    if "south" in base_chart_id or "south" in str(key_row.get("chart_id", "")).strip().lower():
        chart_token = "south"
    index_tuple = list(key_row.get("index_tuple") or [])
    u_idx = int(index_tuple[0]) if len(index_tuple) > 0 else 0
    v_idx = int(index_tuple[1]) if len(index_tuple) > 1 else 0
    return "atlas.{}.{}.{}".format(chart_token, u_idx, v_idx)


def _geo_hash(tile_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    return canonical_sha256(_semantic_cell_key(key_row)) if key_row else ""


def _geo_sort_tuple(tile_cell_key: Mapping[str, object]) -> tuple:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    chart_id = str(key_row.get("chart_id", "")).strip()
    index_tuple = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        chart_id,
        int(_as_int(key_row.get("refinement_level", 0), 0)),
        int(index_tuple[1]),
        int(index_tuple[0]),
        int(index_tuple[2]),
    )


def _material_or_surface_class(artifact_row: Mapping[str, object]) -> tuple[str, str]:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    material_id = str(row.get("material_baseline_id", "")).strip() or "material.stone_basic"
    surface_class_id = str(extensions.get("surface_class_id", "")).strip()
    if not surface_class_id:
        if material_id == "material.water":
            surface_class_id = "surface.class.ocean"
        elif "ice" in material_id:
            surface_class_id = "surface.class.ice"
        else:
            surface_class_id = "surface.class.land"
    return (material_id, surface_class_id)


def _latitude_factor_permille(latitude_mdeg: int, tide_params_row: Mapping[str, object]) -> int:
    extensions = _as_map(_as_map(tide_params_row).get("extensions"))
    floor = _clamp(_as_int(extensions.get("latitude_floor_permille", 450), 450), 0, 1000)
    peak = _clamp(_as_int(extensions.get("latitude_peak_permille", 1000), 1000), floor, 1500)
    distance_from_mid = abs(abs(int(latitude_mdeg)) - 45_000)
    return _clamp(peak - ((distance_from_mid * (peak - floor)) // 45_000), floor, peak)


def _surface_factor_permille(artifact_row: Mapping[str, object], tide_params_row: Mapping[str, object]) -> int:
    row = _as_map(artifact_row)
    tide_ext = _as_map(_as_map(tide_params_row).get("extensions"))
    row_ext = _as_map(row.get("extensions"))
    coastal_proximity = _clamp(_as_int(row_ext.get("coastal_proximity_permille", 0), 0), 0, 1000)
    inland = _clamp(_as_int(tide_params_row.get("inland_damping_factor", 180), 180), 0, 1000)
    ocean_factor = _clamp(_as_int(tide_ext.get("ocean_factor_permille", 1000), 1000), 0, 1500)
    ice_factor = _clamp(_as_int(tide_ext.get("ice_factor_permille", inland), inland), 0, 1500)
    coastal_boost = _clamp(_as_int(tide_ext.get("coastal_boost_permille", 200), 200), 0, 1000)
    _material_id, surface_class_id = _material_or_surface_class(row)
    if surface_class_id == "surface.class.ocean":
        return _clamp(ocean_factor + ((coastal_proximity * coastal_boost) // 1000), 0, 2000)
    if surface_class_id == "surface.class.ice":
        return _clamp(ice_factor + ((coastal_proximity * coastal_boost) // 3000), 0, 2000)
    return _clamp(inland + ((coastal_proximity * coastal_boost) // 2000), 0, 2000)


def build_tide_coupling_stub(*, tide_evaluation: Mapping[str, object]) -> dict:
    row = _as_map(tide_evaluation)
    tide_height_value = int(_as_int(row.get("tide_height_value", 0), 0))
    coastal_proximity = int(_as_int(row.get("coastal_proximity_permille", 0), 0))
    surface_class_id = str(row.get("surface_class_id", "")).strip()
    estuary_bias = tide_height_value if coastal_proximity >= 500 else 0
    coastal_hazard_bias = min(1000, abs(tide_height_value) * 4)
    return {
        "future.ocean.surface_height_bias": {
            "hook_kind": "field_proxy",
            "field_type_id": "field.tide_height_proxy",
            "enabled": surface_class_id == "surface.class.ocean",
            "signed_value": int(tide_height_value),
        },
        "future.hazard.coastal_flood_bias": {
            "hook_kind": "hazard_proxy",
            "field_type_id": "field.tide_height_proxy",
            "enabled": coastal_proximity >= 500,
            "bias_permille": int(coastal_hazard_bias),
        },
        "future.fluid.estuary_flow_bias": {
            "hook_kind": "flow_proxy",
            "field_type_id": "field.tide_height_proxy",
            "enabled": coastal_proximity >= 500,
            "signed_value": int(estuary_bias),
        },
    }


def evaluate_earth_tile_tide(
    *,
    artifact_row: Mapping[str, object],
    tide_params_row: Mapping[str, object],
    current_tick: int,
) -> dict:
    row = _as_map(artifact_row)
    tide_row = _as_map(tide_params_row)
    extensions = _as_map(row.get("extensions"))
    tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
    latitude_mdeg = _as_int(extensions.get("latitude_mdeg", 0), 0)
    longitude_mdeg = _as_int(extensions.get("longitude_mdeg", 0), 0)
    tick = max(0, _as_int(current_tick, 0))
    lunar_phase_value = lunar_phase_from_params(
        tick=tick,
        tide_params_row=tide_row,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    rotation_phase_value = rotation_phase_from_params(
        tick=tick,
        tide_params_row=tide_row,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    carrier_permille = phase_carrier_permille(
        rotation_phase_value=rotation_phase_value,
        lunar_phase_value=lunar_phase_value,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    amplitude = max(0, _as_int(tide_row.get("amplitude", 0), 0))
    latitude_factor = _latitude_factor_permille(latitude_mdeg, tide_row)
    surface_factor = _surface_factor_permille(row, tide_row)
    tide_height_value = int((amplitude * latitude_factor * surface_factor * carrier_permille) // 1_000_000_000)
    material_id, surface_class_id = _material_or_surface_class(row)
    coastal_proximity = _clamp(_as_int(extensions.get("coastal_proximity_permille", 0), 0), 0, 1000)
    payload = {
        "tile_object_id": str(row.get("tile_object_id", "")).strip(),
        "planet_object_id": str(row.get("planet_object_id", "")).strip(),
        "tile_cell_key": dict(tile_cell_key),
        "cell_id": _legacy_cell_alias_from_tile_key(tile_cell_key),
        "current_tick": int(tick),
        "lunar_phase": int(lunar_phase_value),
        "rotation_phase": int(rotation_phase_value),
        "carrier_permille": int(carrier_permille),
        "tide_height_value": int(tide_height_value),
        "latitude_mdeg": int(latitude_mdeg),
        "longitude_mdeg": int(longitude_mdeg),
        "latitude_factor_permille": int(latitude_factor),
        "surface_factor_permille": int(surface_factor),
        "coastal_proximity_permille": int(coastal_proximity),
        "surface_class_id": surface_class_id,
        "material_baseline_id": material_id,
        "coupling_hooks": build_tide_coupling_stub(
            tide_evaluation={
                "tide_height_value": int(tide_height_value),
                "coastal_proximity_permille": int(coastal_proximity),
                "surface_class_id": surface_class_id,
            }
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_tide_field_updates(
    *,
    tide_row: Mapping[str, object],
    tide_evaluations: Sequence[Mapping[str, object]],
) -> List[dict]:
    evaluations = [dict(row) for row in list(tide_evaluations or []) if isinstance(row, Mapping)]
    if not evaluations:
        return []
    planet_id = str(evaluations[0].get("planet_object_id", "")).strip()
    tide_params_id = str(_as_map(tide_row).get("tide_params_id", "")).strip() or DEFAULT_TIDE_PARAMS_ID
    field_updates: List[dict] = []
    for row in evaluations:
        cell_id = str(row.get("cell_id", "")).strip()
        geo_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not cell_id:
            continue
        field_updates.append(
            {
                "field_id": "field.tide_height_proxy.surface.{}".format(planet_id),
                "field_type_id": "field.tide_height_proxy",
                "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                "resolution_level": "macro",
                "cell_id": cell_id,
                "geo_cell_key": dict(geo_cell_key),
                "value": int(_as_int(row.get("tide_height_value", 0), 0)),
                "extensions": {
                    "tide_params_id": tide_params_id,
                    "source": EARTH_TIDE_ENGINE_VERSION,
                },
            }
        )
    return sorted(
        field_updates,
        key=lambda row: (
            str(row.get("field_id", "")),
            _geo_sort_tuple(row.get("geo_cell_key") or {}),
            str(row.get("cell_id", "")),
        ),
    )


def tide_bucket_id(*, tile_cell_key: Mapping[str, object], update_interval_ticks: int) -> int:
    interval = max(1, _as_int(update_interval_ticks, 1))
    return int(int(_geo_hash(tile_cell_key)[:8], 16) % interval)


def due_bucket_ids(*, current_tick: int, last_processed_tick: int | None, update_interval_ticks: int) -> List[int]:
    interval = max(1, _as_int(update_interval_ticks, 1))
    tick = max(0, _as_int(current_tick, 0))
    if last_processed_tick is None:
        return list(range(interval))
    previous = _as_int(last_processed_tick, -1)
    if previous < 0:
        return list(range(interval))
    if tick <= previous:
        return [int(tick % interval)]
    if (tick - previous) >= interval:
        return list(range(interval))
    return sorted(set(int(step % interval) for step in range(previous + 1, tick + 1)))


def build_earth_tide_update_plan(
    *,
    artifact_rows: object,
    tide_params_row: Mapping[str, object],
    current_tick: int,
    last_processed_tick: int | None,
    max_tiles_per_update: int,
) -> dict:
    tide_row = _as_map(tide_params_row)
    interval = max(1, _as_int(tide_row.get("update_interval_ticks", 1), 1))
    bucket_ids = due_bucket_ids(
        current_tick=current_tick,
        last_processed_tick=last_processed_tick,
        update_interval_ticks=interval,
    )
    candidates: List[dict] = []
    for raw in list(artifact_rows or []):
        row = _as_map(raw)
        if not row or not is_earth_surface_tile(row):
            continue
        tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not tile_cell_key:
            continue
        bucket_id = tide_bucket_id(tile_cell_key=tile_cell_key, update_interval_ticks=interval)
        if bucket_id not in bucket_ids:
            continue
        candidates.append(
            {
                "artifact_row": dict(row),
                "bucket_id": int(bucket_id),
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "tile_cell_key": dict(tile_cell_key),
            }
        )
    candidates = sorted(
        candidates,
        key=lambda row: (
            int(_as_int(row.get("bucket_id", 0), 0)),
            _geo_sort_tuple(row.get("tile_cell_key") or {}),
            str(row.get("tile_object_id", "")),
        ),
    )
    budget = max(0, _as_int(max_tiles_per_update, 0))
    selected = list(candidates[:budget]) if budget > 0 else []
    skipped = list(candidates[budget:]) if budget > 0 else list(candidates)
    evaluations = [
        evaluate_earth_tile_tide(
            artifact_row=dict(row.get("artifact_row") or {}),
            tide_params_row=tide_row,
            current_tick=int(current_tick),
        )
        for row in selected
    ]
    field_updates = build_tide_field_updates(
        tide_row=tide_row,
        tide_evaluations=evaluations,
    )
    result = {
        "tide_params_id": str(tide_row.get("tide_params_id", "")).strip() or DEFAULT_TIDE_PARAMS_ID,
        "due_bucket_ids": [int(item) for item in list(bucket_ids or [])],
        "selected_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in selected if str(row.get("tile_object_id", "")).strip()],
        "skipped_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in skipped if str(row.get("tile_object_id", "")).strip()],
        "evaluations": [dict(row) for row in evaluations],
        "field_updates": [dict(row) for row in field_updates],
        "cost_units_used": int(len(selected)),
        "degraded": bool(len(skipped) > 0),
        "degrade_reason": "degrade.earth_tide.budget" if skipped else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def tide_window_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for row in list(rows or []):
        payload = _as_map(row)
        normalized.append(
            {
                "tile_object_id": str(payload.get("tile_object_id", "")).strip(),
                "tide_height_value": int(_as_int(payload.get("tide_height_value", 0), 0)),
                "lunar_phase": int(_as_int(payload.get("lunar_phase", 0), 0)),
                "rotation_phase": int(_as_int(payload.get("rotation_phase", 0), 0)),
                "surface_class_id": str(payload.get("surface_class_id", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


__all__ = [
    "DEFAULT_TIDE_PARAMS_ID",
    "EARTH_TIDE_ENGINE_VERSION",
    "TIDE_PARAMS_REGISTRY_REL",
    "build_earth_tide_update_plan",
    "build_tide_coupling_stub",
    "build_tide_field_updates",
    "due_bucket_ids",
    "evaluate_earth_tile_tide",
    "tide_bucket_id",
    "tide_params_rows",
    "tide_window_hash",
]
