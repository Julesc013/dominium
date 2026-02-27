"""FAST test: MAT-10 multiplayer inspection arbitration uses deterministic equal-share budgets."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.multiplayer_equal_share_arbitration"
TEST_TAGS = ["fast", "materials", "mat10", "multiplayer", "arbitration"]


def _first_tick_shares(report: dict) -> list[int]:
    ticks = [dict(row) for row in list(report.get("per_tick_reports") or []) if isinstance(row, dict)]
    if not ticks:
        return []
    rows = [dict(row) for row in list(ticks[0].get("player_inspection_reports") or []) if isinstance(row, dict)]
    return [
        int(row.get("budget_share_units", 0) or 0)
        for row in sorted(rows, key=lambda item: str(item.get("player_id", "")))
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.mat_scale_testlib import (
        base_scenario,
        run_report,
        with_budget,
        with_workload_overrides,
    )

    scenario = base_scenario(seed=739, factory_complex_count=9, logistics_node_count=36, active_project_count=22, player_count=9)
    scenario = with_budget(
        scenario,
        max_solver_cost_units_per_tick=2_000,
        max_inspection_cost_units_per_tick=100,
        max_micro_parts_per_roi=80,
    )
    scenario = with_workload_overrides(
        scenario,
        {"inspection_desired_fidelity": "meso", "inspection_history_window_ticks": 3},
    )
    policies = (
        "policy.net.lockstep",
        "policy.net.server_authoritative",
        "policy.net.srz_hybrid",
    )
    baseline_shares = None
    for policy_id in policies:
        report = run_report(scenario=scenario, tick_count=6, multiplayer_policy_id=policy_id)
        shares = _first_tick_shares(report)
        if not shares:
            return {"status": "fail", "message": "missing first-tick player budget shares for {}".format(policy_id)}
        if sum(shares) != 100:
            return {"status": "fail", "message": "inspection shares must sum to envelope max for {}".format(policy_id)}
        if max(shares) - min(shares) > 1:
            return {"status": "fail", "message": "inspection shares must remain equal-share bounded for {}".format(policy_id)}
        if baseline_shares is None:
            baseline_shares = shares
        elif shares != baseline_shares:
            return {"status": "fail", "message": "equal-share arbitration diverged across multiplayer policies"}
    return {"status": "pass", "message": "multiplayer equal-share arbitration passed"}
