"""FAST test: POLL-3 degradation order is deterministic and ordered under tight budgets."""

from __future__ import annotations

import sys


TEST_ID = "test_poll3_degradation_order_deterministic"
TEST_TAGS = ["fast", "pollution", "poll3", "degradation", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.poll3_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=9301)
    first = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        budget_envelope_id="poll.envelope.tight",
    )
    second = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        budget_envelope_id="poll.envelope.tight",
    )
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first POLL-3 tight-envelope stress run failed"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second POLL-3 tight-envelope stress run failed"}

    rows_a = [dict(row) for row in list(dict(first.get("extensions") or {}).get("pollution_degradation_event_rows") or []) if isinstance(row, dict)]
    rows_b = [dict(row) for row in list(dict(second.get("extensions") or {}).get("pollution_degradation_event_rows") or []) if isinstance(row, dict)]
    if rows_a != rows_b:
        return {"status": "fail", "message": "POLL-3 degradation rows drifted across equivalent runs"}

    policy_order = list((dict(first.get("metrics") or {})).get("degradation_policy_order") or [])
    expected_order = [
        "degrade.pollution.dispersion_tick_bucket",
        "degrade.pollution.cell_budget",
        "degrade.pollution.exposure_subject_budget",
        "degrade.pollution.compliance_delay",
        "degrade.pollution.measurement_refusal",
    ]
    if policy_order != expected_order:
        return {"status": "fail", "message": "POLL-3 degradation policy order mismatch"}

    if not rows_a:
        return {"status": "fail", "message": "expected POLL-3 degradation rows under tight envelope"}

    return {"status": "pass", "message": "POLL-3 degradation order deterministic under tight envelope"}
