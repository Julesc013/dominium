"""Shared deterministic EARTH-4 sky/starfield fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def sun_direction_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth4_probe import sun_direction_report as _report

    return _report(repo_root)


def sky_gradient_transition_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth4_probe import sky_gradient_transition_report as _report

    return _report(repo_root)


def starfield_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth4_probe import starfield_report as _report

    return _report(repo_root)


def replay_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth4_probe import verify_sky_view_replay as _report

    return _report(repo_root)


def earth_sky_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth4_probe import sky_hash as _report

    return str(_report(repo_root)).strip()
