"""Shared POLL-3 stress/replay TestX fixtures."""

from __future__ import annotations

import copy
import sys


def make_stress_scenario(
    *,
    repo_root: str,
    seed: int = 9301,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.pollution.tool_generate_poll_stress import generate_poll_stress_scenario

    return generate_poll_stress_scenario(
        seed=int(seed),
        region_count=3,
        cells_per_region=9,
        subject_count=36,
        tick_horizon=24,
        emissions_per_tick=3,
        measurements_per_tick=1,
        compliance_interval_ticks=4,
        include_wind_field=False,
        repo_root=repo_root,
    )


def run_stress_report(
    *,
    repo_root: str,
    scenario: dict,
    budget_envelope_id: str = "poll.envelope.standard",
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.pollution.tool_run_poll_stress import _envelope_defaults, run_poll_stress_scenario

    defaults = _envelope_defaults(str(budget_envelope_id))
    return run_poll_stress_scenario(
        scenario=copy.deepcopy(dict(scenario or {})),
        tick_count=24,
        budget_envelope_id=str(budget_envelope_id),
        max_compute_units_per_tick=int(defaults["max_compute_units_per_tick"]),
        dispersion_tick_stride_base=int(defaults["dispersion_tick_stride_base"]),
        max_cell_updates_per_tick=int(defaults["max_cell_updates_per_tick"]),
        max_subject_updates_per_tick=int(defaults["max_subject_updates_per_tick"]),
        max_compliance_reports_per_tick=int(defaults["max_compliance_reports_per_tick"]),
        max_measurements_per_tick=int(defaults["max_measurements_per_tick"]),
    )

