"""Deterministic EARTH-2 orbit-phase and seasonal proxy helpers."""

from __future__ import annotations

from typing import Mapping


EARTH_SEASON_PHASE_ENGINE_VERSION = "EARTH2-3"
EARTH_ORBIT_PHASE_SCALE = 1_000_000


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def earth_orbit_phase(
    *,
    tick: int,
    year_length_ticks: int,
    epoch_offset_ticks: int = 0,
    phase_scale: int = EARTH_ORBIT_PHASE_SCALE,
) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_ORBIT_PHASE_SCALE))
    year_length = max(1, _as_int(year_length_ticks, 1))
    canonical_tick = max(0, _as_int(tick, 0))
    offset = max(0, _as_int(epoch_offset_ticks, 0))
    shifted = canonical_tick + offset
    return (shifted % year_length) * scale // year_length


def earth_orbit_phase_from_params(
    *,
    tick: int,
    climate_params_row: Mapping[str, object] | None,
    phase_scale: int = EARTH_ORBIT_PHASE_SCALE,
) -> int:
    row = _as_map(climate_params_row)
    extensions = _as_map(row.get("extensions"))
    return earth_orbit_phase(
        tick=tick,
        year_length_ticks=_as_int(row.get("year_length_ticks", 1), 1),
        epoch_offset_ticks=_as_int(extensions.get("epoch_offset_ticks", 0), 0),
        phase_scale=phase_scale,
    )


def seasonal_wave_permille(
    *,
    orbit_phase: int,
    phase_scale: int = EARTH_ORBIT_PHASE_SCALE,
) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_ORBIT_PHASE_SCALE))
    phase = _clamp(_as_int(orbit_phase, 0), 0, scale - 1)
    quarter = max(1, scale // 4)
    half = max(1, scale // 2)
    three_quarter = max(1, (3 * scale) // 4)
    if phase < quarter:
        return _clamp((phase * 1000) // quarter, -1000, 1000)
    if phase < three_quarter:
        return _clamp(1000 - (((phase - quarter) * 2000) // half), -1000, 1000)
    tail = max(1, scale - three_quarter)
    return _clamp(-1000 + (((phase - three_quarter) * 1000) // tail), -1000, 1000)


def axial_tilt_mdeg(climate_params_row: Mapping[str, object] | None) -> int:
    row = _as_map(climate_params_row)
    extensions = _as_map(row.get("extensions"))
    explicit_mdeg = _as_int(extensions.get("axial_tilt_mdeg", 0), 0)
    if explicit_mdeg > 0:
        return explicit_mdeg
    return max(0, _as_int(row.get("axial_tilt_deg", 0), 0) * 1000)


def solar_declination_mdeg(
    *,
    orbit_phase: int,
    axial_tilt_mdeg: int,
    phase_scale: int = EARTH_ORBIT_PHASE_SCALE,
) -> int:
    return (_as_int(axial_tilt_mdeg, 0) * seasonal_wave_permille(orbit_phase=orbit_phase, phase_scale=phase_scale)) // 1000


__all__ = [
    "EARTH_ORBIT_PHASE_SCALE",
    "EARTH_SEASON_PHASE_ENGINE_VERSION",
    "axial_tilt_mdeg",
    "earth_orbit_phase",
    "earth_orbit_phase_from_params",
    "seasonal_wave_permille",
    "solar_declination_mdeg",
]
