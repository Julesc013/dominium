"""FAST test: LOGIC-3 canonical network hash is stable under ordering changes."""

from __future__ import annotations

import sys


TEST_ID = "test_graph_hash_stable"
TEST_TAGS = ["fast", "logic", "network", "hash"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.network import canonical_logic_network_hash
    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, graph_row, node_row

    binding_a = binding_row(network_id="net.logic.hash.a", graph_id="graph.logic.hash.a")
    binding_b = binding_row(network_id="net.logic.hash.b", graph_id="graph.logic.hash.b")
    graph_a = graph_row(
        graph_id=binding_a["graph_id"],
        nodes=[
            node_row(node_id="node.a.2", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
            node_row(node_id="node.a.1", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
        ],
        edges=[],
    )
    graph_b = graph_row(
        graph_id=binding_b["graph_id"],
        nodes=[
            node_row(node_id="node.b.1", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
        ],
        edges=[],
    )
    state_a = {
        "logic_network_graph_rows": [graph_a, graph_b],
        "logic_network_binding_rows": [binding_a, binding_b],
    }
    state_b = {
        "logic_network_graph_rows": [
            graph_row(graph_id=binding_b["graph_id"], nodes=list(reversed(graph_b["nodes"])), edges=[]),
            graph_row(graph_id=binding_a["graph_id"], nodes=list(reversed(graph_a["nodes"])), edges=[]),
        ],
        "logic_network_binding_rows": [binding_b, binding_a],
    }

    if canonical_logic_network_hash(state=state_a) != canonical_logic_network_hash(state=state_b):
        return {"status": "fail", "message": "logic network hash changed under ordering-only differences"}
    return {"status": "pass", "message": "logic network hash is stable under ordering changes"}
