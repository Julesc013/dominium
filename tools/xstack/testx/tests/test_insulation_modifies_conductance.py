"""FAST test: THERM-2 insulation factor modifies effective conductance deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_insulation_modifies_conductance"
TEST_TAGS = ["fast", "thermal", "insulation", "models"]


def _edge_row(result: dict) -> dict:
    rows = [dict(row) for row in list(result.get("edge_status_rows") or []) if isinstance(row, dict)]
    return rows[0] if rows else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    baseline_graph = build_thermal_graph(source_energy=5000, sink_energy=0, source_capacity=100, sink_capacity=100, conductance_value=120)
    insulated_graph = copy.deepcopy(baseline_graph)
    insulated_graph["edges"][0]["payload"]["extensions"] = {"insulation_factor_permille": 500}

    baseline = solve_thermal_network_t1(
        graph_row=baseline_graph,
        current_tick=5,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    insulated = solve_thermal_network_t1(
        graph_row=insulated_graph,
        current_tick=5,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    if str(baseline.get("mode", "")) != "T1" or str(insulated.get("mode", "")) != "T1":
        return {"status": "fail", "message": "expected T1 solve for baseline and insulated fixtures"}

    base_edge = _edge_row(baseline)
    ins_edge = _edge_row(insulated)
    if not base_edge or not ins_edge:
        return {"status": "fail", "message": "missing edge status rows for insulation fixture"}

    base_effective = int(base_edge.get("effective_conductance_value", 0))
    ins_effective = int(ins_edge.get("effective_conductance_value", 0))
    if base_effective <= 0:
        return {"status": "fail", "message": "baseline effective conductance should be positive"}
    if ins_effective != (base_effective // 2):
        return {
            "status": "fail",
            "message": "insulation factor did not deterministically halve effective conductance (base={}, insulated={})".format(
                base_effective, ins_effective
            ),
        }

    base_transfer = int(base_edge.get("heat_transfer", 0))
    ins_transfer = int(ins_edge.get("heat_transfer", 0))
    if ins_transfer >= base_transfer:
        return {"status": "fail", "message": "insulated transfer should be lower than baseline transfer"}
    return {"status": "pass", "message": "insulation deterministically modifies effective conductance and transfer"}

