"""FAST test: LOGIC-3 network validation hash is deterministic under input ordering."""

from __future__ import annotations

import sys


TEST_ID = "test_network_validation_deterministic"
TEST_TAGS = ["fast", "logic", "network", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row, validate

    binding = binding_row(network_id="net.logic.det", graph_id="graph.logic.det")
    nodes = [
        node_row(node_id="node.src.a", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
        node_row(node_id="node.src.b", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
        node_row(
            node_id="node.and.in.a",
            node_kind="port_in",
            element_instance_id="inst.logic.and.1",
            port_id="in.a",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(
            node_id="node.and.in.b",
            node_kind="port_in",
            element_instance_id="inst.logic.and.1",
            port_id="in.b",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(
            node_id="node.and.out.q",
            node_kind="port_out",
            element_instance_id="inst.logic.and.1",
            port_id="out.q",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(node_id="node.sink", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.boolean"]}),
    ]
    edges = [
        edge_row(edge_id="edge.src.a", from_node_id="node.src.a", to_node_id="node.and.in.a", edge_kind="link", signal_type_id="signal.boolean"),
        edge_row(edge_id="edge.src.b", from_node_id="node.src.b", to_node_id="node.and.in.b", edge_kind="link", signal_type_id="signal.boolean"),
        edge_row(edge_id="edge.out", from_node_id="node.and.out.q", to_node_id="node.sink", edge_kind="link", signal_type_id="signal.boolean"),
    ]

    graph_a = graph_row(graph_id=binding["graph_id"], nodes=nodes, edges=edges)
    graph_b = graph_row(graph_id=binding["graph_id"], nodes=list(reversed(nodes)), edges=list(reversed(edges)))
    result_a = validate(repo_root, binding=binding, graph=graph_a)
    result_b = validate(repo_root, binding=binding, graph=graph_b)

    if str(result_a.get("result", "")) != "complete" or str(result_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "expected deterministic validation fixture to complete"}
    if result_a.get("validation_hash") != result_b.get("validation_hash"):
        return {"status": "fail", "message": "validation hash changed under node/edge reordering"}
    if list(result_a.get("checks") or []) != list(result_b.get("checks") or []):
        return {"status": "fail", "message": "validation checks changed under node/edge reordering"}
    return {"status": "pass", "message": "logic network validation hash is deterministic"}
