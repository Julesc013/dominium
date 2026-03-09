"""Deterministic EARTH-5 illumination/shadow probes for replay and TestX reuse."""

from __future__ import annotations

import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.worldgen.earth.lighting import build_lighting_view_surface  # noqa: E402
from tools.worldgen.earth4_probe import (  # noqa: E402
    SKY_DAY_TICK,
    SKY_NIGHT_TICK,
    SKY_TWILIGHT_TICK,
    build_sky_fixture,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _deep_copy_map(value: Mapping[str, object] | None) -> dict:
    payload = _as_map(value)
    return {
        key: _deep_copy_map(item) if isinstance(item, Mapping) else list(item) if isinstance(item, list) else item
        for key, item in payload.items()
    }


def build_lighting_fixture(
    repo_root: str,
    *,
    current_tick: int,
    override_surface_artifact: Mapping[str, object] | None = None,
    ui_mode: str = "gui",
) -> dict:
    sky_fixture = build_sky_fixture(repo_root, current_tick=int(current_tick), ui_mode=str(ui_mode))
    surface_artifact = _deep_copy_map(override_surface_artifact) or _deep_copy_map(sky_fixture.get("observer_surface_artifact"))
    lighting_view_surface = build_lighting_view_surface(
        sky_view_artifact=_as_map(_as_map(sky_fixture.get("sky_view_surface")).get("sky_view_artifact")),
        observer_ref=_as_map(sky_fixture.get("observer_ref")),
        observer_surface_artifact=surface_artifact,
        ui_mode=str(ui_mode),
    )
    return {
        **sky_fixture,
        "observer_surface_artifact": surface_artifact,
        "lighting_view_surface": lighting_view_surface,
    }


def verify_illumination_view_replay(repo_root: str) -> dict:
    first = build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK)
    second = build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK)
    first_surface = _as_map(first.get("lighting_view_surface"))
    second_surface = _as_map(second.get("lighting_view_surface"))
    first_artifact = _as_map(first_surface.get("illumination_view_artifact"))
    second_artifact = _as_map(second_surface.get("illumination_view_artifact"))
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
        "shadow_factor": int(first_artifact.get("shadow_factor", 0) or 0),
        "surface_fingerprint": canonical_sha256(normalized_first_surface),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def illumination_report(repo_root: str) -> dict:
    first = _as_map(_as_map(build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("lighting_view_surface")).get("illumination_view_artifact"))
    second = _as_map(_as_map(build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("lighting_view_surface")).get("illumination_view_artifact"))
    return {
        "result": "complete",
        "stable": first == second,
        "ambient_intensity": int(first.get("ambient_intensity", 0) or 0),
        "sun_intensity": int(first.get("sun_intensity", 0) or 0),
        "shadow_factor": int(first.get("shadow_factor", 0) or 0),
    }


def moon_phase_report(repo_root: str) -> dict:
    first = _as_map(_as_map(build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("lighting_view_surface")).get("illumination_view_artifact"))
    second = _as_map(_as_map(build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK + 130).get("lighting_view_surface")).get("illumination_view_artifact"))
    return {
        "result": "complete",
        "tick_a": int(SKY_NIGHT_TICK),
        "tick_b": int(SKY_NIGHT_TICK + 130),
        "moon_intensity_a": int(first.get("moon_intensity", 0) or 0),
        "moon_intensity_b": int(second.get("moon_intensity", 0) or 0),
        "changed": int(first.get("moon_intensity", 0) or 0) != int(second.get("moon_intensity", 0) or 0),
    }


def horizon_shadow_report(repo_root: str) -> dict:
    baseline_fixture = build_lighting_fixture(repo_root, current_tick=SKY_DAY_TICK)
    baseline_artifact = _deep_copy_map(baseline_fixture.get("observer_surface_artifact"))
    exaggerated = _deep_copy_map(baseline_artifact)
    elevation = _as_map(exaggerated.get("elevation_params_ref"))
    exaggerated["elevation_params_ref"] = {
        **elevation,
        "macro_relief_permille": 980,
        "ridge_bias_permille": 980,
        "coastal_bias_permille": 0,
        "continent_mask_permille": 1000,
    }
    occluded = _as_map(
        _as_map(
            build_lighting_fixture(
                repo_root,
                current_tick=SKY_DAY_TICK,
                override_surface_artifact=exaggerated,
            ).get("lighting_view_surface")
        ).get("illumination_view_artifact")
    )
    baseline_view = _as_map(_as_map(baseline_fixture.get("lighting_view_surface")).get("illumination_view_artifact"))
    return {
        "result": "complete",
        "baseline_shadow_factor": int(baseline_view.get("shadow_factor", 0) or 0),
        "occluded_shadow_factor": int(occluded.get("shadow_factor", 0) or 0),
        "sun_intensity": int(occluded.get("sun_intensity", 0) or 0),
        "shadow_samples": list(_as_map(occluded.get("extensions")).get("shadow_samples") or []),
        "occludes_more_than_baseline": int(occluded.get("shadow_factor", 0) or 0) < int(baseline_view.get("shadow_factor", 0) or 0),
    }


def sampling_bounded_report(repo_root: str) -> dict:
    artifact = _as_map(_as_map(build_lighting_fixture(repo_root, current_tick=SKY_TWILIGHT_TICK).get("lighting_view_surface")).get("illumination_view_artifact"))
    shadow_summary = _as_map(_as_map(artifact.get("extensions")).get("shadow_summary"))
    return {
        "result": "complete",
        "sample_count": int(shadow_summary.get("sample_count", 0) or 0),
        "sampling_bounded": bool(shadow_summary.get("sampling_bounded", False)),
        "max_horizon_angle_mdeg": int(shadow_summary.get("max_horizon_angle_mdeg", 0) or 0),
    }


def lighting_hash(repo_root: str) -> str:
    surface = _as_map(build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK).get("lighting_view_surface"))
    artifact = _as_map(surface.get("illumination_view_artifact"))
    return canonical_sha256(
        {
            "artifact_fingerprint": str(artifact.get("deterministic_fingerprint", "")).strip(),
            "summary": dict(_as_map(surface.get("presentation")).get("summary") or {}),
            "shadow_summary": dict(_as_map(_as_map(artifact.get("extensions")).get("shadow_summary"))),
        }
    )


__all__ = [
    "build_lighting_fixture",
    "horizon_shadow_report",
    "illumination_report",
    "lighting_hash",
    "moon_phase_report",
    "sampling_bounded_report",
    "verify_illumination_view_replay",
]
