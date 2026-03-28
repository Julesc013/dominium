"""Deterministic EARTH-5 bounded horizon shadow helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_SHADOW_MODEL_ID = "shadow.horizon_stub_default"
SHADOW_MODEL_REGISTRY_REL = os.path.join("data", "registries", "shadow_model_registry.json")
EARTH_HORIZON_SHADOW_ENGINE_VERSION = "EARTH5-4"


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
            return os.path.normpath(os.path.join(here, "..", "..", "..", ".."))
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


def shadow_model_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(SHADOW_MODEL_REGISTRY_REL),
        row_key="shadow_models",
        id_key="shadow_model_id",
    )


def shadow_model_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(SHADOW_MODEL_REGISTRY_REL))


def _sign(value: int) -> int:
    token = _as_int(value, 0)
    if token < 0:
        return -1
    if token > 0:
        return 1
    return 0


def _surface_height_inputs(observer_surface_artifact: Mapping[str, object] | None) -> tuple[int, int, int, int, int]:
    artifact = _as_map(observer_surface_artifact)
    elevation = _as_map(artifact.get("elevation_params_ref"))
    return (
        max(0, _as_int(elevation.get("height_proxy", 0), 0)),
        _clamp(_as_int(elevation.get("macro_relief_permille", 0), 0), 0, 1000),
        _clamp(_as_int(elevation.get("ridge_bias_permille", 0), 0), 0, 1000),
        _clamp(_as_int(elevation.get("coastal_bias_permille", 0), 0), 0, 1000),
        _clamp(_as_int(elevation.get("continent_mask_permille", 0), 0), 0, 1000),
    )


def _sample_trace(
    *,
    base_height: int,
    macro_relief_permille: int,
    ridge_bias_permille: int,
    coastal_bias_permille: int,
    continent_mask_permille: int,
    sun_dir: Mapping[str, object] | None,
    shadow_model_row: Mapping[str, object] | None,
) -> list[dict]:
    direction = _as_map(sun_dir)
    row_ext = _as_map(_as_map(shadow_model_row).get("extensions"))
    horizontal_x = _clamp(_as_int(direction.get("x", 0), 0), -1000, 1000)
    horizontal_y = _clamp(_as_int(direction.get("y", 0), 0), -1000, 1000)
    horizontal_strength = max(1, abs(horizontal_x) + abs(horizontal_y))
    directional_alignment = max(abs(horizontal_x), abs(horizontal_y))
    sample_count = max(0, _as_int(row_ext.get("sample_count", 8), 8))
    step_distance_cells = max(1, _as_int(row_ext.get("step_distance_cells", 1), 1))
    sample_height_gain_units = max(0, _as_int(row_ext.get("sample_height_gain_units", 280), 280))
    horizon_bias_mdeg = max(0, _as_int(row_ext.get("horizon_bias_mdeg", 900), 900))
    max_occlusion_mdeg = max(1000, _as_int(row_ext.get("max_occlusion_mdeg", 24_000), 24_000))
    azimuth_sector = "{}{}".format(
        "n" if _sign(horizontal_y) >= 0 else "s",
        "e" if _sign(horizontal_x) >= 0 else "w",
    )
    rows: list[dict] = []
    for sample_index in range(1, sample_count + 1):
        distance_cells = sample_index * step_distance_cells
        distance_units = max(1, distance_cells * 18_000)
        relief_gain = (macro_relief_permille * sample_height_gain_units * distance_cells) // 1_000_000
        ridge_gain = (ridge_bias_permille * (directional_alignment + 320)) // 1000
        profile_wave = abs((((sample_index * (horizontal_strength + 173)) % 2000) - 1000))
        profile_gain = (profile_wave * macro_relief_permille) // 5000
        continent_gain = (continent_mask_permille * max(1, sample_count - sample_index + 1)) // max(1, sample_count * 5)
        coastal_damping = (coastal_bias_permille * distance_cells) // 12
        sample_height = max(
            base_height,
            base_height + relief_gain + ridge_gain + profile_gain + continent_gain - coastal_damping,
        )
        height_delta = max(0, sample_height - base_height)
        bias = (horizon_bias_mdeg * max(macro_relief_permille, ridge_bias_permille)) // 1000
        horizon_angle = _clamp(bias + ((height_delta * 90_000) // distance_units), 0, max_occlusion_mdeg)
        rows.append(
            {
                "sample_index": int(sample_index),
                "distance_cells": int(distance_cells),
                "step_lat_sign": int(_sign(horizontal_y)),
                "step_lon_sign": int(_sign(horizontal_x)),
                "azimuth_sector": azimuth_sector,
                "sample_elevation_proxy": int(sample_height),
                "height_delta_proxy": int(height_delta),
                "horizon_angle_mdeg": int(horizon_angle),
            }
        )
    return rows


def _shadow_factor_permille(*, sun_elevation_mdeg: int, max_horizon_angle_mdeg: int, soft_transition_band_mdeg: int) -> int:
    elevation = _as_int(sun_elevation_mdeg, 0)
    if elevation <= 0:
        return 0
    band = max(1, _as_int(soft_transition_band_mdeg, 1600))
    lower = max_horizon_angle_mdeg - band
    upper = max_horizon_angle_mdeg + band
    if elevation <= lower:
        return 0
    if elevation >= upper:
        return 1000
    return _clamp(((elevation - lower) * 1000) // max(1, upper - lower), 0, 1000)


def evaluate_horizon_shadow(
    *,
    sky_view_artifact: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None = None,
    shadow_model_row: Mapping[str, object] | None = None,
) -> dict:
    sky_artifact = _as_map(sky_view_artifact)
    model = dict(
        _as_map(shadow_model_row)
        or shadow_model_rows().get(DEFAULT_SHADOW_MODEL_ID)
        or {}
    )
    row_ext = _as_map(model.get("extensions"))
    sky_ext = _as_map(sky_artifact.get("extensions"))
    sun_elevation_mdeg = _as_int(sky_ext.get("sun_elevation_mdeg", 0), 0)
    if str(model.get("kind", "")).strip() == "none":
        payload = {
            "shadow_model_id": str(model.get("shadow_model_id", "")).strip() or "shadow.none",
            "sun_elevation_mdeg": int(sun_elevation_mdeg),
            "shadow_factor_permille": 0 if sun_elevation_mdeg <= 0 else 1000,
            "max_horizon_angle_mdeg": 0,
            "occluded": bool(sun_elevation_mdeg <= 0),
            "sampling_bounded": True,
            "sample_count": 0,
            "samples": [],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    base_height, macro_relief, ridge_bias, coastal_bias, continent_mask = _surface_height_inputs(observer_surface_artifact)
    samples = _sample_trace(
        base_height=base_height,
        macro_relief_permille=macro_relief,
        ridge_bias_permille=ridge_bias,
        coastal_bias_permille=coastal_bias,
        continent_mask_permille=continent_mask,
        sun_dir=_as_map(sky_artifact.get("sun_direction")),
        shadow_model_row=model,
    )
    max_horizon_angle = max((int(_as_int(row.get("horizon_angle_mdeg", 0), 0)) for row in samples), default=0)
    shadow_factor = _shadow_factor_permille(
        sun_elevation_mdeg=sun_elevation_mdeg,
        max_horizon_angle_mdeg=max_horizon_angle,
        soft_transition_band_mdeg=_as_int(row_ext.get("soft_transition_band_mdeg", 1600), 1600),
    )
    payload = {
        "shadow_model_id": str(model.get("shadow_model_id", "")).strip() or DEFAULT_SHADOW_MODEL_ID,
        "sun_elevation_mdeg": int(sun_elevation_mdeg),
        "shadow_factor_permille": int(shadow_factor),
        "max_horizon_angle_mdeg": int(max_horizon_angle),
        "occluded": bool(shadow_factor < 500),
        "sampling_bounded": True,
        "sample_count": int(len(samples)),
        "samples": [dict(row) for row in samples],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_SHADOW_MODEL_ID",
    "EARTH_HORIZON_SHADOW_ENGINE_VERSION",
    "SHADOW_MODEL_REGISTRY_REL",
    "evaluate_horizon_shadow",
    "shadow_model_registry_hash",
    "shadow_model_rows",
]
