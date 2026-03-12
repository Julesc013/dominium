"""Deterministic EARTH-4 procedural starfield helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Mapping

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.worldgen.mw.mw_cell_generator import galaxy_priors_rows
from tools.xstack.compatx.canonical_json import canonical_sha256


STARFIELD_POLICY_REGISTRY_REL = os.path.join("data", "registries", "starfield_policy_registry.json")
MILKYWAY_BAND_POLICY_REGISTRY_REL = os.path.join("data", "registries", "milkyway_band_policy_registry.json")
EARTH_STARFIELD_GENERATOR_VERSION = "EARTH4-5"


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


def starfield_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(STARFIELD_POLICY_REGISTRY_REL),
        row_key="starfield_policies",
        id_key="policy_id",
    )


def milkyway_band_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(MILKYWAY_BAND_POLICY_REGISTRY_REL),
        row_key="milkyway_band_policies",
        id_key="policy_id",
    )


def sky_tick_bucket(*, current_tick: int, tick_bucket_size: int) -> int:
    size = max(1, _as_int(tick_bucket_size, 1))
    return max(0, _as_int(current_tick, 0)) // size


def _observer_key_hash(observer_cell_key: Mapping[str, object] | None) -> str:
    key_row = _coerce_cell_key(observer_cell_key) or {}
    if key_row:
        return canonical_sha256(_semantic_cell_key(key_row))
    return canonical_sha256({"observer_cell_key": "fallback"})


def _stream_seed(
    *,
    universe_identity: Mapping[str, object],
    observer_cell_key: Mapping[str, object] | None,
    tick_bucket: int,
) -> str:
    identity = _as_map(universe_identity)
    return canonical_sha256(
        {
            "stream_name": "rng.view.sky.starfield",
            "universe_seed": str(identity.get("universe_seed", "")).strip(),
            "generator_version_id": str(identity.get("generator_version_id", "")).strip(),
            "realism_profile_id": str(identity.get("realism_profile_id", "")).strip(),
            "observer_cell_key": _observer_key_hash(observer_cell_key),
            "tick_bucket": int(tick_bucket),
        }
    )


def _hash_int(seed: str, salt: str) -> int:
    return int(canonical_sha256({"seed": str(seed), "salt": str(salt)})[:16], 16)


def _color_for_magnitude(magnitude_permille: int, policy_row: Mapping[str, object]) -> dict:
    ext = _as_map(_as_map(policy_row).get("extensions"))
    bins = list(ext.get("magnitude_bins") or [])
    for row in bins:
        item = _as_map(row)
        if magnitude_permille <= _as_int(item.get("max_permille", 1000), 1000):
            return dict(_as_map(item.get("color")) or {"r": 224, "g": 234, "b": 255})
    return {"r": 224, "g": 234, "b": 255}


def _visibility_star_count(*, policy_row: Mapping[str, object], sky_visibility_permille: int) -> int:
    max_stars = max(0, _as_int(_as_map(policy_row).get("max_stars", 0), 0))
    visibility = _clamp(_as_int(sky_visibility_permille, 0), 0, 1000)
    return (max_stars * visibility) // 1000


def _build_star_rows(
    *,
    stream_seed: str,
    policy_row: Mapping[str, object],
    visible_star_count: int,
) -> list[dict]:
    policy = _as_map(policy_row)
    ext = _as_map(policy.get("extensions"))
    magnitude_range = _as_map(policy.get("magnitude_range"))
    minimum_magnitude = _clamp(_as_int(magnitude_range.get("min_permille", 0), 0), 0, 1000)
    maximum_magnitude = _clamp(_as_int(magnitude_range.get("max_permille", 1000), 1000), minimum_magnitude, 1000)
    min_altitude = _clamp(_as_int(ext.get("min_altitude_mdeg", 1000), 1000), 0, 45_000)
    rows = []
    for index in range(max(0, int(visible_star_count))):
        azimuth_mdeg = _hash_int(stream_seed, "star.azimuth.{}".format(index)) % 360_000
        altitude_draw = _hash_int(stream_seed, "star.altitude.{}".format(index)) % 1000
        altitude_mdeg = min_altitude + ((88_000 - min_altitude) * altitude_draw // 1000)
        magnitude_draw = _hash_int(stream_seed, "star.magnitude.{}".format(index)) % 1000
        weighted_draw = (magnitude_draw * magnitude_draw) // 1000
        magnitude_permille = minimum_magnitude + (((maximum_magnitude - minimum_magnitude) * weighted_draw) // 1000)
        color = _color_for_magnitude(magnitude_permille, policy)
        rows.append(
            {
                "star_index": int(index),
                "azimuth_mdeg": int(azimuth_mdeg),
                "altitude_mdeg": int(altitude_mdeg),
                "magnitude_permille": int(magnitude_permille),
                "color": dict(color),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "stream_seed": stream_seed,
                        "star_index": int(index),
                        "azimuth_mdeg": int(azimuth_mdeg),
                        "altitude_mdeg": int(altitude_mdeg),
                        "magnitude_permille": int(magnitude_permille),
                        "color": dict(color),
                    }
                ),
            }
        )
    return rows


def _build_milkyway_band_rows(
    *,
    stream_seed: str,
    policy_row: Mapping[str, object],
    galaxy_priors_row: Mapping[str, object],
    galaxy_proxy_row: Mapping[str, object] | None,
    observer_latitude_mdeg: int,
    tick_bucket: int,
    sky_visibility_permille: int,
) -> list[dict]:
    policy = _as_map(policy_row)
    galaxy = _as_map(galaxy_priors_row)
    policy_ext = _as_map(policy.get("extensions"))
    density_params = _as_map(galaxy.get("density_params"))
    arm_count = max(1, _as_int(galaxy.get("arm_count", 4), 4))
    sample_count = max(4, _as_int(policy.get("sample_count", 12), 12))
    band_half_width = _clamp(_as_int(policy.get("band_half_width_mdeg", 16000), 16000), 4000, 90_000)
    peak = _clamp(_as_int(policy.get("brightness_peak_permille", 720), 720), 0, 1000)
    contrast = _clamp(_as_int(density_params.get("arm_contrast_permille", 240), 240), 0, 1000)
    visibility = _clamp(_as_int(sky_visibility_permille, 0), 0, 1000)
    if visibility <= 0:
        return []
    proxy_row = _as_map(galaxy_proxy_row)
    proxy_density = _clamp(_as_int(proxy_row.get("stellar_density_proxy_value", 0), 0), 0, 1000)
    proxy_radiation = _clamp(_as_int(proxy_row.get("radiation_background_proxy_value", 0), 0), 0, 1000)
    proxy_alignment_permille = 1000
    if proxy_row:
        proxy_alignment_permille = _clamp(
            800 + ((proxy_density * 140) // 1000) + ((proxy_radiation * 60) // 1000),
            800,
            1100,
        )
    center_azimuth = (
        _hash_int(stream_seed, "milkyway.center")
        + (tick_bucket * 13_000)
        + (arm_count * 7_500)
    ) % 360_000
    center_altitude = _clamp(
        _as_int(policy_ext.get("plane_tilt_mdeg", 63_000), 63_000) - (abs(_as_int(observer_latitude_mdeg, 0)) // 2),
        8_000,
        80_000,
    )
    rows = []
    for index in range(sample_count):
        azimuth = (index * 360_000) // sample_count
        angular_gap = abs(azimuth - center_azimuth)
        angular_gap = min(angular_gap, 360_000 - angular_gap)
        if angular_gap >= band_half_width:
            intensity = 0
        else:
            intensity = (peak * (band_half_width - angular_gap)) // max(1, band_half_width)
        intensity = _clamp((intensity * (760 + contrast)) // 1000, 0, 1000)
        intensity = _clamp((intensity * proxy_alignment_permille) // 1000, 0, 1000)
        intensity = (intensity * visibility) // 1000
        if intensity <= 0:
            continue
        rows.append(
            {
                "sample_index": int(index),
                "azimuth_mdeg": int(azimuth),
                "altitude_center_mdeg": int(center_altitude),
                "band_half_width_mdeg": int(band_half_width),
                "intensity_permille": int(intensity),
                "extensions": {
                    "proxy_alignment_permille": int(proxy_alignment_permille),
                },
            }
        )
    return rows


def build_starfield_snapshot(
    *,
    universe_identity: Mapping[str, object] | None,
    observer_cell_key: Mapping[str, object] | None,
    current_tick: int,
    observer_latitude_mdeg: int,
    starfield_policy_row: Mapping[str, object] | None,
    milkyway_band_policy_row: Mapping[str, object] | None,
    galaxy_priors_row: Mapping[str, object] | None,
    galaxy_proxy_row: Mapping[str, object] | None = None,
    sky_visibility_permille: int,
) -> dict:
    universe = _as_map(universe_identity)
    policy_row = _as_map(starfield_policy_row)
    band_row = _as_map(milkyway_band_policy_row)
    galaxy_row = _as_map(galaxy_priors_row)
    if not galaxy_row:
        galaxy_rows = galaxy_priors_rows()
        galaxy_row = dict(galaxy_rows.get("priors.milkyway_stub_default") or {})
    tick_bucket = sky_tick_bucket(
        current_tick=current_tick,
        tick_bucket_size=_as_int(policy_row.get("tick_bucket_size", 1), 1),
    )
    stream_seed = _stream_seed(
        universe_identity=universe,
        observer_cell_key=observer_cell_key,
        tick_bucket=tick_bucket,
    )
    visible_star_count = _visibility_star_count(
        policy_row=policy_row,
        sky_visibility_permille=sky_visibility_permille,
    )
    stars = _build_star_rows(
        stream_seed=stream_seed,
        policy_row=policy_row,
        visible_star_count=visible_star_count,
    )
    band_rows = _build_milkyway_band_rows(
        stream_seed=stream_seed,
        policy_row=band_row,
        galaxy_priors_row=galaxy_row,
        galaxy_proxy_row=galaxy_proxy_row,
        observer_latitude_mdeg=observer_latitude_mdeg,
        tick_bucket=tick_bucket,
        sky_visibility_permille=sky_visibility_permille,
    )
    payload = {
        "tick_bucket": int(tick_bucket),
        "stream_name": "rng.view.sky.starfield",
        "stream_seed": str(stream_seed),
        "visible_star_count": int(visible_star_count),
        "star_rows": list(stars),
        "milkyway_band_rows": list(band_rows),
        "policy_id": str(policy_row.get("policy_id", "")).strip() or "stars.mvp_default",
        "milkyway_band_policy_id": str(band_row.get("policy_id", "")).strip() or "mwband.mvp_stub",
        "deterministic_fingerprint": "",
        "extensions": {
            "engine_version": EARTH_STARFIELD_GENERATOR_VERSION,
            "observer_cell_key_hash": _observer_key_hash(observer_cell_key),
            "galaxy_proxy_alignment_enabled": bool(_as_map(galaxy_proxy_row)),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
