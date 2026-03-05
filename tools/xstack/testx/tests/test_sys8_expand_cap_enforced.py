"""FAST test: SYS-8 expand cap remains enforced under budget pressure."""

from __future__ import annotations

import sys


TEST_ID = "test_expand_cap_enforced_sys8"
TEST_TAGS = ["fast", "system", "sys8", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys8_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=88037)
    report = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        max_expands_per_tick=2,
        max_collapses_per_tick=8,
        max_macro_capsules_per_tick=20,
        max_health_updates_per_tick=16,
        max_reliability_evals_per_tick=16,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-8 stress report did not complete under tight expand cap"}

    assertions = dict(report.get("assertions") or {})
    if bool(assertions.get("bounded_expands_per_tick")) is not True:
        return {"status": "fail", "message": "SYS-8 bounded_expands_per_tick assertion failed"}

    metrics = dict(report.get("metrics") or {})
    expands = [int(item) for item in list(metrics.get("expand_count_per_tick") or [])]
    if any(value > 2 for value in expands):
        return {"status": "fail", "message": "SYS-8 observed expand count exceeded configured cap"}
    return {"status": "pass", "message": "SYS-8 expand cap enforced deterministically"}
