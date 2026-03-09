"""Deterministic EARTH-2 seasonal climate field helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key

from .season_phase_engine import (
    EARTH_ORBIT_PHASE_SCALE,
    axial_tilt_mdeg,
    earth_orbit_phase_from_params,
    solar_declination_mdeg,
)


DEFAULT_EARTH_CLIMATE_PARAMS_ID = "climate.earth_stub_default"
EARTH_CLIMATE_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "earth_climate_params_registry.json")
EARTH_CLIMATE_ENGINE_VERSION = "EARTH2-4"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


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


def _sorted_unique_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


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


def earth_climate_params_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(EARTH_CLIMATE_PARAMS_REGISTRY_REL),
        row_key="earth_climate_params",
        id_key="climate_params_id",
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


def _route_tags(artifact_row: Mapping[str, object]) -> List[str]:
    extensions = _as_map(_as_map(artifact_row).get("extensions"))
    return _sorted_unique_strings(list(extensions.get("route_tags") or extensions.get("planet_tags") or []))


def is_earth_surface_tile(artifact_row: Mapping[str, object]) -> bool:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    tags = set(_route_tags(row))
    if "planet.earth" in tags:
        return True
    return str(extensions.get("selected_generator_id", "")).strip() == "gen.surface.earth_stub"


def climate_bucket_id(*, tile_cell_key: Mapping[str, object], update_interval_ticks: int) -> int:
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


def _height_proxy(artifact_row: Mapping[str, object], geometry_row: Mapping[str, object] | None = None) -> int:
    geometry = _as_map(geometry_row)
    if geometry:
        value = _as_int(geometry.get("height_proxy", 0), 0)
        if value > 0:
            return value
    extensions = _as_map(_as_map(artifact_row).get("extensions"))
    elevation = _as_map(_as_map(artifact_row).get("elevation_params_ref"))
    return max(
        0,
        _as_int(
            extensions.get(
                "hydrology_effective_height_proxy",
                elevation.get("height_proxy", 0),
            ),
            0,
        ),
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


def evaluate_earth_tile_climate(
    *,
    artifact_row: Mapping[str, object],
    climate_params_row: Mapping[str, object],
    current_tick: int,
    geometry_row: Mapping[str, object] | None = None,
) -> dict:
    row = _as_map(artifact_row)
    climate = _as_map(climate_params_row)
    climate_ext = _as_map(climate.get("extensions"))
    extensions = _as_map(row.get("extensions"))
    tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
    latitude_mdeg = _as_int(extensions.get("latitude_mdeg", 0), 0)
    longitude_mdeg = _as_int(extensions.get("longitude_mdeg", 0), 0)
    tick = max(0, _as_int(current_tick, 0))
    orbit_phase = earth_orbit_phase_from_params(tick=tick, climate_params_row=climate, phase_scale=EARTH_ORBIT_PHASE_SCALE)
    tilt_mdeg = axial_tilt_mdeg(climate)
    declination_mdeg = solar_declination_mdeg(orbit_phase=orbit_phase, axial_tilt_mdeg=tilt_mdeg, phase_scale=EARTH_ORBIT_PHASE_SCALE)
    tilt_weight = _clamp(_as_int(climate_ext.get("seasonal_tilt_weight_permille", 1000), 1000), 0, 1000)
    effective_declination_mdeg = (declination_mdeg * tilt_weight) // 1000
    equatorial_daylight = max(100, _as_int(climate_ext.get("equatorial_daylight_permille", 1000), 1000))
    polar_floor = _clamp(_as_int(climate_ext.get("polar_floor_permille", 0), 0), 0, equatorial_daylight)
    solar_distance = abs(latitude_mdeg - effective_declination_mdeg)
    daylight_value = _clamp(equatorial_daylight - ((solar_distance * equatorial_daylight) // 90_000), polar_floor, equatorial_daylight)
    baseline_daylight = _clamp(
        equatorial_daylight - ((abs(latitude_mdeg) * equatorial_daylight) // 90_000),
        polar_floor,
        equatorial_daylight,
    )
    daylight_anomaly = int(daylight_value - baseline_daylight)
    lat_weight = 250 + ((abs(latitude_mdeg) * 750) // 90_000)
    base_equator = _as_int(climate.get("base_temp_equator", 303), 303)
    base_pole = _as_int(climate.get("base_temp_pole", 238), 238)
    base_temp = int(base_pole + (((90_000 - abs(latitude_mdeg)) * (base_equator - base_pole)) // 90_000))
    seasonal_amplitude = max(0, _as_int(climate.get("seasonal_amplitude", 0), 0))
    seasonal_delta = int((daylight_anomaly * seasonal_amplitude * lat_weight) // 1_000_000)
    altitude_units_per_km = max(1, _as_int(climate_ext.get("altitude_units_per_km", 1000), 1000))
    altitude_km = _height_proxy(row, geometry_row=geometry_row) // altitude_units_per_km
    lapse_rate = max(0, _as_int(climate.get("lapse_rate_per_km", 0), 0))
    altitude_lapse = int(max(0, altitude_km) * lapse_rate)
    material_id, surface_class_id = _material_or_surface_class(row)
    surface_bias = 2 if surface_class_id == "surface.class.ocean" else (-2 if surface_class_id == "surface.class.ice" else 0)
    temperature_value = _clamp(base_temp + seasonal_delta - altitude_lapse + surface_bias, 180, 360)

    shift_limit = max(0, _as_int(climate_ext.get("season_boundary_shift_mdeg", 4500), 4500))
    climate_shift_mdeg = _clamp(declination_mdeg // 2, -shift_limit, shift_limit)
    effective_latitude = abs(latitude_mdeg - climate_shift_mdeg)
    tropical_limit = _clamp(_as_int(climate_ext.get("tropical_band_max_mdeg", 24_000), 24_000), 5_000, 45_000)
    polar_limit = _clamp(_as_int(climate_ext.get("polar_band_min_mdeg", 64_000), 64_000), 40_000, 88_000)
    arid_min = _clamp(_as_int(climate_ext.get("arid_band_min_mdeg", 18_000), 18_000), 0, 60_000)
    arid_max = _clamp(_as_int(climate_ext.get("arid_band_max_mdeg", 36_000), 36_000), arid_min, 75_000)
    continent_score = _as_int(extensions.get("continent_score_permille", 0), 0)
    coastal_proximity = _as_int(extensions.get("coastal_proximity_permille", 1000), 1000)
    river_flag = bool(row.get("river_flag", False))
    lake_flag = bool(extensions.get("lake_flag", False))

    climate_band_id = "climate.band.temperate"
    if effective_latitude >= polar_limit or temperature_value <= (base_pole + 8):
        climate_band_id = "climate.band.polar"
    elif (
        surface_class_id == "surface.class.land"
        and effective_latitude >= arid_min
        and effective_latitude <= arid_max
        and continent_score >= 600
        and coastal_proximity <= 550
        and not river_flag
        and not lake_flag
    ):
        climate_band_id = "climate.band.arid"
    elif effective_latitude <= tropical_limit and temperature_value >= (base_equator - 18):
        climate_band_id = "climate.band.tropical"

    derived_tags = [climate_band_id]
    if river_flag:
        derived_tags.append("climate.feature.river")
    if lake_flag:
        derived_tags.append("climate.feature.lake")

    payload = {
        "tile_object_id": str(row.get("tile_object_id", "")).strip(),
        "planet_object_id": str(row.get("planet_object_id", "")).strip(),
        "tile_cell_key": dict(tile_cell_key),
        "cell_id": _legacy_cell_alias_from_tile_key(tile_cell_key),
        "current_tick": int(tick),
        "orbit_phase": int(orbit_phase),
        "declination_mdeg": int(declination_mdeg),
        "temperature_value": int(temperature_value),
        "daylight_value": int(daylight_value),
        "climate_band_id": climate_band_id,
        "derived_tags": _sorted_unique_strings(derived_tags),
        "biome_overlay_tags": _sorted_unique_strings(derived_tags),
        "latitude_mdeg": int(latitude_mdeg),
        "longitude_mdeg": int(longitude_mdeg),
        "surface_class_id": surface_class_id,
        "material_baseline_id": material_id,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_climate_field_updates(
    *,
    climate_row: Mapping[str, object],
    climate_evaluations: Sequence[Mapping[str, object]],
) -> List[dict]:
    evaluations = [dict(row) for row in list(climate_evaluations or []) if isinstance(row, Mapping)]
    if not evaluations:
        return []
    planet_id = str(evaluations[0].get("planet_object_id", "")).strip()
    climate_params_id = str(_as_map(climate_row).get("climate_params_id", "")).strip() or DEFAULT_EARTH_CLIMATE_PARAMS_ID
    field_updates: List[dict] = []
    for row in evaluations:
        cell_id = str(row.get("cell_id", "")).strip()
        geo_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not cell_id:
            continue
        field_updates.extend(
            [
                {
                    "field_id": "field.temperature.surface.{}".format(planet_id),
                    "field_type_id": "field.temperature",
                    "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("temperature_value", 0), 0)),
                    "extensions": {
                        "climate_params_id": climate_params_id,
                        "source": EARTH_CLIMATE_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.daylight.surface.{}".format(planet_id),
                    "field_type_id": "field.daylight",
                    "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("daylight_value", 0), 0)),
                    "extensions": {
                        "climate_params_id": climate_params_id,
                        "source": EARTH_CLIMATE_ENGINE_VERSION,
                    },
                },
            ]
        )
    return sorted(
        field_updates,
        key=lambda row: (
            str(row.get("field_id", "")),
            _geo_sort_tuple(row.get("geo_cell_key") or {}),
            str(row.get("cell_id", "")),
        ),
    )


def build_earth_climate_update_plan(
    *,
    artifact_rows: object,
    climate_params_row: Mapping[str, object],
    current_tick: int,
    last_processed_tick: int | None,
    max_tiles_per_update: int,
    geometry_rows_by_key: Mapping[str, object] | None = None,
) -> dict:
    climate_row = _as_map(climate_params_row)
    interval = max(1, _as_int(climate_row.get("update_interval_ticks", 1), 1))
    bucket_ids = due_bucket_ids(
        current_tick=current_tick,
        last_processed_tick=last_processed_tick,
        update_interval_ticks=interval,
    )
    candidates: List[dict] = []
    geometry_index = dict(geometry_rows_by_key or {})
    for raw in list(artifact_rows or []):
        row = _as_map(raw)
        if not row or not is_earth_surface_tile(row):
            continue
        tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not tile_cell_key:
            continue
        bucket_id = climate_bucket_id(tile_cell_key=tile_cell_key, update_interval_ticks=interval)
        if bucket_id not in bucket_ids:
            continue
        geo_hash = _geo_hash(tile_cell_key)
        candidates.append(
            {
                "artifact_row": dict(row),
                "bucket_id": int(bucket_id),
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "tile_cell_key": dict(tile_cell_key),
                "geo_hash": geo_hash,
                "geometry_row": dict(geometry_index.get(geo_hash) or {}),
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
        evaluate_earth_tile_climate(
            artifact_row=dict(row.get("artifact_row") or {}),
            climate_params_row=climate_row,
            current_tick=int(current_tick),
            geometry_row=dict(row.get("geometry_row") or {}),
        )
        for row in selected
    ]
    field_updates = build_climate_field_updates(
        climate_row=climate_row,
        climate_evaluations=evaluations,
    )
    result = {
        "climate_params_id": str(climate_row.get("climate_params_id", "")).strip() or DEFAULT_EARTH_CLIMATE_PARAMS_ID,
        "due_bucket_ids": [int(item) for item in list(bucket_ids or [])],
        "selected_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in selected if str(row.get("tile_object_id", "")).strip()],
        "skipped_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in skipped if str(row.get("tile_object_id", "")).strip()],
        "evaluations": [dict(row) for row in evaluations],
        "field_updates": [dict(row) for row in field_updates],
        "cost_units_used": int(len(selected)),
        "degraded": bool(len(skipped) > 0),
        "degrade_reason": "degrade.earth_climate.budget" if skipped else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def climate_window_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for row in list(rows or []):
        payload = _as_map(row)
        normalized.append(
            {
                "tile_object_id": str(payload.get("tile_object_id", "")).strip(),
                "temperature_value": int(_as_int(payload.get("temperature_value", 0), 0)),
                "daylight_value": int(_as_int(payload.get("daylight_value", 0), 0)),
                "climate_band_id": str(payload.get("climate_band_id", "")).strip(),
                "orbit_phase": int(_as_int(payload.get("orbit_phase", 0), 0)),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


__all__ = [
    "DEFAULT_EARTH_CLIMATE_PARAMS_ID",
    "EARTH_CLIMATE_ENGINE_VERSION",
    "EARTH_CLIMATE_PARAMS_REGISTRY_REL",
    "build_climate_field_updates",
    "build_earth_climate_update_plan",
    "climate_bucket_id",
    "climate_window_hash",
    "due_bucket_ids",
    "earth_climate_params_rows",
    "evaluate_earth_tile_climate",
    "is_earth_surface_tile",
]
