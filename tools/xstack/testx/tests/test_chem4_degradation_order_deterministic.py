"""FAST test: CHEM-4 degradation order is deterministic and ordered."""

from __future__ import annotations

import sys


TEST_ID = "test_chem4_degradation_order_deterministic"
TEST_TAGS = ["fast", "chem", "degradation", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem4_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(
        repo_root=repo_root,
        seed=9300,
        species_pools=48,
        reactions=48,
        process_runs=96,
        ticks=48,
    )
    first = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        tick_count=48,
        budget_envelope_id="chem.envelope.tight",
    )
    second = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        tick_count=48,
        budget_envelope_id="chem.envelope.tight",
    )
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "CHEM stress run failed for first degradation-order fixture"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "CHEM stress run failed for second degradation-order fixture"}

    rows_a = [dict(row) for row in list(dict(first.get("extensions") or {}).get("degradation_event_rows") or []) if isinstance(row, dict)]
    rows_b = [dict(row) for row in list(dict(second.get("extensions") or {}).get("degradation_event_rows") or []) if isinstance(row, dict)]
    if not rows_a:
        return {"status": "fail", "message": "expected deterministic CHEM degradation rows under tight envelope"}
    if rows_a != rows_b:
        return {"status": "fail", "message": "CHEM degradation rows drifted across equivalent runs"}

    by_scope = {}
    for row in rows_a:
        scope = "{}::{}".format(int(row.get("tick", 0) or 0), str(row.get("run_id", "")))
        by_scope.setdefault(scope, [])
        by_scope[scope].append(int(row.get("step_order", 999) or 999))
    for values in by_scope.values():
        if list(values) != sorted(values):
            return {"status": "fail", "message": "CHEM degradation step_order is not non-decreasing per tick/run scope"}

    assertions = dict(first.get("assertions") or {})
    if not bool(assertions.get("degradation_order_deterministic", False)):
        return {"status": "fail", "message": "CHEM stress harness did not report deterministic degradation order"}
    return {"status": "pass", "message": "CHEM degradation order deterministic and ordered"}

