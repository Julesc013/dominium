"""Deterministic EARTH-3 lunar and rotational tide phase helpers."""

from __future__ import annotations

from typing import Mapping


EARTH_TIDE_PHASE_ENGINE_VERSION = "EARTH3-3"
EARTH_TIDE_PHASE_SCALE = 1_000_000


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _phase_from_ticks(
    *,
    tick: int,
    period_ticks: int,
    epoch_offset_ticks: int = 0,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    period = max(1, _as_int(period_ticks, 1))
    canonical_tick = max(0, _as_int(tick, 0))
    offset = max(0, _as_int(epoch_offset_ticks, 0))
    shifted = canonical_tick + offset
    return (shifted % period) * scale // period


def lunar_phase(
    *,
    tick: int,
    lunar_period_ticks: int,
    epoch_offset_ticks: int = 0,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    return _phase_from_ticks(
        tick=tick,
        period_ticks=lunar_period_ticks,
        epoch_offset_ticks=epoch_offset_ticks,
        phase_scale=phase_scale,
    )


def rotation_phase(
    *,
    tick: int,
    day_length_ticks: int,
    epoch_offset_ticks: int = 0,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    return _phase_from_ticks(
        tick=tick,
        period_ticks=day_length_ticks,
        epoch_offset_ticks=epoch_offset_ticks,
        phase_scale=phase_scale,
    )


def lunar_phase_from_params(
    *,
    tick: int,
    tide_params_row: Mapping[str, object] | None,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    row = _as_map(tide_params_row)
    extensions = _as_map(row.get("extensions"))
    return lunar_phase(
        tick=tick,
        lunar_period_ticks=_as_int(extensions.get("lunar_period_ticks", 273), 273),
        epoch_offset_ticks=_as_int(extensions.get("epoch_offset_ticks", 0), 0),
        phase_scale=phase_scale,
    )


def rotation_phase_from_params(
    *,
    tick: int,
    tide_params_row: Mapping[str, object] | None,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    row = _as_map(tide_params_row)
    extensions = _as_map(row.get("extensions"))
    return rotation_phase(
        tick=tick,
        day_length_ticks=_as_int(extensions.get("day_length_ticks", 10), 10),
        epoch_offset_ticks=_as_int(extensions.get("rotation_epoch_offset_ticks", 0), 0),
        phase_scale=phase_scale,
    )


def phase_cosine_proxy_permille(
    *,
    phase: int,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    token = _clamp(_as_int(phase, 0), 0, scale - 1)
    quarter = max(1, scale // 4)
    half = max(1, scale // 2)
    three_quarter = max(1, (3 * scale) // 4)
    if token < quarter:
        return _clamp(1000 - ((token * 1000) // quarter), -1000, 1000)
    if token < half:
        return _clamp(-((token - quarter) * 1000) // max(1, half - quarter), -1000, 1000)
    if token < three_quarter:
        return _clamp(-1000 + (((token - half) * 1000) // max(1, three_quarter - half)), -1000, 1000)
    return _clamp(((token - three_quarter) * 1000) // max(1, scale - three_quarter), -1000, 1000)


def phase_carrier_permille(
    *,
    rotation_phase_value: int,
    lunar_phase_value: int,
    phase_scale: int = EARTH_TIDE_PHASE_SCALE,
) -> int:
    scale = max(1000, _as_int(phase_scale, EARTH_TIDE_PHASE_SCALE))
    delta = (_as_int(rotation_phase_value, 0) - _as_int(lunar_phase_value, 0)) % scale
    semidiurnal_phase = (delta * 2) % scale
    return phase_cosine_proxy_permille(phase=semidiurnal_phase, phase_scale=scale)


__all__ = [
    "EARTH_TIDE_PHASE_ENGINE_VERSION",
    "EARTH_TIDE_PHASE_SCALE",
    "lunar_phase",
    "lunar_phase_from_params",
    "phase_carrier_permille",
    "phase_cosine_proxy_permille",
    "rotation_phase",
    "rotation_phase_from_params",
]
