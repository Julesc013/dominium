"""FAST test: LOGIC-3 cross-shard links require SIG or explicit boundary artifacts."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_shard_link_requires_sig_or_boundary"
TEST_TAGS = ["fast", "logic", "network", "cross_shard"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row, validate

    binding = binding_row(network_id="net.logic.cross_shard", graph_id="graph.logic.cross_shard")
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(
                node_id="node.shard.a",
                node_kind="junction",
                payload_extensions={"allowed_signal_type_ids": ["signal.boolean"], "shard_id": "shard.a"},
            ),
            node_row(
                node_id="node.shard.b",
                node_kind="junction",
                payload_extensions={"allowed_signal_type_ids": ["signal.boolean"], "shard_id": "shard.b"},
            ),
        ],
        edges=[
            edge_row(
                edge_id="edge.cross_shard",
                from_node_id="node.shard.a",
                to_node_id="node.shard.b",
                edge_kind="link",
                signal_type_id="signal.boolean",
            )
        ],
    )

    result = validate(repo_root, binding=binding, graph=graph)
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "cross-shard direct link should be refused"}
    failed_ids = {str(row.get("check_id", "")).strip() for row in list(result.get("failed_checks") or []) if isinstance(row, dict)}
    if not any(token.startswith("edge.cross_shard.boundary_safe.") for token in failed_ids):
        return {"status": "fail", "message": "cross-shard refusal did not report boundary safety check"}
    return {"status": "pass", "message": "cross-shard logic links require SIG or boundary artifacts"}
