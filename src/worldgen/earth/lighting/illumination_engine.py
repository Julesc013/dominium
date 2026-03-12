"""Deterministic EARTH-5 illumination artifact helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_ILLUMINATION_MODEL_ID = "illum.basic_diffuse_default"
ILLUMINATION_MODEL_REGISTRY_REL = os.path.join("data", "registries", "illumination_model_registry.json")
EARTH_ILLUMINATION_ENGINE_VERSION = "EARTH5-3"


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


def illumination_model_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(ILLUMINATION_MODEL_REGISTRY_REL),
        row_key="illumination_models",
        id_key="illum_model_id",
    )


def illumination_model_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(ILLUMINATION_MODEL_REGISTRY_REL))


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


def _ambient_intensity_permille(*, sky_artifact: Mapping[str, object], illum_model_row: Mapping[str, object]) -> int:
    colors = _as_map(_as_map(sky_artifact).get("sky_colors_ref"))
    model_ext = _as_map(_as_map(illum_model_row).get("extensions"))
    sun_intensity = _clamp(_as_int(colors.get("sun_intensity_permille", 0), 0), 0, 1000)
    twilight = _clamp(_as_int(colors.get("twilight_factor_permille", 0), 0), 0, 1000)
    day_value = _clamp(_as_int(model_ext.get("ambient_day_permille", 520), 520), 0, 1000)
    twilight_value = _clamp(_as_int(model_ext.get("ambient_twilight_permille", 340), 340), 0, 1000)
    night_value = _clamp(_as_int(model_ext.get("ambient_night_permille", 90), 90), 0, 1000)
    min_value = _clamp(_as_int(model_ext.get("ambient_min_permille", 40), 40), 0, 1000)
    if sun_intensity >= 600:
        return _clamp(day_value, min_value, 1000)
    twilight_mix = _clamp((sun_intensity * (1000 - twilight)) // 1000, 0, 1000)
    base = night_value + (((twilight_value - night_value) * twilight) // 1000)
    return _clamp(base + (((day_value - base) * twilight_mix) // 1000), min_value, 1000)


def _sky_light_color(*, sky_artifact: Mapping[str, object], illum_model_row: Mapping[str, object]) -> dict:
    colors = _as_map(_as_map(sky_artifact).get("sky_colors_ref"))
    model_ext = _as_map(_as_map(illum_model_row).get("extensions"))
    sun_intensity = _clamp(_as_int(colors.get("sun_intensity_permille", 0), 0), 0, 1000)
    twilight = _clamp(_as_int(colors.get("twilight_factor_permille", 0), 0), 0, 1000)
    day_color = _as_map(model_ext.get("sky_light_day_color"))
    twilight_color = _as_map(model_ext.get("sky_light_twilight_color"))
    night_color = _as_map(model_ext.get("sky_light_night_color"))
    if sun_intensity >= 600:
        return _mix_color(twilight_color, day_color, _clamp((sun_intensity - 600) * 2, 0, 1000))
    if sun_intensity > 0 or twilight > 0:
        return _mix_color(night_color, twilight_color, max(twilight, sun_intensity))
    return dict(night_color)


def _moon_fill_intensity_permille(*, sky_artifact: Mapping[str, object], illum_model_row: Mapping[str, object]) -> int:
    sky_ext = _as_map(_as_map(sky_artifact).get("extensions"))
    colors = _as_map(_as_map(sky_artifact).get("sky_colors_ref"))
    model_ext = _as_map(_as_map(illum_model_row).get("extensions"))
    moon_geometry = _as_map(sky_ext.get("moon_illumination_view_artifact"))
    moon_illumination = _clamp(
        _as_int(moon_geometry.get("illumination_fraction", sky_ext.get("moon_illumination_permille", 0)), 0),
        0,
        1000,
    )
    sun_intensity = _clamp(_as_int(colors.get("sun_intensity_permille", 0), 0), 0, 1000)
    moon_fill_max = _clamp(_as_int(model_ext.get("moon_fill_max_permille", 220), 220), 0, 1000)
    return _clamp((moon_fill_max * moon_illumination * max(0, 1000 - sun_intensity)) // 1_000_000, 0, 1000)


def build_earth_lighting_artifact(
    *,
    sky_view_artifact: Mapping[str, object] | None,
    observer_ref: Mapping[str, object] | None,
    illum_model_row: Mapping[str, object] | None = None,
    shadow_model_id: str = "shadow.none",
    shadow_factor_permille: int = 1000,
) -> dict:
    sky_artifact = _as_map(sky_view_artifact)
    observer = _as_map(observer_ref)
    model = dict(
        _as_map(illum_model_row)
        or illumination_model_rows().get(DEFAULT_ILLUMINATION_MODEL_ID)
        or {}
    )
    sky_colors = _as_map(sky_artifact.get("sky_colors_ref"))
    sky_ext = _as_map(sky_artifact.get("extensions"))
    sun_dir = dict(_as_map(sky_artifact.get("sun_direction")))
    moon_dir = dict(_as_map(sky_artifact.get("moon_direction")))
    ambient_intensity = _ambient_intensity_permille(
        sky_artifact=sky_artifact,
        illum_model_row=model,
    )
    sky_light_color = _sky_light_color(
        sky_artifact=sky_artifact,
        illum_model_row=model,
    )
    sun_intensity = _clamp(_as_int(sky_colors.get("sun_intensity_permille", 0), 0), 0, 1000)
    twilight_factor = _clamp(_as_int(sky_colors.get("twilight_factor_permille", 0), 0), 0, 1000)
    sun_key_day = _clamp(_as_int(_as_map(model.get("extensions")).get("sun_key_day_permille", 960), 960), 0, 1000)
    sun_key_twilight = _clamp(_as_int(_as_map(model.get("extensions")).get("sun_key_twilight_permille", 620), 620), 0, 1000)
    key_light_intensity = _clamp(
        (sun_intensity * (sun_key_twilight + (((sun_key_day - sun_key_twilight) * max(0, 1000 - twilight_factor)) // 1000))) // 1000,
        0,
        1000,
    )
    moon_intensity = _moon_fill_intensity_permille(
        sky_artifact=sky_artifact,
        illum_model_row=model,
    )
    sky_color = _as_map(sky_colors.get("horizon_color"))
    zenith_color = _as_map(sky_colors.get("zenith_color"))
    ambient_color = _mix_color(sky_color, zenith_color, 350)
    payload = {
        "view_id": "illumination_view.{}.tick.{}".format(
            canonical_sha256(observer)[:16] if observer else "observer",
            int(_as_int(sky_artifact.get("tick", 0), 0)),
        ),
        "tick": int(_as_int(sky_artifact.get("tick", 0), 0)),
        "observer_ref": dict(observer),
        "illum_model_id": str(model.get("illum_model_id", "")).strip() or DEFAULT_ILLUMINATION_MODEL_ID,
        "shadow_model_id": str(shadow_model_id or "shadow.none").strip() or "shadow.none",
        "sun_dir": dict(sun_dir),
        "sun_intensity": int(key_light_intensity),
        "moon_dir": dict(moon_dir),
        "moon_intensity": int(moon_intensity),
        "ambient_intensity": int(ambient_intensity),
        "shadow_factor": int(_clamp(_as_int(shadow_factor_permille, 1000), 0, 1000)),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": EARTH_ILLUMINATION_ENGINE_VERSION,
            "derived_only": True,
            "compactable": True,
            "artifact_class": "DERIVED_VIEW",
            "moon_illumination_view_artifact": dict(_as_map(sky_ext.get("moon_illumination_view_artifact"))),
            "ambient_color": ambient_color,
            "sky_light_color": sky_light_color,
            "key_light_color": dict(_as_map(sky_colors.get("sun_color")) or {"r": 255, "g": 240, "b": 220}),
            "fill_light_color": _mix_color({"r": 48, "g": 52, "b": 62}, {"r": 220, "g": 224, "b": 236}, int(moon_intensity)),
            "sky_twilight_factor_permille": int(twilight_factor),
            "sun_screen": dict(_as_map(sky_ext.get("sun_screen"))),
            "moon_screen": dict(_as_map(sky_ext.get("moon_screen"))),
            "registry_hashes": {
                "illumination_model_registry_hash": illumination_model_registry_hash(),
            },
            "lighting_summary": {
                "ambient_intensity": int(ambient_intensity),
                "key_light_intensity": int(key_light_intensity),
                "fill_light_intensity": int(moon_intensity),
            },
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_ILLUMINATION_MODEL_ID",
    "EARTH_ILLUMINATION_ENGINE_VERSION",
    "ILLUMINATION_MODEL_REGISTRY_REL",
    "build_earth_lighting_artifact",
    "illumination_model_registry_hash",
    "illumination_model_rows",
]
