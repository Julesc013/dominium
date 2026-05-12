"""Deterministic EARTH-4 sky gradient model."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


SKY_GRADIENT_MODEL_VERSION = "EARTH4-4"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _mix_channel(a: int, b: int, factor_permille: int) -> int:
    factor = _clamp(_as_int(factor_permille, 0), 0, 1000)
    return _clamp(((_as_int(a, 0) * (1000 - factor)) + (_as_int(b, 0) * factor)) // 1000, 0, 255)


def _mix_color(a: Mapping[str, object], b: Mapping[str, object], factor_permille: int) -> dict:
    color_a = _as_map(a)
    color_b = _as_map(b)
    return {
        "r": _mix_channel(color_a.get("r", 0), color_b.get("r", 0), factor_permille),
        "g": _mix_channel(color_a.get("g", 0), color_b.get("g", 0), factor_permille),
        "b": _mix_channel(color_a.get("b", 0), color_b.get("b", 0), factor_permille),
    }


def evaluate_sky_gradient(
    *,
    sun_elevation_mdeg: int,
    sky_model_row: Mapping[str, object] | None,
    moon_illumination_permille: int = 0,
) -> dict:
    row = _as_map(sky_model_row)
    ext = _as_map(row.get("extensions"))
    turbidity = _clamp(_as_int(ext.get("turbidity_permille", 460), 460), 0, 1000)
    twilight_top = _as_int(ext.get("twilight_top_mdeg", 6000), 6000)
    twilight_bottom = _as_int(ext.get("twilight_bottom_mdeg", -18000), -18000)
    elevation = _clamp(_as_int(sun_elevation_mdeg, 0), -90_000, 90_000)

    day_zenith = {"r": 50, "g": 122, "b": _clamp(222 - (turbidity // 10), 80, 240)}
    day_horizon = {"r": 160, "g": 206, "b": 255}
    twilight_zenith = {"r": 74, "g": 66, "b": 118}
    twilight_horizon = {"r": 255, "g": 132, "b": 72}
    night_zenith = {"r": 8, "g": 18, "b": 42}
    night_horizon = {"r": 18, "g": 24, "b": 42}
    day_sun = {"r": 255, "g": 242, "b": 222}
    twilight_sun = {"r": 255, "g": 162, "b": 92}
    night_sun = {"r": 0, "g": 0, "b": 0}

    if elevation >= twilight_top:
        twilight_factor = 0
        day_factor = 1000
        night_factor = 0
        sun_intensity = _clamp(720 + ((elevation - twilight_top) * 280) // max(1, 90_000 - twilight_top), 720, 1000)
    elif elevation > twilight_bottom:
        twilight_factor = _clamp(((twilight_top - elevation) * 1000) // max(1, twilight_top - twilight_bottom), 0, 1000)
        day_factor = 1000 - twilight_factor
        night_factor = 0
        sun_intensity = _clamp(120 + (((elevation - twilight_bottom) * 580) // max(1, twilight_top - twilight_bottom)), 120, 700)
    else:
        twilight_factor = 0
        day_factor = 0
        night_factor = _clamp(1000 + ((elevation - twilight_bottom) * 1000) // 18_000, 0, 1000)
        sun_intensity = 0

    if day_factor > 0:
        zenith = _mix_color(twilight_zenith, day_zenith, day_factor)
        horizon = _mix_color(twilight_horizon, day_horizon, day_factor)
        sun_color = _mix_color(twilight_sun, day_sun, day_factor)
    elif night_factor > 0:
        zenith = _mix_color(night_zenith, twilight_zenith, night_factor)
        horizon = _mix_color(night_horizon, twilight_horizon, night_factor // 2)
        sun_color = dict(night_sun)
    else:
        zenith = _mix_color(day_zenith, twilight_zenith, twilight_factor)
        horizon = _mix_color(day_horizon, twilight_horizon, twilight_factor)
        sun_color = _mix_color(day_sun, twilight_sun, twilight_factor)

    moon_glow = _clamp((_as_int(moon_illumination_permille, 0) * max(0, 1000 - sun_intensity)) // 1000, 0, 1000)
    if moon_glow > 0:
        zenith = _mix_color(zenith, {"r": 18, "g": 24, "b": 56}, moon_glow // 6)
        horizon = _mix_color(horizon, {"r": 34, "g": 40, "b": 72}, moon_glow // 8)

    payload = {
        "sky_model_id": str(row.get("sky_model_id", "")).strip() or "sky.gradient_stub_default",
        "sun_elevation_mdeg": int(elevation),
        "turbidity_permille": int(turbidity),
        "zenith_color": zenith,
        "horizon_color": horizon,
        "sun_color": sun_color,
        "sun_intensity_permille": int(sun_intensity),
        "twilight_factor_permille": int(twilight_factor),
        "moon_glow_permille": int(moon_glow),
        "deterministic_fingerprint": "",
        "extensions": {
            "model_version": SKY_GRADIENT_MODEL_VERSION,
            "twilight_top_mdeg": int(twilight_top),
            "twilight_bottom_mdeg": int(twilight_bottom),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
