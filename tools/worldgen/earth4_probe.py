"""Deterministic EARTH-4 sky/starfield probes for replay and TestX reuse."""

from __future__ import annotations

import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from geo import build_position_ref  # noqa: E402
from worldgen.earth import build_sky_view_surface  # noqa: E402
from tools.worldgen.earth0_probe import build_earth_probe_context, generate_earth_probe_tile  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


SKY_SAMPLE_CHART_ID = "chart.atlas.north"
SKY_SAMPLE_INDEX_TUPLE = [16, 6]
SKY_DAY_TICK = 0
SKY_TWILIGHT_TICK = 6
SKY_NIGHT_TICK = 8


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def build_sky_fixture(
    repo_root: str,
    *,
    current_tick: int,
    yaw_mdeg: int = 0,
    pitch_mdeg: int = 0,
    ui_mode: str = "gui",
    debug_entitlements: bool = False,
) -> dict:
    context = build_earth_probe_context(repo_root)
    tile = generate_earth_probe_tile(
        context,
        chart_id=SKY_SAMPLE_CHART_ID,
        index_tuple=SKY_SAMPLE_INDEX_TUPLE,
        refinement_level=1,
        current_tick=int(current_tick),
    )
    artifact = dict(list(tile.get("generated_surface_tile_artifact_rows") or [])[0] or {})
    artifact_ext = _as_map(artifact.get("extensions"))
    observer_ref = build_position_ref(
        object_id="camera.earth4.probe",
        frame_id="frame.surface_local",
        local_position=[0, 0, 1600],
        extensions={
            "latitude_mdeg": int(artifact_ext.get("latitude_mdeg", 0) or 0),
            "longitude_mdeg": int(artifact_ext.get("longitude_mdeg", 0) or 0),
            "geo_cell_key": dict(artifact.get("tile_cell_key") or {}),
            "source": "EARTH4-8",
        },
    )
    perceived_model = {
        "viewpoint_id": "viewpoint.earth4.probe",
        "camera_viewpoint": {
            "view_mode_id": "view.first_person.player",
            "orientation_mdeg": {"yaw": int(yaw_mdeg), "pitch": int(pitch_mdeg), "roll": 0},
        },
        "time_state": {"tick": int(current_tick)},
        "metadata": {
            "lens_type": "diegetic",
            "epistemic_policy_id": "epistemic.admin_full" if debug_entitlements else "epistemic.diegetic_default",
        },
        "truth_overlay": {"state_hash_anchor": "truth.earth4.probe"},
    }
    authority_context = {
        "authority_origin": "tool",
        "privilege_level": "observer",
        "entitlements": (
            ["entitlement.debug_view", "entitlement.observer.truth"]
            if debug_entitlements
            else []
        ),
        "epistemic_scope": {
            "scope_id": "epistemic.admin_full" if debug_entitlements else "epistemic.diegetic_default",
        },
    }
    universe_identity = {
        "universe_seed": str(_as_map(context.get("universe_identity")).get("universe_seed", "")).strip(),
        "generator_version_id": str(_as_map(context.get("universe_identity")).get("generator_version_id", "")).strip(),
        "realism_profile_id": str(context.get("realism_profile_id", "")).strip(),
    }
    surface = build_sky_view_surface(
        universe_identity=universe_identity,
        perceived_model=perceived_model,
        observer_ref=observer_ref,
        observer_surface_artifact=artifact,
        authority_context=authority_context,
        lens_profile_id="lens.fp",
        ui_mode=str(ui_mode),
        star_artifact_rows=context.get("star_artifact_rows"),
        planet_basic_artifact_rows=context.get("planet_basic_artifact_rows"),
    )
    return {
        "context": context,
        "tile": tile,
        "observer_surface_artifact": artifact,
        "observer_ref": observer_ref,
        "perceived_model": perceived_model,
        "authority_context": authority_context,
        "sky_view_surface": surface,
    }


