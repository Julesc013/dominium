"""FAST test: LOGIC-3 validator allows sequential loops under default policy."""

from __future__ import annotations

import sys


TEST_ID = "test_sequential_loop_allowed"
TEST_TAGS = ["fast", "logic", "network", "loop"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row, validate

    binding = binding_row(network_id="net.logic.seq_loop", graph_id="graph.logic.seq_loop")
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(
                node_id="node.relay1.in",
                node_kind="port_in",
                element_instance_id="inst.logic.relay.1",
                port_id="in.coil",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.relay1.out",
                node_kind="port_out",
                element_instance_id="inst.logic.relay.1",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.relay2.in",
                node_kind="port_in",
                element_instance_id="inst.logic.relay.2",
                port_id="in.coil",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.relay2.out",
                node_kind="port_out",
                element_instance_id="inst.logic.relay.2",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
        ],
        edges=[
            edge_row(edge_id="edge.relay1_to_relay2", from_node_id="node.relay1.out", to_node_id="node.relay2.in", edge_kind="link", signal_type_id="signal.boolean"),
            edge_row(edge_id="edge.relay2_to_relay1", from_node_id="node.relay2.out", to_node_id="node.relay1.in", edge_kind="link", signal_type_id="signal.boolean"),
        ],
    )

    result = validate(repo_root, binding=binding, graph=graph)
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "sequential loop should be allowed under default policy"}
    loops = list(result.get("loop_classifications") or [])
    if not loops:
        return {"status": "fail", "message": "sequential loop classification missing"}
    first = dict(loops[0])
    if str(first.get("classification", "")).strip() != "sequential":
        return {"status": "fail", "message": "sequential loop classified incorrectly"}
    return {"status": "pass", "message": "sequential loops are allowed deterministically"}
