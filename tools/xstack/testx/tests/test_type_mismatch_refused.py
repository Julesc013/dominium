"""FAST test: LOGIC-3 validator refuses signal type mismatches."""

from __future__ import annotations

import sys


TEST_ID = "test_type_mismatch_refused"
TEST_TAGS = ["fast", "logic", "network", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row, validate

    binding = binding_row(network_id="net.logic.type_mismatch", graph_id="graph.logic.type_mismatch")
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(node_id="node.src.scalar", node_kind="junction", payload_extensions={"allowed_signal_type_ids": ["signal.scalar"]}),
            node_row(
                node_id="node.and.in.a",
                node_kind="port_in",
                element_instance_id="inst.logic.and.type",
                port_id="in.a",
                payload_extensions={"element_definition_id": "logic.and"},
            ),
        ],
        edges=[
            edge_row(
                edge_id="edge.scalar_to_bool",
                from_node_id="node.src.scalar",
                to_node_id="node.and.in.a",
                edge_kind="link",
                signal_type_id="signal.scalar",
            )
        ],
    )

    result = validate(repo_root, binding=binding, graph=graph)
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "type mismatch should refuse validation"}
    failed_ids = {str(row.get("check_id", "")).strip() for row in list(result.get("failed_checks") or []) if isinstance(row, dict)}
    if not any(token.startswith("edge.signal.matches_to.") for token in failed_ids):
        return {"status": "fail", "message": "type mismatch refusal did not surface target compatibility check"}
    return {"status": "pass", "message": "logic network type mismatches are refused"}
