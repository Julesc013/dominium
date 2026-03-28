"""Deterministic EMB-2 friction tuning helpers."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def resolve_horizontal_damping_state(
    *,
    base_damping_permille: int,
    slope_response: Mapping[str, object] | None = None,
    friction_field_value: object = None,
    source_kind: str = "",
) -> dict:
    slope = _as_map(slope_response)
    base = _clamp(_as_int(base_damping_permille, 120), 0, 950)
    friction_permille = _clamp(_as_int(friction_field_value, 1000), 100, 1200)
    slope_angle_mdeg = max(0, _as_int(slope.get("slope_angle_mdeg", 0), 0))
    direction_class = str(slope.get("direction_class", "flat")).strip() or "flat"

    if direction_class == "uphill" and slope_angle_mdeg > 0:
        slope_adjust_permille = _clamp(1000 + ((min(45_000, slope_angle_mdeg) * 180) // 45_000), 1000, 1180)
    elif direction_class == "downhill" and slope_angle_mdeg > 0:
        slope_adjust_permille = _clamp(1000 - ((min(45_000, slope_angle_mdeg) * 220) // 45_000), 780, 1000)
    else:
        slope_adjust_permille = 1000

    effective = _clamp((int(base) * int(friction_permille) * int(slope_adjust_permille)) // 1_000_000, 0, 950)
    payload = {
        "effective_damping_permille": int(effective),
        "base_damping_permille": int(base),
        "friction_permille": int(friction_permille),
        "slope_adjust_permille": int(slope_adjust_permille),
        "direction_class": direction_class,
        "source_kind": str(source_kind).strip() or ("field.friction" if friction_field_value is not None else "default"),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
