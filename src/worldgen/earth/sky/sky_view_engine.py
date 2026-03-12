"""Deterministic EARTH-4 sky view artifact engine."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Dict, Mapping

from src.astro import build_view_artifact_from_directions
from src.worldgen.mw import normalize_planet_basic_artifact_rows, normalize_star_artifact_rows
from src.worldgen.mw.mw_cell_generator import galaxy_priors_registry_hash, galaxy_priors_rows
from tools.xstack.compatx.canonical_json import canonical_sha256

from .astronomy_proxy_engine import moon_direction_proxy, sun_direction_proxy
from .sky_gradient_model import evaluate_sky_gradient
from .starfield_generator import (
    MILKYWAY_BAND_POLICY_REGISTRY_REL,
    STARFIELD_POLICY_REGISTRY_REL,
    build_starfield_snapshot,
    milkyway_band_policy_rows,
    starfield_policy_rows,
)
from ..climate_field_engine import DEFAULT_EARTH_CLIMATE_PARAMS_ID, earth_climate_params_rows
from ..tide_field_engine import DEFAULT_TIDE_PARAMS_ID, tide_params_rows


DEFAULT_SKY_MODEL_ID = "sky.gradient_stub_default"
DEFAULT_STARFIELD_POLICY_ID = "stars.mvp_default"
DEFAULT_MILKYWAY_BAND_POLICY_ID = "mwband.mvp_stub"
SKY_MODEL_REGISTRY_REL = os.path.join("data", "registries", "sky_model_registry.json")
EARTH_SKY_VIEW_ENGINE_VERSION = "EARTH4-6"
_SKY_VIEW_CACHE: Dict[str, dict] = {}
_SKY_VIEW_CACHE_MAX = 128
_DEFAULT_MOON_ALBEDO_PROXY_PERMILLE = 120
_DEFAULT_MOON_RADIUS_KM = 1737
_DEFAULT_STAR_LUMINOSITY_PROXY = 1000


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


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _rows_by_object_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        token = str(dict(row).get("object_id", "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


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


def sky_model_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(SKY_MODEL_REGISTRY_REL),
        row_key="sky_models",
        id_key="sky_model_id",
    )


def sky_model_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(SKY_MODEL_REGISTRY_REL))


def starfield_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(STARFIELD_POLICY_REGISTRY_REL))


def milkyway_band_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(MILKYWAY_BAND_POLICY_REGISTRY_REL))


def _cache_lookup(cache_key: str) -> dict | None:
    row = _SKY_VIEW_CACHE.get(str(cache_key))
    if not isinstance(row, dict):
        return None
    return copy.deepcopy(dict(row))


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _SKY_VIEW_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_SKY_VIEW_CACHE) > _SKY_VIEW_CACHE_MAX:
        for stale_key in sorted(_SKY_VIEW_CACHE.keys())[:-_SKY_VIEW_CACHE_MAX]:
            _SKY_VIEW_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def _observer_lat_long(
    *,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
) -> tuple[int, int]:
    artifact_ext = _as_map(_as_map(observer_surface_artifact).get("extensions"))
    observer_ext = _as_map(_as_map(observer_ref).get("extensions"))
    latitude_mdeg = _as_int(
        artifact_ext.get("latitude_mdeg", observer_ext.get("latitude_mdeg", 0)),
        0,
    )
    longitude_mdeg = _as_int(
        artifact_ext.get("longitude_mdeg", observer_ext.get("longitude_mdeg", 0)),
        0,
    )
    return int(latitude_mdeg), int(longitude_mdeg)


def _fallback_observer_cell_key(observer_ref: Mapping[str, object] | None) -> dict:
    ref = _as_map(observer_ref)
    local_position = list(ref.get("local_position") or [])
    while len(local_position) < 3:
        local_position.append(0)
    quantum_mm = 250_000
    return {
        "topology_profile_id": "geo.topology.r3_infinite",
        "partition_profile_id": "geo.partition.grid_zd",
        "chart_id": "chart.sky.observer",
        "refinement_level": 0,
        "index_tuple": [int(_as_int(item, 0)) // quantum_mm for item in local_position[:3]],
        "extensions": {
            "source": "EARTH4-6",
        },
    }


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
    cell_key = _as_map(observer_ext.get("geo_cell_key"))
    if cell_key:
        return cell_key
    return _fallback_observer_cell_key(observer_ref)


def _camera_orientation_mdeg(perceived_model: Mapping[str, object] | None) -> dict:
    camera = _as_map(_as_map(perceived_model).get("camera_viewpoint"))
    orientation = _as_map(camera.get("orientation_mdeg"))
    return {
        "yaw": int(_as_int(orientation.get("yaw", 0), 0)),
        "pitch": int(_as_int(orientation.get("pitch", 0), 0)),
        "roll": int(_as_int(orientation.get("roll", 0), 0)),
    }


def _screen_projection(*, azimuth_mdeg: int, altitude_mdeg: int, camera_orientation_mdeg: Mapping[str, object] | None) -> dict:
    orientation = _as_map(camera_orientation_mdeg)
    yaw_mdeg = int(_as_int(orientation.get("yaw", 0), 0))
    pitch_mdeg = int(_as_int(orientation.get("pitch", 0), 0))
    relative_azimuth = ((_as_int(azimuth_mdeg, 0) - yaw_mdeg + 540_000) % 360_000) - 180_000
    relative_altitude = _as_int(altitude_mdeg, 0) - pitch_mdeg
    screen_x = _clamp(500 + ((relative_azimuth * 500) // 90_000), -500, 1500)
    screen_y = _clamp(500 - ((relative_altitude * 500) // 90_000), -500, 1500)
    visible = abs(relative_azimuth) <= 100_000 and relative_altitude >= -30_000 and relative_altitude <= 100_000
    return {
        "screen_x_permille": int(screen_x),
        "screen_y_permille": int(screen_y),
        "visible": bool(visible),
    }


def _sky_visibility_permille(*, sky_gradient: Mapping[str, object], starfield_policy_row: Mapping[str, object]) -> int:
    sun_intensity = _clamp(_as_int(_as_map(sky_gradient).get("sun_intensity_permille", 0), 0), 0, 1000)
    threshold = _clamp(
        _as_int(_as_map(_as_map(starfield_policy_row).get("extensions")).get("sun_visibility_threshold_permille", 180), 180),
        1,
        1000,
    )
    if sun_intensity >= threshold:
        return 0
    return _clamp(((threshold - sun_intensity) * 1000) // threshold, 0, 1000)


def _debug_overlay_payload(
    *,
    authority_context: Mapping[str, object] | None,
    lens_profile_id: str,
    milkyway_band_rows: object,
    epistemic_policy_id: str,
) -> dict:
    entitlements = set(_sorted_strings(_as_map(authority_context).get("entitlements")))
    enabled = (
        "entitlement.debug_view" in entitlements
        or "entitlement.observer.truth" in entitlements
        or str(epistemic_policy_id or "").strip() == "epistemic.admin_full"
    )
    rows = [dict(row) for row in list(milkyway_band_rows or []) if isinstance(row, Mapping)]
    payload = {
        "galactic_plane_marker": {
            "enabled": bool(enabled),
            "lens_profile_id": str(lens_profile_id or "").strip(),
            "epistemic_policy_id": str(epistemic_policy_id or "").strip(),
            "sample_count": int(len(rows) if enabled else 0),
        },
        "debug_overlay_log": [
            {
                "overlay_id": "overlay.sky.galactic_plane_marker",
                "enabled": bool(enabled),
                "required_entitlement": "entitlement.debug_view",
            }
        ],
    }
    return payload


def _moon_receiver_stub(
    *,
    planet_object_id: str,
    planet_basic_artifact_rows: object,
) -> dict:
    rows_by_id = _rows_by_object_id(normalize_planet_basic_artifact_rows(planet_basic_artifact_rows))
    planet_row = dict(rows_by_id.get(str(planet_object_id or "").strip()) or {})
    extensions = _as_map(planet_row.get("extensions"))
    moon_rows = sorted(
        [dict(row) for row in list(extensions.get("moon_stub_descriptors") or []) if isinstance(row, Mapping)],
        key=lambda row: (
            int(_as_int(row.get("moon_index", 0), 0)),
            str(row.get("object_id", "")),
        ),
    )
    if moon_rows:
        moon_row = dict(moon_rows[0])
        return {
            "object_id": str(moon_row.get("object_id", "")).strip(),
            "radius_km": int(
                max(
                    1,
                    _as_int(
                        _as_map(moon_row.get("radius")).get("value", moon_row.get("radius_km", _DEFAULT_MOON_RADIUS_KM)),
                        _DEFAULT_MOON_RADIUS_KM,
                    ),
                )
            ),
            "albedo_proxy_permille": int(
                _clamp(
                    _as_int(
                        _as_map(moon_row.get("body_albedo_proxy")).get(
                            "value",
                            moon_row.get("albedo_proxy_permille", _DEFAULT_MOON_ALBEDO_PROXY_PERMILLE),
                        ),
                        _DEFAULT_MOON_ALBEDO_PROXY_PERMILLE,
                    ),
                    0,
                    1000,
                )
            ),
            "kind": "receiver.moon",
        }
    planet_token = str(planet_object_id or "").strip() or "planet"
    return {
        "object_id": "object.moon.stub.{}".format(planet_token[:16]),
        "radius_km": _DEFAULT_MOON_RADIUS_KM,
        "albedo_proxy_permille": _DEFAULT_MOON_ALBEDO_PROXY_PERMILLE,
        "kind": "receiver.moon",
    }


def _star_emitter_stub(
    *,
    star_object_id: str,
    star_artifact_rows: object,
) -> dict:
    rows_by_id = _rows_by_object_id(normalize_star_artifact_rows(star_artifact_rows))
    star_row = dict(rows_by_id.get(str(star_object_id or "").strip()) or {})
    return {
        "object_id": str(star_row.get("object_id", "")).strip() or str(star_object_id or "").strip() or "object.star.stub",
        "luminosity_proxy_value": int(
            max(
                0,
                _as_int(
                    _as_map(star_row.get("luminosity_proxy")).get("value", _DEFAULT_STAR_LUMINOSITY_PROXY),
                    _DEFAULT_STAR_LUMINOSITY_PROXY,
                ),
            )
        ),
    }


def build_sky_view_surface(
    *,
    universe_identity: Mapping[str, object] | None,
    perceived_model: Mapping[str, object] | None,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    lens_profile_id: str = "",
    sky_model_id: str = DEFAULT_SKY_MODEL_ID,
    starfield_policy_id: str = DEFAULT_STARFIELD_POLICY_ID,
    milkyway_band_policy_id: str = DEFAULT_MILKYWAY_BAND_POLICY_ID,
    ui_mode: str = "gui",
    star_artifact_rows: object = None,
    planet_basic_artifact_rows: object = None,
) -> dict:
    universe = _as_map(universe_identity)
    perceived = _as_map(perceived_model)
    tick = max(0, _as_int(_as_map(perceived.get("time_state")).get("tick", 0), 0))
    observer = _as_map(observer_ref)
    surface_artifact = _as_map(observer_surface_artifact)
    metadata = _as_map(perceived.get("metadata"))
    epistemic_policy_id = str(
        metadata.get(
            "epistemic_policy_id",
            _as_map(_as_map(authority_context).get("epistemic_scope")).get("scope_id", ""),
        )
    ).strip()
    sky_model_row = dict(sky_model_rows().get(str(sky_model_id).strip() or DEFAULT_SKY_MODEL_ID) or {})
    star_policy_row = dict(starfield_policy_rows().get(str(starfield_policy_id).strip() or DEFAULT_STARFIELD_POLICY_ID) or {})
    band_policy_row = dict(milkyway_band_policy_rows().get(str(milkyway_band_policy_id).strip() or DEFAULT_MILKYWAY_BAND_POLICY_ID) or {})
    climate_rows = earth_climate_params_rows()
    tide_rows = tide_params_rows()
    surface_ext = _as_map(surface_artifact.get("extensions"))
    climate_params_row = dict(
        climate_rows.get(str(surface_ext.get("earth_climate_params_id", DEFAULT_EARTH_CLIMATE_PARAMS_ID)).strip() or DEFAULT_EARTH_CLIMATE_PARAMS_ID)
        or climate_rows.get(DEFAULT_EARTH_CLIMATE_PARAMS_ID)
        or {}
    )
    tide_params_row = dict(
        tide_rows.get(str(surface_ext.get("tide_params_id", DEFAULT_TIDE_PARAMS_ID)).strip() or DEFAULT_TIDE_PARAMS_ID)
        or tide_rows.get(DEFAULT_TIDE_PARAMS_ID)
        or {}
    )
    observer_cell_key = _observer_cell_key(observer_ref=observer, observer_surface_artifact=surface_artifact)
    observer_hash = canonical_sha256(observer_cell_key)
    camera_orientation = _camera_orientation_mdeg(perceived)
    cache_key = canonical_sha256(
        {
            "universe_seed": str(universe.get("universe_seed", "")).strip(),
            "generator_version_id": str(universe.get("generator_version_id", "")).strip(),
            "realism_profile_id": str(universe.get("realism_profile_id", "")).strip(),
            "tick": int(tick),
            "observer_cell_key_hash": observer_hash,
            "lens_profile_id": str(lens_profile_id or "").strip(),
            "camera_orientation_mdeg": dict(camera_orientation),
            "sky_model_id": str(sky_model_id or "").strip(),
            "starfield_policy_id": str(starfield_policy_id or "").strip(),
            "milkyway_band_policy_id": str(milkyway_band_policy_id or "").strip(),
            "observer_surface_artifact_hash": canonical_sha256(surface_artifact) if surface_artifact else "",
            "star_artifact_rows_hash": canonical_sha256(normalize_star_artifact_rows(star_artifact_rows)),
            "planet_basic_artifact_rows_hash": canonical_sha256(normalize_planet_basic_artifact_rows(planet_basic_artifact_rows)),
        }
    )
    cached = _cache_lookup(cache_key)
    if cached is not None:
        out = dict(cached)
        out["cache_hit"] = True
        return out

    latitude_mdeg, longitude_mdeg = _observer_lat_long(observer_ref=observer, observer_surface_artifact=surface_artifact)
    sun_payload = sun_direction_proxy(
        latitude_mdeg=latitude_mdeg,
        longitude_mdeg=longitude_mdeg,
        current_tick=tick,
        climate_params_row=climate_params_row,
        tide_params_row=tide_params_row,
    )
    moon_payload = moon_direction_proxy(
        latitude_mdeg=latitude_mdeg,
        longitude_mdeg=longitude_mdeg,
        current_tick=tick,
        climate_params_row=climate_params_row,
        tide_params_row=tide_params_row,
    )
    star_emitter = _star_emitter_stub(
        star_object_id=str(surface_ext.get("parent_star_object_id", "")).strip(),
        star_artifact_rows=star_artifact_rows,
    )
    moon_receiver = _moon_receiver_stub(
        planet_object_id=str(surface_artifact.get("planet_object_id", "")).strip(),
        planet_basic_artifact_rows=planet_basic_artifact_rows,
    )
    moon_illumination_view_artifact = build_view_artifact_from_directions(
        tick=int(tick),
        viewer_ref=observer,
        emitter_object_id=str(star_emitter.get("object_id", "")).strip(),
        receiver_object_id=str(moon_receiver.get("object_id", "")).strip(),
        emitter_direction=_as_map(sun_payload.get("sun_direction")),
        receiver_direction=_as_map(moon_payload.get("moon_direction")),
        luminosity_proxy_value=int(star_emitter.get("luminosity_proxy_value", _DEFAULT_STAR_LUMINOSITY_PROXY)),
        receiver_radius_km=int(moon_receiver.get("radius_km", _DEFAULT_MOON_RADIUS_KM)),
        receiver_albedo_proxy_permille=int(moon_receiver.get("albedo_proxy_permille", _DEFAULT_MOON_ALBEDO_PROXY_PERMILLE)),
        receiver_kind=str(moon_receiver.get("kind", "receiver.moon")).strip() or "receiver.moon",
    )
    moon_illumination_permille = int(_as_int(moon_illumination_view_artifact.get("illumination_fraction", 0), 0))
    sky_gradient = evaluate_sky_gradient(
        sun_elevation_mdeg=_as_int(sun_payload.get("sun_elevation_mdeg", 0), 0),
        sky_model_row=sky_model_row,
        moon_illumination_permille=moon_illumination_permille,
    )
    galaxy_rows = galaxy_priors_rows()
    galaxy_priors_row = dict(
        galaxy_rows.get(str(_as_map(universe).get("galaxy_priors_id", "")).strip())
        or galaxy_rows.get("priors.milkyway_stub_default")
        or {}
    )
    sky_visibility = _sky_visibility_permille(
        sky_gradient=sky_gradient,
        starfield_policy_row=star_policy_row,
    )
    starfield = build_starfield_snapshot(
        universe_identity=universe,
        observer_cell_key=observer_cell_key,
        current_tick=tick,
        observer_latitude_mdeg=latitude_mdeg,
        starfield_policy_row=star_policy_row,
        milkyway_band_policy_row=band_policy_row,
        galaxy_priors_row=galaxy_priors_row,
        sky_visibility_permille=sky_visibility,
    )
    star_rows = []
    for row in list(starfield.get("star_rows") or []):
        payload = dict(row)
        projection = _screen_projection(
            azimuth_mdeg=_as_int(payload.get("azimuth_mdeg", 0), 0),
            altitude_mdeg=_as_int(payload.get("altitude_mdeg", 0), 0),
            camera_orientation_mdeg=camera_orientation,
        )
        if not bool(projection.get("visible", False)):
            continue
        star_rows.append({**payload, **projection})
    band_rows = []
    for row in list(starfield.get("milkyway_band_rows") or []):
        payload = dict(row)
        projection = _screen_projection(
            azimuth_mdeg=_as_int(payload.get("azimuth_mdeg", 0), 0),
            altitude_mdeg=_as_int(payload.get("altitude_center_mdeg", 0), 0),
            camera_orientation_mdeg=camera_orientation,
        )
        if not bool(projection.get("visible", False)):
            continue
        band_rows.append({**payload, **projection})
    sun_screen = _screen_projection(
        azimuth_mdeg=_as_int(sun_payload.get("sun_azimuth_mdeg", 0), 0),
        altitude_mdeg=_as_int(sun_payload.get("sun_elevation_mdeg", 0), 0),
        camera_orientation_mdeg=camera_orientation,
    )
    moon_screen = _screen_projection(
        azimuth_mdeg=_as_int(moon_payload.get("moon_azimuth_mdeg", 0), 0),
        altitude_mdeg=_as_int(moon_payload.get("moon_elevation_mdeg", 0), 0),
        camera_orientation_mdeg=camera_orientation,
    )
    debug_overlays = _debug_overlay_payload(
        authority_context=authority_context,
        lens_profile_id=lens_profile_id,
        milkyway_band_rows=band_rows,
        epistemic_policy_id=epistemic_policy_id,
    )
    artifact = {
        "view_id": "sky_view.{}.tick.{}".format(observer_hash[:16], tick),
        "tick": int(tick),
        "observer_ref": dict(observer),
        "sky_model_id": str(sky_model_row.get("sky_model_id", "")).strip() or DEFAULT_SKY_MODEL_ID,
        "sun_direction": dict(sun_payload.get("sun_direction") or {}),
        "moon_direction": dict(moon_payload.get("moon_direction") or {}),
        "sky_colors_ref": {
            "zenith_color": dict(_as_map(sky_gradient.get("zenith_color"))),
            "horizon_color": dict(_as_map(sky_gradient.get("horizon_color"))),
            "sun_color": dict(_as_map(sky_gradient.get("sun_color"))),
            "sun_intensity_permille": int(_as_int(sky_gradient.get("sun_intensity_permille", 0), 0)),
            "twilight_factor_permille": int(_as_int(sky_gradient.get("twilight_factor_permille", 0), 0)),
        },
        "star_points_ref": list(star_rows),
        "milkyway_band_ref": list(band_rows),
        "deterministic_fingerprint": "",
        "extensions": {
            "source": EARTH_SKY_VIEW_ENGINE_VERSION,
            "derived_only": True,
            "compactable": True,
            "artifact_class": "DERIVED_VIEW",
            "cache_key": cache_key,
            "cache_policy_id": "cache.sky.observer_tick_bucket",
            "observer_cell_key": dict(observer_cell_key),
            "tick_bucket": int(starfield.get("tick_bucket", 0) or 0),
            "lens_profile_id": str(lens_profile_id or "").strip(),
            "sky_visibility_permille": int(sky_visibility),
            "sun_screen": dict(sun_screen),
            "moon_screen": dict(moon_screen),
            "sun_elevation_mdeg": int(_as_int(sun_payload.get("sun_elevation_mdeg", 0), 0)),
            "moon_elevation_mdeg": int(_as_int(moon_payload.get("moon_elevation_mdeg", 0), 0)),
            "moon_illumination_permille": int(moon_illumination_permille),
            "moon_illumination_view_artifact": dict(moon_illumination_view_artifact),
            "epistemic_policy_id": epistemic_policy_id,
            "visibility_policy": {
                "sky_dome_visible": True,
                "starfield_visible": bool(sky_visibility > 0),
                "debug_overlay_gated": True,
            },
            "registry_hashes": {
                "sky_model_registry_hash": sky_model_registry_hash(),
                "starfield_policy_registry_hash": starfield_policy_registry_hash(),
                "milkyway_band_policy_registry_hash": milkyway_band_policy_registry_hash(),
                "galaxy_priors_registry_hash": galaxy_priors_registry_hash(),
            },
            "debug_overlays": debug_overlays,
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    summary = {
        "sun_elevation_mdeg": int(_as_int(sun_payload.get("sun_elevation_mdeg", 0), 0)),
        "twilight_factor_permille": int(_as_int(sky_gradient.get("twilight_factor_permille", 0), 0)),
        "star_count": int(len(star_rows)),
        "milkyway_sample_count": int(len(band_rows)),
        "moon_illumination_permille": int(moon_illumination_permille),
        "moon_phase_angle_mdeg": int(_as_int(moon_illumination_view_artifact.get("phase_angle", 0), 0)),
    }
    payload = {
        "result": "complete",
        "source_kind": "derived.sky_view_artifact",
        "cache_hit": False,
        "cache_key": cache_key,
        "lens_layer_ids": ["layer.sky_dome", "layer.starfield"],
        "sky_view_artifact": artifact,
        "presentation": {
            "preferred_presentation": "summary" if str(ui_mode or "").strip().lower() in {"cli", "tui"} else "buffer",
            "summary": summary,
            "summary_text": "sun_elevation={} twilight={} stars={}".format(
                summary["sun_elevation_mdeg"],
                summary["twilight_factor_permille"],
                summary["star_count"],
            ),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)
