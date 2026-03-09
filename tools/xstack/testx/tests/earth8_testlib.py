"""Shared deterministic EARTH-8 water fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def water_view_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth8_probe import verify_water_view_replay as _report

    return _report(repo_root)


def river_mask_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth8_probe import river_mask_report as _report

    return _report(repo_root)


def tide_offset_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth8_probe import tide_offset_report as _report

    return _report(repo_root)


def earth_water_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth8_probe import water_hash

    return str(water_hash(repo_root)).strip()
