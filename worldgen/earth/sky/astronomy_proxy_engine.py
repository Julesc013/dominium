"""Deterministic EARTH-4 astronomy proxy helpers."""

from __future__ import annotations

from typing import Mapping

from worldgen.earth.season_phase_engine import (
    EARTH_ORBIT_PHASE_SCALE,
    axial_tilt_mdeg,
    earth_orbit_phase_from_params,
    seasonal_wave_permille,
    solar_declination_mdeg,
)
from worldgen.earth.tide_phase_engine import (
    EARTH_TIDE_PHASE_SCALE,
    lunar_phase_from_params,
    phase_cosine_proxy_permille,
    rotation_phase_from_params,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


EARTH_SKY_ASTRONOMY_ENGINE_VERSION = "EARTH4-3"
SKY_DIRECTION_SCALE = 1000


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _phase_wrap(phase_value: int, *, phase_scale: int) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    return _as_int(phase_value, 0) % scale


def _phase_shift(phase_value: int, *, delta: int, phase_scale: int) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    return (_as_int(phase_value, 0) + _as_int(delta, 0)) % scale


def _longitude_phase_offset(longitude_mdeg: int, *, phase_scale: int) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    wrapped = ((_as_int(longitude_mdeg, 0) + 180_000) % 360_000) - 180_000
    return (wrapped * scale) // 360_000


def local_phase_from_longitude_mdeg(*, phase_value: int, longitude_mdeg: int, phase_scale: int = EARTH_TIDE_PHASE_SCALE) -> int:
    return _phase_wrap(
        _as_int(phase_value, 0) + _longitude_phase_offset(longitude_mdeg, phase_scale=phase_scale),
        phase_scale=phase_scale,
    )


def _normalized_direction(*, east_permille: int, north_permille: int, up_permille: int) -> dict:
    east = _clamp(_as_int(east_permille, 0), -SKY_DIRECTION_SCALE, SKY_DIRECTION_SCALE)
    north = _clamp(_as_int(north_permille, 0), -SKY_DIRECTION_SCALE, SKY_DIRECTION_SCALE)
    up = _clamp(_as_int(up_permille, 0), -SKY_DIRECTION_SCALE, SKY_DIRECTION_SCALE)
    total = max(1, abs(east) + abs(north) + abs(up))
    return {
        "x": int((east * SKY_DIRECTION_SCALE) // total),
        "y": int((north * SKY_DIRECTION_SCALE) // total),
        "z": int((up * SKY_DIRECTION_SCALE) // total),
        "scale": SKY_DIRECTION_SCALE,
    }


def _altitude_from_declination(
    *,
    latitude_mdeg: int,
    declination_mdeg: int,
    local_phase: int,
    phase_scale: int,
) -> tuple[int, int]:
    phase = _phase_wrap(local_phase, phase_scale=phase_scale)
    day_carrier = phase_cosine_proxy_permille(phase=phase, phase_scale=phase_scale)
    midday_altitude_mdeg = _clamp(90_000 - abs(_as_int(latitude_mdeg, 0) - _as_int(declination_mdeg, 0)), -90_000, 90_000)
    altitude_mdeg = _clamp((midday_altitude_mdeg * day_carrier) // 1000, -90_000, 90_000)
    return int(day_carrier), int(altitude_mdeg)


def _direction_payload(
    *,
    latitude_mdeg: int,
    declination_mdeg: int,
    local_phase: int,
    altitude_mdeg: int,
    phase_scale: int,
) -> dict:
    phase = _phase_wrap(local_phase, phase_scale=phase_scale)
    east_carrier = phase_cosine_proxy_permille(
        phase=_phase_shift(phase, delta=phase_scale // 4, phase_scale=phase_scale),
        phase_scale=phase_scale,
    )
    up_permille = _clamp((_as_int(altitude_mdeg, 0) * SKY_DIRECTION_SCALE) // 90_000, -SKY_DIRECTION_SCALE, SKY_DIRECTION_SCALE)
    horizon_scale = max(0, SKY_DIRECTION_SCALE - abs(up_permille))
    north_bias = _clamp(
        ((_as_int(declination_mdeg, 0) - _as_int(latitude_mdeg, 0)) * horizon_scale) // 90_000,
        -SKY_DIRECTION_SCALE,
        SKY_DIRECTION_SCALE,
    )
    east_bias = _clamp((east_carrier * horizon_scale) // 1000, -SKY_DIRECTION_SCALE, SKY_DIRECTION_SCALE)
    azimuth_mdeg = int((_phase_wrap(phase, phase_scale=phase_scale) * 360_000) // max(1, phase_scale))
    return {
        "local_phase": int(phase),
        "azimuth_mdeg": int(azimuth_mdeg),
        "altitude_mdeg": int(_as_int(altitude_mdeg, 0)),
        "direction": _normalized_direction(
            east_permille=east_bias,
            north_permille=north_bias,
            up_permille=up_permille,
        ),
    }


def sun_direction_proxy(
    *,
    latitude_mdeg: int,
    longitude_mdeg: int,
    current_tick: int,
    climate_params_row: Mapping[str, object] | None,
    tide_params_row: Mapping[str, object] | None,
) -> dict:
    climate_row = _as_map(climate_params_row)
    tide_row = _as_map(tide_params_row)
    tick = max(0, _as_int(current_tick, 0))
    orbit_phase = earth_orbit_phase_from_params(
        tick=tick,
        climate_params_row=climate_row,
        phase_scale=EARTH_ORBIT_PHASE_SCALE,
    )
    declination_mdeg = solar_declination_mdeg(
        orbit_phase=orbit_phase,
        axial_tilt_mdeg=axial_tilt_mdeg(climate_row),
        phase_scale=EARTH_ORBIT_PHASE_SCALE,
    )
    rotation_phase = rotation_phase_from_params(
        tick=tick,
        tide_params_row=tide_row,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    local_phase = local_phase_from_longitude_mdeg(
        phase_value=rotation_phase,
        longitude_mdeg=longitude_mdeg,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    day_carrier, altitude_mdeg = _altitude_from_declination(
        latitude_mdeg=latitude_mdeg,
        declination_mdeg=declination_mdeg,
        local_phase=local_phase,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    direction_payload = _direction_payload(
        latitude_mdeg=latitude_mdeg,
        declination_mdeg=declination_mdeg,
        local_phase=local_phase,
        altitude_mdeg=altitude_mdeg,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    payload = {
        "tick": int(tick),
        "orbit_phase": int(orbit_phase),
        "rotation_phase": int(rotation_phase),
        "declination_mdeg": int(declination_mdeg),
        "day_carrier_permille": int(day_carrier),
        "sun_elevation_mdeg": int(altitude_mdeg),
        "sun_direction": dict(direction_payload.get("direction") or {}),
        "sun_azimuth_mdeg": int(direction_payload.get("azimuth_mdeg", 0)),
        "local_phase": int(direction_payload.get("local_phase", 0)),
        "deterministic_fingerprint": "",
        "extensions": {
            "engine_version": EARTH_SKY_ASTRONOMY_ENGINE_VERSION,
            "latitude_mdeg": int(_as_int(latitude_mdeg, 0)),
            "longitude_mdeg": int(_as_int(longitude_mdeg, 0)),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def moon_direction_proxy(
    *,
    latitude_mdeg: int,
    longitude_mdeg: int,
    current_tick: int,
    climate_params_row: Mapping[str, object] | None,
    tide_params_row: Mapping[str, object] | None,
) -> dict:
    climate_row = _as_map(climate_params_row)
    tide_row = _as_map(tide_params_row)
    tide_ext = _as_map(tide_row.get("extensions"))
    tick = max(0, _as_int(current_tick, 0))
    lunar_phase_value = lunar_phase_from_params(
        tick=tick,
        tide_params_row=tide_row,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    rotation_phase = rotation_phase_from_params(
        tick=tick,
        tide_params_row=tide_row,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    local_phase = local_phase_from_longitude_mdeg(
        phase_value=rotation_phase - lunar_phase_value,
        longitude_mdeg=longitude_mdeg,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    inclination_mdeg = max(1000, _as_int(tide_ext.get("lunar_inclination_mdeg", 5200), 5200))
    declination_wave = seasonal_wave_permille(
        orbit_phase=lunar_phase_value,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    lunar_declination_mdeg = (inclination_mdeg * declination_wave) // 1000
    carrier_permille, altitude_mdeg = _altitude_from_declination(
        latitude_mdeg=latitude_mdeg,
        declination_mdeg=lunar_declination_mdeg,
        local_phase=local_phase,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    direction_payload = _direction_payload(
        latitude_mdeg=latitude_mdeg,
        declination_mdeg=lunar_declination_mdeg,
        local_phase=local_phase,
        altitude_mdeg=altitude_mdeg,
        phase_scale=EARTH_TIDE_PHASE_SCALE,
    )
    payload = {
        "tick": int(tick),
        "rotation_phase": int(rotation_phase),
        "declination_mdeg": int(lunar_declination_mdeg),
        "carrier_permille": int(carrier_permille),
        "moon_elevation_mdeg": int(altitude_mdeg),
        "moon_direction": dict(direction_payload.get("direction") or {}),
        "moon_azimuth_mdeg": int(direction_payload.get("azimuth_mdeg", 0)),
        "local_phase": int(direction_payload.get("local_phase", 0)),
        "deterministic_fingerprint": "",
        "extensions": {
            "engine_version": EARTH_SKY_ASTRONOMY_ENGINE_VERSION,
            "latitude_mdeg": int(_as_int(latitude_mdeg, 0)),
            "longitude_mdeg": int(_as_int(longitude_mdeg, 0)),
            "axial_tilt_mdeg": int(axial_tilt_mdeg(climate_row)),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
