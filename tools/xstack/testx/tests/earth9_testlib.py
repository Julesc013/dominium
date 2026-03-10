"""Shared deterministic EARTH-9 stress and regression fixtures for TestX."""

from __future__ import annotations

import json
import os
import sys
from functools import lru_cache


def _ensure_repo_root(repo_root: str) -> str:
    normalized = os.path.normpath(os.path.abspath(repo_root))
    if normalized not in sys.path:
        sys.path.insert(0, normalized)
    return normalized


@lru_cache(maxsize=4)
def _scenario(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.earth.earth9_stress_common import generate_earth_mvp_stress_scenario

    return generate_earth_mvp_stress_scenario(repo_root=normalized)


@lru_cache(maxsize=4)
def _stress_report(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.earth.earth9_stress_common import verify_earth_mvp_stress_scenario

    return verify_earth_mvp_stress_scenario(repo_root=normalized, scenario=_scenario(normalized))


@lru_cache(maxsize=4)
def _view_replay(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.earth.earth9_stress_common import replay_earth_view_window

    return replay_earth_view_window(repo_root=normalized, scenario=_scenario(normalized))


@lru_cache(maxsize=4)
def _physics_replay(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.earth.earth9_stress_common import replay_earth_physics_window

    return replay_earth_physics_window(repo_root=normalized)


@lru_cache(maxsize=4)
def _baseline(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    baseline_path = os.path.join(normalized, "data", "regression", "earth_mvp_baseline.json")
    with open(baseline_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def earth_stress_scenario(repo_root: str) -> dict:
    return dict(_scenario(_ensure_repo_root(repo_root)))


def earth_stress_report(repo_root: str) -> dict:
    return dict(_stress_report(_ensure_repo_root(repo_root)))


def earth_view_replay_report(repo_root: str) -> dict:
    return dict(_view_replay(_ensure_repo_root(repo_root)))


def earth_physics_replay_report(repo_root: str) -> dict:
    return dict(_physics_replay(_ensure_repo_root(repo_root)))


def earth_regression_baseline(repo_root: str) -> dict:
    return dict(_baseline(_ensure_repo_root(repo_root)))


def earth_timewarp_report(repo_root: str) -> dict:
    report = earth_stress_report(repo_root)
    subsystems = dict(report.get("subsystem_reports") or {})
    return {
        "climate_year_delta": dict(subsystems.get("climate_year_delta") or {}),
        "polar_daylight": dict(subsystems.get("polar_daylight") or {}),
        "tide_day_delta": dict(subsystems.get("tide_day_delta") or {}),
        "lighting_moon_phase": dict(subsystems.get("lighting_moon_phase") or {}),
        "assertions": dict(report.get("assertions") or {}),
    }


def earth_sky_consistency_report(repo_root: str) -> dict:
    report = earth_stress_report(repo_root)
    subsystems = dict(report.get("subsystem_reports") or {})
    return {
        "sky_transition": dict(subsystems.get("sky_transition") or {}),
        "view_fingerprints": dict(dict(report.get("view_window") or {}).get("proof_summary") or {}),
        "assertions": dict(report.get("assertions") or {}),
    }


def earth_geometry_edit_report(repo_root: str) -> dict:
    report = earth_stress_report(repo_root)
    return {
        "hydrology_local_edit": dict(dict(report.get("subsystem_reports") or {}).get("hydrology_local_edit") or {}),
        "geometry_edit_report": dict(dict(report.get("physics_window") or {}).get("geometry_edit_report") or {}),
        "assertions": dict(report.get("assertions") or {}),
    }


def earth_view_fingerprint_report(repo_root: str) -> dict:
    return {
        "baseline": earth_regression_baseline(repo_root),
        "view_replay": earth_view_replay_report(repo_root),
    }


def earth_mvp_hash(repo_root: str) -> str:
    report = earth_stress_report(repo_root)
    return str(dict(report.get("proof_summary") or {}).get("cross_platform_determinism_hash", "")).strip()
