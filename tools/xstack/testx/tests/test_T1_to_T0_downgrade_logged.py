"""FAST test: THERM-1 deterministically downgrades to T0 and logs the downgrade."""

from __future__ import annotations

import sys


TEST_ID = "test_T1_to_T0_downgrade_logged"
TEST_TAGS = ["fast", "thermal", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph()
    solved = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=5,
        max_processed_edges=0,
        max_cost_units=1,
    )
    if str(solved.get("mode", "")) != "T0":
        return {"status": "fail", "message": "expected deterministic T1->T0 fallback under edge/cost budget pressure"}
    decision_rows = [dict(row) for row in list(solved.get("decision_log_rows") or []) if isinstance(row, dict)]
    if not decision_rows:
        return {"status": "fail", "message": "downgrade must emit decision_log_rows"}
    reason_codes = set(str(row.get("reason_code", "")).strip() for row in decision_rows)
    if "degrade.therm.t1_budget" not in reason_codes:
        return {"status": "fail", "message": "expected degrade.therm.t1_budget reason_code in downgrade decision log"}
    return {"status": "pass", "message": "T1->T0 downgrade logged deterministically"}
