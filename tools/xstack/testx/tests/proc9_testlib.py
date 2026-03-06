"""Shared PROC-9 stress/proof TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Mapping


def make_stress_scenario(
    *,
    repo_root: str,
    seed: int = 99101,
    stabilized_count: int = 160,
    exploration_count: int = 48,
    drifting_count: int = 32,
    research_campaign_count: int = 24,
    software_run_count: int = 40,
    tick_horizon: int = 32,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_generate_proc_stress import generate_proc_stress_scenario

    return generate_proc_stress_scenario(
        seed=int(seed),
        stabilized_count=int(stabilized_count),
        exploration_count=int(exploration_count),
        drifting_count=int(drifting_count),
        research_campaign_count=int(research_campaign_count),
        software_run_count=int(software_run_count),
        tick_horizon=int(tick_horizon),
    )


def run_stress_report(
    *,
    repo_root: str,
    scenario: Mapping[str, object],
    max_micro_steps_per_tick: int = 32,
    max_total_tasks_per_tick: int = 96,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_run_proc_stress import run_proc_stress

    return run_proc_stress(
        repo_root=repo_root,
        scenario=copy.deepcopy(dict(scenario or {})),
        tick_count=int(max(1, int(dict(scenario or {}).get("tick_horizon", 32) or 32))),
        max_micro_steps_per_tick=int(max_micro_steps_per_tick),
        max_total_tasks_per_tick=int(max_total_tasks_per_tick),
    )
