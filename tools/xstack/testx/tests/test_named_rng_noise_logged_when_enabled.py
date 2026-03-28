"""STRICT test: LOGIC-8 named-RNG noise is deterministic, gated, and logged."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_named_rng_noise_logged_when_enabled"
TEST_TAGS = ["strict", "logic", "noise", "rng"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import process_logic_network_evaluate
    from logic.signal import process_signal_emit_pulse, process_signal_set
    from system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_scalar_comparator_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_scalar_comparator_network(network_id="net.logic.noise.rng")
    graph_row = dict(logic_network_state["logic_network_graph_rows"][0])
    graph_row["edges"] = [
        dict(edge, payload=dict(dict(edge.get("payload") or {}), noise_policy_id="noise.named_rng_optional"))
        if str(edge.get("edge_id", "")) == "edge.scalar.value"
        else dict(edge)
        for edge in list(graph_row.get("edges") or [])
    ]
    logic_network_state["logic_network_graph_rows"] = [graph_row]

    signal_store_state = None
    for port_id, value_fixed in (("in.value", 75), ("in.threshold", 60)):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.noise.rng",
                "element_id": "inst.logic.comparator.1",
                "port_id": port_id,
                "signal_type_id": "signal.scalar",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value_fixed": value_fixed},
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
        signal_store_state = dict(seeded.get("signal_store_state") or {})

    def run_once():
        return process_logic_network_evaluate(
            current_tick=1,
            logic_network_state=copy.deepcopy(logic_network_state),
            signal_store_state=copy.deepcopy(signal_store_state),
            logic_eval_state=None,
            evaluation_request={
                "network_id": "net.logic.noise.rng",
                "extensions": {"allow_named_rng_noise": True},
            },
            state_vector_snapshot_rows=[],
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            serialize_state=serialize_state,
            process_signal_set_fn=process_signal_set,
            process_signal_emit_pulse_fn=process_signal_emit_pulse,
            **inputs,
        )

    first = run_once()
    second = run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "named-RNG noise fixture did not complete"}
    first_rows = list(dict(first.get("logic_eval_state") or {}).get("logic_noise_decision_rows") or [])
    second_rows = list(dict(second.get("logic_eval_state") or {}).get("logic_noise_decision_rows") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "named-RNG noise decisions drifted across equivalent runs"}
    rng_rows = [dict(row) for row in first_rows if str(dict(row).get("reason", "")).strip() == "named_rng_applied"]
    if not rng_rows:
        return {"status": "fail", "message": "named-RNG noise fixture produced no noise decision rows"}
    row = dict(rng_rows[0])
    if not str(row.get("rng_stream_name", "")).strip() or not str(row.get("rng_seed_hash", "")).strip():
        return {"status": "fail", "message": "named-RNG noise decision did not log deterministic RNG details"}
    return {"status": "pass", "message": "named-RNG logic noise is deterministic and logged when enabled"}
