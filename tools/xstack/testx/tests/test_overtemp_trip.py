"""FAST test: THERM-1 overtemperature emits hazard and safety trip events."""

from __future__ import annotations

import sys


TEST_ID = "test_overtemp_trip"
TEST_TAGS = ["fast", "thermal", "safety"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = build_thermal_graph(source_energy=20_000, sink_energy=0, source_capacity=50, sink_capacity=100)
    solved = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=77,
        overtemp_threshold_default=50,
        max_processed_edges=64,
        max_cost_units=4096,
    )
    hazards = [dict(row) for row in list(solved.get("hazard_rows") or []) if isinstance(row, dict)]
    events = [dict(row) for row in list(solved.get("safety_event_rows") or []) if isinstance(row, dict)]
    if not any(str(row.get("hazard_type_id", "")).strip() == "hazard.overheat" for row in hazards):
        return {"status": "fail", "message": "expected hazard.overheat row for overtemperature node"}
    if not any(str(row.get("pattern_id", "")).strip() == "safety.overtemp_trip" for row in events):
        return {"status": "fail", "message": "expected safety.overtemp_trip event for overtemperature node"}
    return {"status": "pass", "message": "overtemp hazard and safety trip emitted"}
