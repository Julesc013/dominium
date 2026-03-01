"""FAST test: MECH-1 plastic strain accumulates under sustained high stress."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.plastic_strain_accumulates"
TEST_TAGS = ["fast", "mechanics", "deformation"]


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
        row["applied_force"] = 900
    policy = policy_context()

    first = evaluate_structural_graphs(
        structural_graph_rows=copy.deepcopy(state.get("structural_graphs")),
        structural_node_rows=nodes,
        structural_edge_rows=copy.deepcopy(state.get("structural_edges")),
        current_tick=11,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy.get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy.get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy.get("stacking_policy_registry")),
    )
    second = evaluate_structural_graphs(
        structural_graph_rows=copy.deepcopy(first.get("structural_graph_rows")),
        structural_node_rows=copy.deepcopy(first.get("structural_node_rows")),
        structural_edge_rows=copy.deepcopy(first.get("structural_edge_rows")),
        current_tick=12,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy.get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy.get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy.get("stacking_policy_registry")),
    )
    first_nodes = [dict(row) for row in list(first.get("structural_node_rows") or []) if isinstance(row, dict)]
    second_nodes = [dict(row) for row in list(second.get("structural_node_rows") or []) if isinstance(row, dict)]
    if (not first_nodes) or (not second_nodes):
        return {"status": "fail", "message": "missing structural nodes for plastic strain check"}
    first_plastic = int(first_nodes[0].get("plastic_strain", 0))
    second_plastic = int(second_nodes[0].get("plastic_strain", 0))
    if second_plastic <= first_plastic:
        return {"status": "fail", "message": "plastic_strain did not accumulate across repeated high-stress ticks"}
    return {"status": "pass", "message": "plastic strain accumulates deterministically"}

