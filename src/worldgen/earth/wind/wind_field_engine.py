"""Deterministic EARTH-7 wind field helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key

from ..climate_field_engine import is_earth_surface_tile
from ..season_phase_engine import (
    EARTH_ORBIT_PHASE_SCALE,
    axial_tilt_mdeg,
    earth_orbit_phase_from_params,
    solar_declination_mdeg,
)


DEFAULT_WIND_PARAMS_ID = "wind.earth_stub_default"
WIND_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "wind_params_registry.json")
EARTH_WIND_ENGINE_VERSION = "EARTH7-3"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "..", ".."))


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


def wind_params_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(WIND_PARAMS_REGISTRY_REL),
        row_key="wind_params",
        id_key="wind_params_id",
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


def wind_bucket_id(*, tile_cell_key: Mapping[str, object], update_interval_ticks: int) -> int:
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


def wind_tick_bucket(*, current_tick: int, update_interval_ticks: int) -> int:
    interval = max(1, _as_int(update_interval_ticks, 1))
    tick = max(0, _as_int(current_tick, 0))
    return int(tick // interval)


def _climate_proxy_row(wind_params_row: Mapping[str, object]) -> dict:
    row = _as_map(wind_params_row)
    extensions = _as_map(row.get("extensions"))
    return {
        "year_length_ticks": int(max(1, _as_int(extensions.get("year_length_ticks", 3650), 3650))),
        "axial_tilt_deg": int(max(0, _as_int(extensions.get("axial_tilt_deg", 0), 0))),
        "extensions": {
            "epoch_offset_ticks": int(max(0, _as_int(extensions.get("epoch_offset_ticks", 0), 0))),
            "axial_tilt_mdeg": int(max(0, _as_int(extensions.get("axial_tilt_mdeg", 23_500), 23_500))),
        },
    }


def _season_boundary_shift_mdeg(*, wind_params_row: Mapping[str, object], current_tick: int) -> tuple[int, int, int]:
    climate_proxy = _climate_proxy_row(wind_params_row)
    orbit_phase = earth_orbit_phase_from_params(
        tick=int(max(0, _as_int(current_tick, 0))),
        climate_params_row=climate_proxy,
        phase_scale=EARTH_ORBIT_PHASE_SCALE,
    )
    tilt_mdeg = axial_tilt_mdeg(climate_proxy)
    declination_mdeg = solar_declination_mdeg(
        orbit_phase=orbit_phase,
        axial_tilt_mdeg=tilt_mdeg,
        phase_scale=EARTH_ORBIT_PHASE_SCALE,
    )
    amplitude = max(0, _as_int(_as_map(wind_params_row).get("seasonal_shift_amplitude", 0), 0))
    denominator = max(1, int(tilt_mdeg))
    shift_mdeg = int((int(declination_mdeg) * amplitude) // denominator)
    shift_mdeg = _clamp(shift_mdeg, -amplitude, amplitude)
    return int(orbit_phase), int(declination_mdeg), int(shift_mdeg)


def _latitude_band(*, latitude_mdeg: int, shift_mdeg: int, wind_params_row: Mapping[str, object]) -> tuple[str, int]:
    extensions = _as_map(_as_map(wind_params_row).get("extensions"))
    hadley_max = _clamp(_as_int(extensions.get("hadley_max_mdeg", 30_000), 30_000), 5_000, 45_000)
    ferrel_max = _clamp(_as_int(extensions.get("ferrel_max_mdeg", 60_000), 60_000), hadley_max + 1, 85_000)
    effective_latitude = abs(int(latitude_mdeg) - int(shift_mdeg))
    if effective_latitude <= hadley_max:
        return ("wind.band.hadley", int(effective_latitude))
    if effective_latitude <= ferrel_max:
        return ("wind.band.ferrel", int(effective_latitude))
    return ("wind.band.polar", int(effective_latitude))


def _signed_hash_noise(*, tile_cell_key: Mapping[str, object], tick_bucket: int, axis: str, magnitude: int) -> int:
    amplitude = max(0, _as_int(magnitude, 0))
    if amplitude <= 0:
        return 0
    digest = canonical_sha256(
        {
            "tile_cell_key": _semantic_cell_key(_coerce_cell_key(tile_cell_key) or {}),
            "tick_bucket": int(max(0, _as_int(tick_bucket, 0))),
            "axis": str(axis).strip() or "x",
        }
    )
    span = (amplitude * 2) + 1
    return int((int(digest[:8], 16) % span) - amplitude)


def _band_components(
    *,
    band_id: str,
    latitude_mdeg: int,
    wind_params_row: Mapping[str, object],
) -> tuple[int, int]:
    extensions = _as_map(_as_map(wind_params_row).get("extensions"))
    equatorward_sign = -1 if int(latitude_mdeg) > 0 else (1 if int(latitude_mdeg) < 0 else 0)
    poleward_sign = -equatorward_sign
    if str(band_id) == "wind.band.hadley":
        return (
            int(_as_int(extensions.get("hadley_zonal_permille", -900), -900)),
            int(equatorward_sign * _as_int(extensions.get("hadley_meridional_permille", 220), 220)),
        )
    if str(band_id) == "wind.band.ferrel":
        return (
            int(_as_int(extensions.get("ferrel_zonal_permille", 920), 920)),
            int(poleward_sign * _as_int(extensions.get("ferrel_meridional_permille", 180), 180)),
        )
    return (
        int(_as_int(extensions.get("polar_zonal_permille", -700), -700)),
        int(equatorward_sign * _as_int(extensions.get("polar_meridional_permille", 140), 140)),
    )


def _band_speed(band_id: str, wind_params_row: Mapping[str, object]) -> int:
    speeds = _as_map(_as_map(wind_params_row).get("base_speed_by_band"))
    default_speed = 300
    if str(band_id) == "wind.band.ferrel":
        default_speed = 420
    elif str(band_id) == "wind.band.polar":
        default_speed = 240
    return int(max(0, _as_int(speeds.get(str(band_id), default_speed), default_speed)))


def build_poll_advection_stub(*, wind_evaluation: Mapping[str, object]) -> dict:
    row = _as_map(wind_evaluation)
    vector = _as_map(row.get("wind_vector"))
    magnitude = int(max(abs(_as_int(vector.get("x", 0), 0)), abs(_as_int(vector.get("y", 0), 0))))
    return {
        "future.poll.advection_bias": {
            "hook_kind": "field_proxy",
            "field_type_id": "field.wind_vector",
            "enabled": magnitude > 0,
            "vector": {
                "x": int(_as_int(vector.get("x", 0), 0)),
                "y": int(_as_int(vector.get("y", 0), 0)),
                "z": int(_as_int(vector.get("z", 0), 0)),
            },
        },
        "future.sky.cloud_drift_bias": {
            "hook_kind": "vector_proxy",
            "field_type_id": "field.wind_vector",
            "enabled": magnitude > 0,
            "speed_proxy": int(magnitude),
        },
        "future.sound.wind_attenuation_bias": {
            "hook_kind": "vector_proxy",
            "field_type_id": "field.wind_vector",
            "enabled": magnitude > 0,
            "speed_proxy": int(magnitude),
        },
    }


def evaluate_earth_tile_wind(
    *,
    artifact_row: Mapping[str, object],
    wind_params_row: Mapping[str, object],
    current_tick: int,
) -> dict:
    row = _as_map(artifact_row)
    wind_row = _as_map(wind_params_row)
    extensions = _as_map(row.get("extensions"))
    tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
    latitude_mdeg = _as_int(extensions.get("latitude_mdeg", 0), 0)
    longitude_mdeg = _as_int(extensions.get("longitude_mdeg", 0), 0)
    update_interval = max(1, _as_int(wind_row.get("update_interval_ticks", 1), 1))
    tick = max(0, _as_int(current_tick, 0))
    tick_bucket = wind_tick_bucket(current_tick=tick, update_interval_ticks=update_interval)
    orbit_phase, declination_mdeg, shift_mdeg = _season_boundary_shift_mdeg(
        wind_params_row=wind_row,
        current_tick=tick,
    )
    band_id, effective_latitude = _latitude_band(
        latitude_mdeg=latitude_mdeg,
        shift_mdeg=shift_mdeg,
        wind_params_row=wind_row,
    )
    zonal_permille, meridional_permille = _band_components(
        band_id=band_id,
        latitude_mdeg=latitude_mdeg,
        wind_params_row=wind_row,
    )
    speed_value = _band_speed(band_id, wind_row)
    noise_policy_id = str(wind_row.get("noise_policy_id", "")).strip() or "noise.none"
    noise_magnitude = max(0, _as_int(wind_row.get("noise_magnitude", 0), 0))
    noise_x = 0
    noise_y = 0
    if noise_policy_id == "noise.hash_tile_bucket" and noise_magnitude > 0:
        noise_x = _signed_hash_noise(tile_cell_key=tile_cell_key, tick_bucket=tick_bucket, axis="x", magnitude=noise_magnitude)
        noise_y = _signed_hash_noise(tile_cell_key=tile_cell_key, tick_bucket=tick_bucket, axis="y", magnitude=noise_magnitude)
    wind_vector = {
        "x": int((speed_value * zonal_permille) // 1000) + int(noise_x),
        "y": int((speed_value * meridional_permille) // 1000) + int(noise_y),
        "z": 0,
    }
    payload = {
        "tile_object_id": str(row.get("tile_object_id", "")).strip(),
        "planet_object_id": str(row.get("planet_object_id", "")).strip(),
        "tile_cell_key": dict(tile_cell_key),
        "cell_id": _legacy_cell_alias_from_tile_key(tile_cell_key),
        "current_tick": int(tick),
        "tick_bucket": int(tick_bucket),
        "orbit_phase": int(orbit_phase),
        "declination_mdeg": int(declination_mdeg),
        "band_shift_mdeg": int(shift_mdeg),
        "latitude_mdeg": int(latitude_mdeg),
        "longitude_mdeg": int(longitude_mdeg),
        "effective_latitude_mdeg": int(effective_latitude),
        "wind_band_id": str(band_id),
        "base_speed_value": int(speed_value),
        "noise_policy_id": noise_policy_id,
        "wind_vector": dict(wind_vector),
        "coupling_hooks": build_poll_advection_stub(
            wind_evaluation={
                "wind_vector": dict(wind_vector),
            }
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_wind_field_updates(
    *,
    wind_row: Mapping[str, object],
    wind_evaluations: Sequence[Mapping[str, object]],
) -> List[dict]:
    evaluations = [dict(row) for row in list(wind_evaluations or []) if isinstance(row, Mapping)]
    if not evaluations:
        return []
    planet_id = str(evaluations[0].get("planet_object_id", "")).strip()
    wind_params_id = str(_as_map(wind_row).get("wind_params_id", "")).strip() or DEFAULT_WIND_PARAMS_ID
    field_updates: List[dict] = []
    for row in evaluations:
        cell_id = str(row.get("cell_id", "")).strip()
        geo_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not cell_id:
            continue
        field_updates.append(
            {
                "field_id": "field.wind_vector.surface.{}".format(planet_id),
                "field_type_id": "field.wind_vector",
                "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                "resolution_level": "macro",
                "cell_id": cell_id,
                "geo_cell_key": dict(geo_cell_key),
                "value": {
                    "x": int(_as_int(_as_map(row.get("wind_vector")).get("x", 0), 0)),
                    "y": int(_as_int(_as_map(row.get("wind_vector")).get("y", 0), 0)),
                    "z": int(_as_int(_as_map(row.get("wind_vector")).get("z", 0), 0)),
                },
                "extensions": {
                    "wind_params_id": wind_params_id,
                    "wind_band_id": str(row.get("wind_band_id", "")).strip(),
                    "source": EARTH_WIND_ENGINE_VERSION,
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


def build_earth_wind_update_plan(
    *,
    artifact_rows: object,
    wind_params_row: Mapping[str, object],
    current_tick: int,
    last_processed_tick: int | None,
    max_tiles_per_update: int,
) -> dict:
    wind_row = _as_map(wind_params_row)
    interval = max(1, _as_int(wind_row.get("update_interval_ticks", 1), 1))
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
        bucket_id = wind_bucket_id(tile_cell_key=tile_cell_key, update_interval_ticks=interval)
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
        evaluate_earth_tile_wind(
            artifact_row=dict(row.get("artifact_row") or {}),
            wind_params_row=wind_row,
            current_tick=int(current_tick),
        )
        for row in selected
    ]
    field_updates = build_wind_field_updates(
        wind_row=wind_row,
        wind_evaluations=evaluations,
    )
    result = {
        "wind_params_id": str(wind_row.get("wind_params_id", "")).strip() or DEFAULT_WIND_PARAMS_ID,
        "due_bucket_ids": [int(item) for item in list(bucket_ids or [])],
        "selected_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in selected if str(row.get("tile_object_id", "")).strip()],
        "skipped_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in skipped if str(row.get("tile_object_id", "")).strip()],
        "evaluations": [dict(row) for row in evaluations],
        "field_updates": [dict(row) for row in field_updates],
        "cost_units_used": int(len(selected)),
        "degraded": bool(len(skipped) > 0),
        "degrade_reason": "degrade.earth_wind.budget" if skipped else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def wind_window_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for row in list(rows or []):
        payload = _as_map(row)
        vector = _as_map(payload.get("wind_vector"))
        normalized.append(
            {
                "tile_object_id": str(payload.get("tile_object_id", "")).strip(),
                "wind_band_id": str(payload.get("wind_band_id", "")).strip(),
                "wind_vector": {
                    "x": int(_as_int(vector.get("x", 0), 0)),
                    "y": int(_as_int(vector.get("y", 0), 0)),
                    "z": int(_as_int(vector.get("z", 0), 0)),
                },
                "tick_bucket": int(_as_int(payload.get("tick_bucket", 0), 0)),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


__all__ = [
    "DEFAULT_WIND_PARAMS_ID",
    "EARTH_WIND_ENGINE_VERSION",
    "WIND_PARAMS_REGISTRY_REL",
    "build_earth_wind_update_plan",
    "build_poll_advection_stub",
    "build_wind_field_updates",
    "due_bucket_ids",
    "evaluate_earth_tile_wind",
    "wind_bucket_id",
    "wind_params_rows",
    "wind_tick_bucket",
    "wind_window_hash",
]
