"""FAST test: MECH-1 fracture trigger emits deterministic fracture edge ids."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.fracture_trigger"
TEST_TAGS = ["fast", "mechanics", "hazard"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mechanics import evaluate_structural_graphs
    from tools.xstack.testx.tests.mechanics_testlib import base_state, policy_context

    state = base_state()
    nodes = copy.deepcopy(state.get("structural_nodes") or [])
    for row in nodes:
        if not isinstance(row, dict):
            continue
        row["applied_force"] = 1200
    result = evaluate_structural_graphs(
        structural_graph_rows=copy.deepcopy(state.get("structural_graphs")),
        structural_node_rows=nodes,
        structural_edge_rows=copy.deepcopy(state.get("structural_edges")),
        current_tick=9,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy_context().get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy_context().get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy_context().get("stacking_policy_registry")),
    )
    fracture_ids = sorted(str(item).strip() for item in list(result.get("fracture_edge_ids") or []) if str(item).strip())
    if fracture_ids != ["structural.edge.ab"]:
        return {"status": "fail", "message": "expected fracture edge ['structural.edge.ab'], got {}".format(fracture_ids)}
    return {"status": "pass", "message": "fracture trigger deterministic"}

