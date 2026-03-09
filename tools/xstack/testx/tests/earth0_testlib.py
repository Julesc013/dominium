"""Shared deterministic EARTH-0 fixture helpers for TestX."""

from __future__ import annotations

import sys


EARTH_FIXTURE_TICK = 4096
EARTH_HASH_TICK = 0
EARTH_FIXTURE_CHART_ID = "chart.atlas.north"
EARTH_FIXTURE_INDEX = [16, 6]
EARTH_SEASONAL_INDEX = [16, 2]


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def generate_earth_tile_fixture(repo_root: str, *, current_tick: int = EARTH_FIXTURE_TICK) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth0_probe import build_earth_probe_context, generate_earth_probe_tile

    context = build_earth_probe_context(repo_root)
    return generate_earth_probe_tile(
        context,
        chart_id=EARTH_FIXTURE_CHART_ID,
        index_tuple=EARTH_FIXTURE_INDEX,
        refinement_level=1,
        current_tick=int(current_tick),
    )


def generate_earth_surface_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth0_probe import verify_earth_surface_consistency

    return verify_earth_surface_consistency(repo_root)


def earth_surface_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth0_probe import earth_surface_sample_hash, sample_earth_surface

    return earth_surface_sample_hash(sample_earth_surface(repo_root, current_tick=EARTH_HASH_TICK))


def generate_earth_seasonal_pair(repo_root: str) -> tuple[dict, dict]:
    _ensure_repo_root(repo_root)
    from tools.worldgen.earth0_probe import (
        EARTH_SEASON_TICK_A,
        EARTH_SEASON_TICK_B,
        build_earth_probe_context,
        generate_earth_probe_tile,
    )

    context = build_earth_probe_context(repo_root)
    first = generate_earth_probe_tile(
        context,
        chart_id=EARTH_FIXTURE_CHART_ID,
        index_tuple=EARTH_SEASONAL_INDEX,
        refinement_level=1,
        current_tick=int(EARTH_SEASON_TICK_A),
    )
    second = generate_earth_probe_tile(
        context,
        chart_id=EARTH_FIXTURE_CHART_ID,
        index_tuple=EARTH_SEASONAL_INDEX,
        refinement_level=1,
        current_tick=int(EARTH_SEASON_TICK_B),
    )
    return first, second
