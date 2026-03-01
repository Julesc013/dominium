"""FAST test: MECH-1 meso budget degradation is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.meso_budget_degradation"
TEST_TAGS = ["fast", "mechanics", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mechanics import evaluate_structural_graphs
    from tools.xstack.testx.tests.mechanics_testlib import base_state, policy_context

    state = base_state()
    graphs = copy.deepcopy(state.get("structural_graphs") or [])
    if graphs:
        second = dict(graphs[0])
        second["structural_graph_id"] = "structural.graph.beta"
        second["assembly_id"] = "assembly.structure_instance.beta"
        second["node_ids"] = list(second.get("node_ids") or [])
        second["edge_ids"] = list(second.get("edge_ids") or [])
        graphs.append(second)
    policy = policy_context()
    result = evaluate_structural_graphs(
        structural_graph_rows=graphs,
        structural_node_rows=copy.deepcopy(state.get("structural_nodes")),
        structural_edge_rows=copy.deepcopy(state.get("structural_edges")),
        current_tick=14,
        max_cost_units=1,
        cost_units_per_graph=1,
        connection_type_registry=copy.deepcopy(policy.get("connection_type_registry")),
        effect_rows=[],
        effect_type_registry=copy.deepcopy(policy.get("effect_type_registry")),
        stacking_policy_registry=copy.deepcopy(policy.get("stacking_policy_registry")),
    )
    if not bool(result.get("degraded", False)):
        return {"status": "fail", "message": "expected mechanics evaluation to degrade under constrained budget"}
    skipped = sorted(str(item).strip() for item in list(result.get("skipped_graph_ids") or []) if str(item).strip())
    if skipped != ["structural.graph.beta"]:
        return {"status": "fail", "message": "unexpected skipped_graph_ids {}".format(skipped)}
    return {"status": "pass", "message": "meso budget degradation deterministic"}

