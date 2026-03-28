"""Deterministic EARTH-5 lighting-view artifact engine."""

from __future__ import annotations

import copy
from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from ..material import evaluate_earth_tile_material_proxy
from .horizon_shadow_engine import (
    DEFAULT_SHADOW_MODEL_ID,
    evaluate_horizon_shadow,
    shadow_model_registry_hash,
    shadow_model_rows,
)
from .illumination_engine import (
    DEFAULT_ILLUMINATION_MODEL_ID,
    build_earth_lighting_artifact,
    illumination_model_registry_hash,
    illumination_model_rows,
)


EARTH_LIGHTING_VIEW_ENGINE_VERSION = "EARTH5-5"
_LIGHTING_VIEW_CACHE: Dict[str, dict] = {}
_LIGHTING_VIEW_CACHE_MAX = 128


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _cache_lookup(cache_key: str) -> dict | None:
    row = _LIGHTING_VIEW_CACHE.get(str(cache_key))
    if not isinstance(row, dict):
        return None
    return copy.deepcopy(dict(row))


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _LIGHTING_VIEW_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_LIGHTING_VIEW_CACHE) > _LIGHTING_VIEW_CACHE_MAX:
        for stale_key in sorted(_LIGHTING_VIEW_CACHE.keys())[:-_LIGHTING_VIEW_CACHE_MAX]:
            _LIGHTING_VIEW_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def _observer_cell_key(
    *,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
) -> dict:
    artifact = _as_map(observer_surface_artifact)
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    if tile_cell_key:
        return tile_cell_key
    observer_ext = _as_map(_as_map(observer_ref).get("extensions"))
    return _as_map(observer_ext.get("geo_cell_key"))


def _surface_material_proxy_preview(
    observer_surface_artifact: Mapping[str, object] | None,
    *,
    tick_bucket: int,
) -> dict:
    artifact = _as_map(observer_surface_artifact)
    if not artifact:
        return {}
    return evaluate_earth_tile_material_proxy(
        artifact_row=artifact,
        current_tick=int(tick_bucket),
        geometry_row=None,
    )


