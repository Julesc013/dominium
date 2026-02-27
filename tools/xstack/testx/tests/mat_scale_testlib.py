"""Shared MAT-10 scale stress fixtures."""

from __future__ import annotations

import copy
from typing import Dict


def base_scenario(
    *,
    seed: int = 424242,
    factory_complex_count: int = 24,
    logistics_node_count: int = 96,
    active_project_count: int = 80,
    player_count: int = 64,
) -> dict:
    from src.materials.performance.mat_scale_engine import default_factory_planet_scenario

    return default_factory_planet_scenario(
        seed=int(seed),
        factory_complex_count=int(factory_complex_count),
        logistics_node_count=int(logistics_node_count),
        active_project_count=int(active_project_count),
        player_count=int(player_count),
    )


def with_budget(
    scenario: dict,
    *,
    max_solver_cost_units_per_tick: int,
    max_inspection_cost_units_per_tick: int,
    max_micro_parts_per_roi: int,
) -> dict:
    out = copy.deepcopy(dict(scenario or {}))
    envelopes = [dict(row) for row in list(out.get("budget_envelopes") or []) if isinstance(row, dict)]
    if not envelopes:
        envelopes = [{}]
    first = dict(envelopes[0])
    first["envelope_id"] = str(first.get("envelope_id", "budget.factory_planet.default")).strip() or "budget.factory_planet.default"
    first["max_solver_cost_units_per_tick"] = int(max(0, int(max_solver_cost_units_per_tick)))
    first["max_inspection_cost_units_per_tick"] = int(max(0, int(max_inspection_cost_units_per_tick)))
    first["max_micro_parts_per_roi"] = int(max(1, int(max_micro_parts_per_roi)))
    envelopes[0] = first
    out["budget_envelopes"] = envelopes
    return out


def with_workload_overrides(scenario: dict, overrides: Dict[str, int | str]) -> dict:
    out = copy.deepcopy(dict(scenario or {}))
    workload = dict(out.get("workload_template") or {})
    for key, value in sorted(dict(overrides or {}).items(), key=lambda item: str(item[0])):
        workload[str(key)] = value
    out["workload_template"] = workload
    return out


def run_report(
    *,
    scenario: dict,
    tick_count: int = 16,
    multiplayer_policy_id: str = "policy.net.server_authoritative",
) -> dict:
    from src.materials.performance.mat_scale_engine import run_stress_simulation

    return run_stress_simulation(
        scenario_row=dict(scenario or {}),
        tick_count=int(max(0, int(tick_count))),
        budget_envelope_id="budget.factory_planet.default",
        arbitration_policy_id="arb.equal_share.deterministic",
        multiplayer_policy_id=str(multiplayer_policy_id),
        strict_budget=False,
    )
