"""FAST test: LOGIC-3 validator detects and refuses combinational loops by default."""

from __future__ import annotations

import sys


TEST_ID = "test_combinational_loop_detected_and_refused"
TEST_TAGS = ["fast", "logic", "network", "loop"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.network import REFUSAL_LOGIC_LOOP_DETECTED
    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row, validate

    binding = binding_row(network_id="net.logic.comb_loop", graph_id="graph.logic.comb_loop")
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(
                node_id="node.not1.in",
                node_kind="port_in",
                element_instance_id="inst.logic.not.1",
                port_id="in.a",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
            node_row(
                node_id="node.not1.out",
                node_kind="port_out",
                element_instance_id="inst.logic.not.1",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
            node_row(
                node_id="node.not2.in",
                node_kind="port_in",
                element_instance_id="inst.logic.not.2",
                port_id="in.a",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
            node_row(
                node_id="node.not2.out",
                node_kind="port_out",
                element_instance_id="inst.logic.not.2",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
        ],
        edges=[
            edge_row(edge_id="edge.not1_to_not2", from_node_id="node.not1.out", to_node_id="node.not2.in", edge_kind="link", signal_type_id="signal.boolean"),
            edge_row(edge_id="edge.not2_to_not1", from_node_id="node.not2.out", to_node_id="node.not1.in", edge_kind="link", signal_type_id="signal.boolean"),
        ],
    )

    result = validate(repo_root, binding=binding, graph=graph)
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "combinational loop should refuse under default policy"}
    if str(result.get("reason_code", "")).strip() != REFUSAL_LOGIC_LOOP_DETECTED:
        return {"status": "fail", "message": "combinational loop refused with wrong reason code"}
    loops = list(result.get("loop_classifications") or [])
    if not loops:
        return {"status": "fail", "message": "combinational loop classification missing"}
    first = dict(loops[0])
    if str(first.get("classification", "")).strip() != "combinational" or str(first.get("policy_resolution", "")).strip() != "refuse":
        return {"status": "fail", "message": "combinational loop classification incorrect"}
    return {"status": "pass", "message": "combinational loops are detected and refused"}
