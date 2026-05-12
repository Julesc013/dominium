"""Deterministic MW-3 insolation and season proxy helpers."""

from __future__ import annotations

from typing import Mapping


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def orbital_period_proxy_ticks(*, semi_major_axis_milli_au: int, star_mass_milli_solar: int) -> int:
    axis = max(80, _as_int(semi_major_axis_milli_au, 1000))
    mass = max(80, _as_int(star_mass_milli_solar, 1000))
    # Coarse integer-only Kepler-like proxy suitable for seasonal phase bucketing.
    period = max(64, (axis * axis) // mass)
    return min(2_000_000, max(64, period))


def season_phase_permille(*, current_tick: int, orbital_period_ticks: int) -> int:
    period = max(1, _as_int(orbital_period_ticks, 1))
    tick = max(0, _as_int(current_tick, 0))
    return (tick % period) * 1000 // period


def _triangle_wave_permille(phase_permille: int) -> int:
    phase = max(0, min(999, _as_int(phase_permille, 0)))
    if phase < 250:
        return phase * 4
    if phase < 750:
        return 2000 - (phase * 4)
    return (phase * 4) - 4000


def daylight_proxy_permille(
    *,
    latitude_mdeg: int,
    axial_tilt_mdeg: int,
    current_tick: int,
    orbital_period_ticks: int,
    daylight_params: Mapping[str, object] | None = None,
) -> int:
    params = _as_map(daylight_params)
    equatorial = max(100, _as_int(params.get("equatorial_daylight_permille", 1000), 1000))
    polar_floor = max(0, min(equatorial, _as_int(params.get("polar_floor_permille", 0), 0)))
    tilt_weight = max(0, _as_int(params.get("seasonal_tilt_weight_permille", 1000), 1000))
    phase = season_phase_permille(current_tick=current_tick, orbital_period_ticks=orbital_period_ticks)
    seasonal_wave = _triangle_wave_permille(phase)
    declination_mdeg = (_as_int(axial_tilt_mdeg, 0) * seasonal_wave * tilt_weight) // 1_000_000
    solar_distance = abs(_as_int(latitude_mdeg, 0) - declination_mdeg)
    attenuation = _clamp((solar_distance * equatorial) // 90_000, 0, equatorial)
    return _clamp(equatorial - attenuation, polar_floor, equatorial)


def insolation_proxy_permille(
    *,
    daylight_permille: int,
    luminosity_permille: int,
    semi_major_axis_milli_au: int,
) -> int:
    daylight = _clamp(_as_int(daylight_permille, 0), 0, 1000)
    luminosity = max(1, _as_int(luminosity_permille, 1))
    axis = max(250, _as_int(semi_major_axis_milli_au, 1000))
    stellar_term = (luminosity * 1000) // axis
    return _clamp((stellar_term * daylight) // 1000, 0, 4000)


__all__ = [
    "daylight_proxy_permille",
    "insolation_proxy_permille",
    "orbital_period_proxy_ticks",
    "season_phase_permille",
]
