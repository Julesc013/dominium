"""FAST test: MECH-1 stress ratio uses deterministic load/max_load calculation."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.stress_ratio_calculation"
TEST_TAGS = ["fast", "mechanics"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from mechanics import evaluate_structural_graphs
    from tools.xstack.testx.tests.mechanics_testlib import base_state, policy_context

    state = base_state()
    rows = copy.deepcopy(state.get("structural_nodes") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        row["applied_force"] = 500
        row["applied_torque"] = 0
    result = evaluate_structural_graphs(
        structural_graph_rows=copy.deepcopy(state.get("structural_graphs")),
        structural_node_rows=rows,
        structural_edge_rows=copy.deepcopy(state.get("structural_edges")),
        current_tick=4,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy_context().get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy_context().get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy_context().get("stacking_policy_registry")),
    )
    edge_rows = [dict(row) for row in list(result.get("structural_edge_rows") or []) if isinstance(row, dict)]
    if not edge_rows:
        return {"status": "fail", "message": "no structural edge rows produced"}
    ratio = int(edge_rows[0].get("stress_ratio_permille", -1))
    if ratio != 1000:
        return {"status": "fail", "message": "expected stress_ratio_permille=1000, got {}".format(ratio)}
    return {"status": "pass", "message": "stress ratio calculation stable"}