def build_lighting_view_surface(
    *,
    sky_view_artifact: Mapping[str, object] | None,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None = None,
    illum_model_id: str = DEFAULT_ILLUMINATION_MODEL_ID,
    shadow_model_id: str = DEFAULT_SHADOW_MODEL_ID,
    ui_mode: str = "gui",
) -> dict:
    sky_artifact = _as_map(sky_view_artifact)
    observer = _as_map(observer_ref)
    surface_artifact = _as_map(observer_surface_artifact)
    illum_row = dict(illumination_model_rows().get(str(illum_model_id).strip() or DEFAULT_ILLUMINATION_MODEL_ID) or {})
    shadow_row = dict(shadow_model_rows().get(str(shadow_model_id).strip() or DEFAULT_SHADOW_MODEL_ID) or {})
    sky_ext = _as_map(sky_artifact.get("extensions"))
    tick_bucket = int(_as_int(sky_ext.get("tick_bucket", sky_artifact.get("tick", 0)), 0))
    observer_cell_key = _observer_cell_key(observer_ref=observer, observer_surface_artifact=surface_artifact)
    observer_hash = canonical_sha256(observer_cell_key) if observer_cell_key else canonical_sha256({"observer_ref": observer})
    cache_key = canonical_sha256(
        {
            "tick_bucket": int(tick_bucket),
            "observer_cell_key_hash": observer_hash,
            "illum_model_id": str(illum_row.get("illum_model_id", "")).strip(),
            "shadow_model_id": str(shadow_row.get("shadow_model_id", "")).strip(),
            "sky_view_fingerprint": str(sky_artifact.get("deterministic_fingerprint", "")).strip(),
            "observer_surface_fingerprint": canonical_sha256(surface_artifact) if surface_artifact else "",
        }
    )
    cached = _cache_lookup(cache_key)
    if cached is not None:
        out = dict(cached)
        out["cache_hit"] = True
        return out

    shadow_payload = evaluate_horizon_shadow(
        sky_view_artifact=sky_artifact,
        observer_surface_artifact=surface_artifact,
        shadow_model_row=shadow_row,
    )
    surface_material_proxy = _surface_material_proxy_preview(surface_artifact, tick_bucket=int(tick_bucket))
    artifact = build_earth_lighting_artifact(
        sky_view_artifact=sky_artifact,
        observer_ref=observer,
        illum_model_row=illum_row,
        shadow_model_id=str(shadow_row.get("shadow_model_id", "")).strip() or DEFAULT_SHADOW_MODEL_ID,
        shadow_factor_permille=int(_as_int(shadow_payload.get("shadow_factor_permille", 1000), 1000)),
    )
    artifact["extensions"] = {
        **_as_map(artifact.get("extensions")),
        "source": EARTH_LIGHTING_VIEW_ENGINE_VERSION,
        "cache_key": cache_key,
        "cache_policy_id": "cache.lighting.observer_tick_bucket",
        "tick_bucket": int(tick_bucket),
        "observer_cell_key": dict(observer_cell_key),
        "observer_surface_artifact_hash": canonical_sha256(surface_artifact) if surface_artifact else "",
        "shadow_summary": {
            "shadow_model_id": str(shadow_payload.get("shadow_model_id", "")).strip(),
            "shadow_factor_permille": int(_as_int(shadow_payload.get("shadow_factor_permille", 0), 0)),
            "max_horizon_angle_mdeg": int(_as_int(shadow_payload.get("max_horizon_angle_mdeg", 0), 0)),
            "sample_count": int(_as_int(shadow_payload.get("sample_count", 0), 0)),
            "sampling_bounded": bool(shadow_payload.get("sampling_bounded", False)),
        },
        "shadow_samples": [dict(row) for row in list(shadow_payload.get("samples") or []) if isinstance(row, Mapping)],
        "registry_hashes": {
            **_as_map(_as_map(artifact.get("extensions")).get("registry_hashes")),
            "illumination_model_registry_hash": illumination_model_registry_hash(),
            "shadow_model_registry_hash": shadow_model_registry_hash(),
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    summary = {
        "ambient_intensity": int(_as_int(artifact.get("ambient_intensity", 0), 0)),
        "sun_intensity": int(_as_int(artifact.get("sun_intensity", 0), 0)),
        "moon_intensity": int(_as_int(artifact.get("moon_intensity", 0), 0)),
        "shadow_factor": int(_as_int(artifact.get("shadow_factor", 0), 0)),
        "sample_count": int(_as_int(shadow_payload.get("sample_count", 0), 0)),
    }
    surface_reflectance_preview = {
        "material_proxy_id": str(surface_material_proxy.get("material_proxy_id", "")).strip() or None,
        "albedo_proxy_value": int(_as_int(surface_material_proxy.get("albedo_proxy_value", 0), 0)),
        "ambient_preview_intensity": int(
            (
                int(_as_int(artifact.get("ambient_intensity", 0), 0))
                * max(250, int(_as_int(surface_material_proxy.get("albedo_proxy_value", 500), 500)))
            )
            // 1000
        ),
        "source_kind": "derived.illumination_surface_reflectance_preview",
    }
    payload = {
        "result": "complete",
        "source_kind": "derived.illumination_view_artifact",
        "cache_hit": False,
        "cache_key": cache_key,
        "lens_layer_ids": ["layer.illumination", "layer.shadow_factor"],
        "illumination_view_artifact": artifact,
        "presentation": {
            "preferred_presentation": "summary" if str(ui_mode or "").strip().lower() in {"cli", "tui"} else "buffer",
            "summary": summary,
            "surface_reflectance_preview": surface_reflectance_preview,
            "summary_text": "ambient={} sun={} moon={} shadow={}".format(
                summary["ambient_intensity"],
                summary["sun_intensity"],
                summary["moon_intensity"],
                summary["shadow_factor"],
            ),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


__all__ = [
    "EARTH_LIGHTING_VIEW_ENGINE_VERSION",
    "build_lighting_view_surface",
]
