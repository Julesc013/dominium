"""Shared deterministic EARTH-1 hydrology fixtures for TestX."""

from __future__ import annotations

import sys


HYDROLOGY_HASH_TICK = 0


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def generate_hydrology_window_fixture(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import generate_hydrology_window_fixture

    return generate_hydrology_window_fixture(repo_root)


def verify_hydrology_window_replay_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import verify_hydrology_window_replay

    return verify_hydrology_window_replay(repo_root)


def verify_window_monotonicity_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import verify_window_monotonicity

    return verify_window_monotonicity(repo_root)


def verify_river_threshold_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import verify_river_threshold_fixture

    return verify_river_threshold_fixture(repo_root)


def verify_local_edit_hydrology_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import verify_local_edit_hydrology_update

    return verify_local_edit_hydrology_update(repo_root)


def earth_hydrology_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth1_probe import earth_hydrology_hash as _hash_rows
    from tools.worldgen.earth1_probe import sample_earth_hydrology

    return _hash_rows(sample_earth_hydrology(repo_root, current_tick=HYDROLOGY_HASH_TICK))
