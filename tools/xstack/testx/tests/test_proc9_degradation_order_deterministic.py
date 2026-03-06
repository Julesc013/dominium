"""FAST test: PROC-9 deterministic degradation ordering under tight budget."""

from __future__ import annotations

import sys


TEST_ID = "test_degradation_order_deterministic_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "degrade", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(
        repo_root=repo_root,
        seed=99141,
        stabilized_count=180,
        exploration_count=120,
        drifting_count=64,
        research_campaign_count=80,
        software_run_count=120,
        tick_horizon=40,
    )
    first = proc9_testlib.run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        max_micro_steps_per_tick=12,
        max_total_tasks_per_tick=28,
    )
    second = proc9_testlib.run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        max_micro_steps_per_tick=12,
        max_total_tasks_per_tick=28,
    )
    if str(first.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "first degraded stress run did not pass"}
    if str(second.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "second degraded stress run did not pass"}

    if dict(first.get("degradation_summary") or {}) != dict(second.get("degradation_summary") or {}):
        return {"status": "fail", "message": "degradation summary drifted across deterministic runs"}
    if list(first.get("degradation_order") or []) != list(second.get("degradation_order") or []):
        return {"status": "fail", "message": "degradation order drifted across deterministic runs"}
    return {"status": "pass", "message": "PROC-9 degradation order deterministic"}
