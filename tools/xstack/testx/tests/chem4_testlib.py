"""Shared CHEM-4 stress/replay fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def make_stress_scenario(
    *,
    repo_root: str,
    seed: int,
    species_pools: int,
    reactions: int,
    process_runs: int,
    ticks: int,
) -> dict:
    _ensure_repo_path(repo_root)
    from tools.chem.tool_generate_chem_stress import generate_chem_stress_scenario

    return generate_chem_stress_scenario(
        seed=int(seed),
        species_pools=int(species_pools),
        reactions=int(reactions),
        process_runs=int(process_runs),
        ticks=int(ticks),
        repo_root=repo_root,
    )


def run_stress_report(
    *,
    repo_root: str,
    scenario: dict,
    tick_count: int,
    budget_envelope_id: str,
) -> dict:
    _ensure_repo_path(repo_root)
    from tools.chem.tool_run_chem_stress import _envelope_defaults, run_chem_stress_scenario

    defaults = _envelope_defaults(str(budget_envelope_id))
    return run_chem_stress_scenario(
        scenario=dict(scenario or {}),
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_envelope_id),
        max_reaction_evaluations_per_tick=int(defaults["max_reaction_evaluations_per_tick"]),
        max_cost_units_per_tick=int(defaults["max_cost_units_per_tick"]),
        max_model_cost_units_per_tick=int(defaults["max_model_cost_units_per_tick"]),
        base_tick_stride=int(defaults["base_tick_stride"]),
        max_emission_events_per_tick=int(defaults["max_emission_events_per_tick"]),
    )