def verify_sky_view_replay(repo_root: str) -> dict:
    first = build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK)
    second = build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK)
    first_surface = _as_map(first.get("sky_view_surface"))
    second_surface = _as_map(second.get("sky_view_surface"))
    first_artifact = _as_map(first_surface.get("sky_view_artifact"))
    second_artifact = _as_map(second_surface.get("sky_view_artifact"))
    normalized_first_surface = dict(first_surface)
    normalized_second_surface = dict(second_surface)
    normalized_first_surface.pop("cache_hit", None)
    normalized_second_surface.pop("cache_hit", None)
    stable = normalized_first_surface == normalized_second_surface and first_artifact == second_artifact
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "artifact_fingerprint": str(first_artifact.get("deterministic_fingerprint", "")).strip(),
        "cache_key": str(_as_map(first_artifact.get("extensions")).get("cache_key", "")).strip(),
        "star_count": int(len(list(first_artifact.get("star_points_ref") or []))),
        "milkyway_sample_count": int(len(list(first_artifact.get("milkyway_band_ref") or []))),
        "surface_fingerprint": canonical_sha256(normalized_first_surface),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def sun_direction_report(repo_root: str) -> dict:
    first = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    second = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    return {
        "result": "complete",
        "sun_direction_a": dict(first.get("sun_direction") or {}),
        "sun_direction_b": dict(second.get("sun_direction") or {}),
        "sun_elevation_a": int(_as_map(first.get("extensions")).get("sun_elevation_mdeg", 0) or 0),
        "sun_elevation_b": int(_as_map(second.get("extensions")).get("sun_elevation_mdeg", 0) or 0),
    }


def sky_gradient_transition_report(repo_root: str) -> dict:
    day = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    twilight = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_TWILIGHT_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    night = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    return {
        "result": "complete",
        "day": {
            "sun_elevation_mdeg": int(_as_map(day.get("extensions")).get("sun_elevation_mdeg", 0) or 0),
            "twilight_factor_permille": int(_as_map(day.get("sky_colors_ref")).get("twilight_factor_permille", 0) or 0),
            "sun_intensity_permille": int(_as_map(day.get("sky_colors_ref")).get("sun_intensity_permille", 0) or 0),
        },
        "twilight": {
            "sun_elevation_mdeg": int(_as_map(twilight.get("extensions")).get("sun_elevation_mdeg", 0) or 0),
            "twilight_factor_permille": int(_as_map(twilight.get("sky_colors_ref")).get("twilight_factor_permille", 0) or 0),
            "sun_intensity_permille": int(_as_map(twilight.get("sky_colors_ref")).get("sun_intensity_permille", 0) or 0),
        },
        "night": {
            "sun_elevation_mdeg": int(_as_map(night.get("extensions")).get("sun_elevation_mdeg", 0) or 0),
            "twilight_factor_permille": int(_as_map(night.get("sky_colors_ref")).get("twilight_factor_permille", 0) or 0),
            "sun_intensity_permille": int(_as_map(night.get("sky_colors_ref")).get("sun_intensity_permille", 0) or 0),
        },
    }


def starfield_report(repo_root: str) -> dict:
    first = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    second = _as_map(_as_map(build_sky_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("sky_view_surface")).get("sky_view_artifact"))
    first_stars = list(first.get("star_points_ref") or [])
    return {
        "result": "complete",
        "stable": first_stars == list(second.get("star_points_ref") or []),
        "star_count": int(len(first_stars)),
        "artifact_fingerprint": str(first.get("deterministic_fingerprint", "")).strip(),
    }


def sky_hash(repo_root: str) -> str:
    surface = _as_map(build_sky_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("sky_view_surface"))
    artifact = _as_map(surface.get("sky_view_artifact"))
    return canonical_sha256(
        {
            "artifact_fingerprint": str(artifact.get("deterministic_fingerprint", "")).strip(),
            "star_count": int(len(list(artifact.get("star_points_ref") or []))),
            "milkyway_sample_count": int(len(list(artifact.get("milkyway_band_ref") or []))),
            "summary": dict(_as_map(surface.get("presentation")).get("summary") or {}),
        }
    )


__all__ = [
    "SKY_DAY_TICK",
    "SKY_NIGHT_TICK",
    "SKY_TWILIGHT_TICK",
    "build_sky_fixture",
    "sky_gradient_transition_report",
    "sky_hash",
    "starfield_report",
    "sun_direction_report",
    "verify_sky_view_replay",
]
