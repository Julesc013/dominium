"""Shared deterministic EARTH-2 climate fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def orbit_phase_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth2_probe import orbit_phase_report as _report

    return _report(repo_root)


def climate_year_delta_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth2_probe import climate_year_delta_report as _report

    return _report(repo_root)


def polar_daylight_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth2_probe import polar_daylight_report as _report

    return _report(repo_root)


def bucket_update_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth2_probe import verify_climate_window_replay as _report

    return _report(repo_root)


def earth_climate_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth2_probe import run_climate_tick_fixture

    return str(run_climate_tick_fixture(repo_root).get("overlay_hash", "")).strip()
