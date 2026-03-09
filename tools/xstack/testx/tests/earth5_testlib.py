"""Shared deterministic EARTH-5 lighting fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def illumination_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import illumination_report as _report

    return _report(repo_root)


def moon_phase_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import moon_phase_report as _report

    return _report(repo_root)


def horizon_shadow_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import horizon_shadow_report as _report

    return _report(repo_root)


def sampling_bounded_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import sampling_bounded_report as _report

    return _report(repo_root)


def replay_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import verify_illumination_view_replay as _report

    return _report(repo_root)


def earth_lighting_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth5_probe import lighting_hash as _report

    return str(_report(repo_root)).strip()
