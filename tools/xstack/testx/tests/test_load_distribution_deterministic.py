"""FAST test: MECH-1 load propagation remains deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.load_distribution_deterministic"
TEST_TAGS = ["fast", "mechanics", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from mechanics import evaluate_structural_graphs
    from tools.xstack.testx.tests.mechanics_testlib import base_state, policy_context

    state = base_state()
    policy = policy_context()

    first = evaluate_structural_graphs(
        structural_graph_rows=copy.deepcopy(state.get("structural_graphs")),
        structural_node_rows=copy.deepcopy(state.get("structural_nodes")),
        structural_edge_rows=copy.deepcopy(state.get("structural_edges")),
        current_tick=10,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy.get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy.get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy.get("stacking_policy_registry")),
    )
    second = evaluate_structural_graphs(
        structural_graph_rows=list(reversed(copy.deepcopy(state.get("structural_graphs")))),
        structural_node_rows=list(reversed(copy.deepcopy(state.get("structural_nodes")))),
        structural_edge_rows=list(reversed(copy.deepcopy(state.get("structural_edges")))),
        current_tick=10,
        max_cost_units=8,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy.get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy.get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy.get("stacking_policy_registry")),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "mechanics evaluation drifted across equivalent input permutations"}
    return {"status": "pass", "message": "load propagation deterministic"}

