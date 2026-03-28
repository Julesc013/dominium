"""STRICT test: LOGIC-4 state updates are committed only in COMMIT phase."""

from __future__ import annotations

import sys


TEST_ID = "test_state_updates_only_in_commit"
TEST_TAGS = ["strict", "logic", "eval", "statevec"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests._logic_network_test_utils import binding_row, graph_row, node_row
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs
    from logic.eval import process_logic_network_evaluate
    from logic.signal import process_signal_set
    from system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )

    inputs = load_eval_inputs(repo_root)
    binding = binding_row(
        network_id="net.logic.eval.commit",
        graph_id="graph.logic.eval.commit",
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.default"},
    )
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(node_id="node.relay.in.coil", node_kind="port_in", element_instance_id="inst.logic.relay.1", port_id="in.coil", payload_extensions={"element_definition_id": "logic.relay"}),
            node_row(node_id="node.relay.in.reset", node_kind="port_in", element_instance_id="inst.logic.relay.1", port_id="in.reset", payload_extensions={"element_definition_id": "logic.relay"}),
            node_row(node_id="node.relay.out.q", node_kind="port_out", element_instance_id="inst.logic.relay.1", port_id="out.q", payload_extensions={"element_definition_id": "logic.relay"}),
        ],
        edges=[],
    )
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [{"tick": 0, "network_id": "net.logic.eval.commit", "validation_hash": "ok", "loop_classifications": []}],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    state = None
    for port_id, value in (("in.coil", 1), ("in.reset", 0)):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=state,
            signal_request={
                "network_id": "net.logic.eval.commit",
                "element_id": "inst.logic.relay.1",
                "port_id": port_id,
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": value},
            },
            signal_type_registry_payload=inputs["signal_type_registry_payload"],
            carrier_type_registry_payload=inputs["carrier_type_registry_payload"],
            signal_delay_policy_registry_payload=inputs["signal_delay_policy_registry_payload"],
            signal_noise_policy_registry_payload=inputs["signal_noise_policy_registry_payload"],
            bus_encoding_registry_payload=inputs["bus_encoding_registry_payload"],
            protocol_registry_payload=inputs["protocol_registry_payload"],
            compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
            compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
            tolerance_policy_registry_payload=inputs["tolerance_policy_registry_payload"],
        )
        state = dict(seeded.get("signal_store_state") or {})

    result = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.eval.commit"},
        state_vector_snapshot_rows=[],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=__import__("logic.signal", fromlist=["process_signal_emit_pulse"]).process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        **inputs,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "relay evaluation did not complete"}
    if result.get("compute_result", {}).get("state_vector_snapshot_rows") is not None:
        return {"status": "fail", "message": "compute phase leaked committed state snapshots"}
    snapshot_rows = list(result.get("state_vector_snapshot_rows") or [])
    if not snapshot_rows:
        return {"status": "fail", "message": "commit phase did not serialize state vector update"}
    relay_snapshot = next((row for row in snapshot_rows if str(row.get("owner_id", "")).strip() == "inst.logic.relay.1"), {})
    if not relay_snapshot:
        return {"status": "fail", "message": "relay instance state snapshot missing after commit"}
    updates = list(dict(result.get("logic_eval_state") or {}).get("logic_state_update_record_rows") or [])
    if not updates:
        return {"status": "fail", "message": "state update record missing from commit phase"}
    return {"status": "pass", "message": "state updates are committed only in COMMIT phase"}

