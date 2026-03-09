"""Shared deterministic EARTH-3 tide fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def lunar_phase_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth3_probe import lunar_phase_report as _report

    return _report(repo_root)


def tide_day_delta_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth3_probe import tide_day_delta_report as _report

    return _report(repo_root)


def inland_damping_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth3_probe import inland_damping_report as _report

    return _report(repo_root)


def bucket_update_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth3_probe import verify_tide_window_replay as _report

    return _report(repo_root)


def earth_tide_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth3_probe import run_tide_tick_fixture

    return str(run_tide_tick_fixture(repo_root).get("overlay_hash", "")).strip()
