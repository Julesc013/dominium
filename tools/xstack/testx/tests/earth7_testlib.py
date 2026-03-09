"""Shared deterministic EARTH-7 wind fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def wind_field_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth7_probe import verify_wind_window_replay as _report

    return _report(repo_root)


def latitude_band_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth7_probe import wind_latitude_band_report as _report

    return _report(repo_root)


def seasonal_shift_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth7_probe import wind_seasonal_shift_report as _report

    return _report(repo_root)


def poll_advection_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth7_probe import poll_advection_bias_report as _report

    return _report(repo_root)


def earth_wind_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth7_probe import run_wind_tick_fixture

    return str(
        run_wind_tick_fixture(
            repo_root,
            current_tick=88,
            last_processed_tick=None,
            max_tiles_per_update=128,
        ).get("overlay_hash", "")
    ).strip()
