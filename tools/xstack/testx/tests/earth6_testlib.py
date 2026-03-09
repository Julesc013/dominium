"""Shared deterministic EARTH-6 terrain-collision fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def ground_contact_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.earth6_probe import ground_contact_report as _report

    return _report(repo_root)


def slope_modifier_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.earth6_probe import slope_modifier_report as _report

    return _report(repo_root)


def geometry_edit_height_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.earth6_probe import geometry_edit_height_report as _report

    return _report(repo_root)


def verify_collision_window_replay_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.earth6_probe import verify_collision_window_replay as _report

    return _report(repo_root)


def earth_collision_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.embodiment.earth6_probe import collision_hash as _hash

    return _hash(repo_root)
