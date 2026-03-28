"""FAST test: THERM-3 ambient evaluation degrades deterministically under budget pressure."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_budget_degrade_ambient_eval"
TEST_TAGS = ["fast", "thermal", "budget", "determinism"]


def _configure_boundary_radiator(graph: dict) -> dict:
    out = copy.deepcopy(graph)
    for node in list(out.get("nodes") or []):
        payload = dict(node.get("payload") or {})
        ext = dict(payload.get("extensions") or {})
        ext["boundary_to_ambient"] = True
        ext["ambient_coupling_coefficient"] = 420
        ext["insulation_factor_permille"] = 1000
        if str(node.get("node_id", "")).strip() == "node.therm.source":
            payload["node_kind"] = "radiator"
            ext["base_conductance"] = 320
            ext["forced_cooling_multiplier"] = 1800
            ext["forced_cooling_on"] = True
            ext["radiator_profile_id"] = "radiator.forced_basic"
        payload["extensions"] = ext
        node["payload"] = payload
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    graph = _configure_boundary_radiator(
        build_thermal_graph(source_energy=7000, sink_energy=2200, conductance_value=20)
    )
    result = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=520,
        ambient_temperature=8,
        max_processed_edges=64,
        max_cost_units=4,
        ambient_eval_stride=1,
    )
    if str(result.get("mode", "")) != "T1":
        return {"status": "fail", "message": "expected T1 solve; test targets ambient sub-budget degradation"}
    deferred = int(result.get("ambient_deferred_count", 0) or 0)
    stride = int(result.get("ambient_eval_stride", 1) or 1)
    if deferred <= 0:
        return {"status": "fail", "message": "expected deferred ambient/radiator bindings under tight budget"}
    if stride <= 1:
        return {"status": "fail", "message": "expected ambient evaluation stride increase under budget pressure"}
    decision_rows = [dict(row) for row in list(result.get("decision_log_rows") or []) if isinstance(row, dict)]
    reason_codes = {str(row.get("reason_code", "")).strip() for row in decision_rows}
    if "degrade.therm.ambient_budget" not in reason_codes:
        return {"status": "fail", "message": "expected ambient budget degradation to be logged"}
    return {"status": "pass", "message": "ambient budget degradation logged deterministically"}

