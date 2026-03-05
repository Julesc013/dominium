"""Shared SYS-8 stress/replay TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Mapping


def make_stress_scenario(
    *,
    repo_root: str,
    seed: int = 88017,
    system_count: int = 64,
    tick_horizon: int = 16,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_generate_sys_stress import generate_sys_stress_scenario

    return generate_sys_stress_scenario(
        seed=int(seed),
        system_count=int(system_count),
        nested_size=12,
        tick_horizon=int(tick_horizon),
        shard_count=4,
        player_count=2,
        roi_width=12,
        time_warp_batch_size=4,
    )


def run_stress_report(
    *,
    repo_root: str,
    scenario: Mapping[str, object],
    max_expands_per_tick: int = 8,
    max_collapses_per_tick: int = 16,
    max_macro_capsules_per_tick: int = 32,
    max_health_updates_per_tick: int = 32,
    max_reliability_evals_per_tick: int = 32,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.system.tool_run_sys_stress import run_sys_stress

    return run_sys_stress(
        scenario=copy.deepcopy(dict(scenario or {})),
        tick_count=int(max(1, int(dict(scenario or {}).get("tick_horizon", 16) or 16))),
        max_expands_per_tick=int(max_expands_per_tick),
        max_collapses_per_tick=int(max_collapses_per_tick),
        max_macro_capsules_per_tick=int(max_macro_capsules_per_tick),
        max_health_updates_per_tick=int(max_health_updates_per_tick),
        max_reliability_evals_per_tick=int(max_reliability_evals_per_tick),
    )
