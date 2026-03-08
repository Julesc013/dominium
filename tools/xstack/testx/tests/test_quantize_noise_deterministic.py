"""STRICT test: LOGIC-8 quantize noise is deterministic and logged."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_quantize_noise_deterministic"
TEST_TAGS = ["strict", "logic", "noise", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.eval import process_logic_network_evaluate
    from src.logic.signal import process_signal_emit_pulse, process_signal_set
    from src.system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_scalar_comparator_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_scalar_comparator_network(network_id="net.logic.noise.quantize")
    graph_row = dict(logic_network_state["logic_network_graph_rows"][0])
    graph_row["edges"] = [
        dict(edge, payload=dict(dict(edge.get("payload") or {}), noise_policy_id="noise.quantize_default"))
        if str(edge.get("edge_id", "")) == "edge.scalar.value"
        else dict(edge)
        for edge in list(graph_row.get("edges") or [])
    ]
    logic_network_state["logic_network_graph_rows"] = [graph_row]

    signal_store_state = None
    for port_id, value_fixed in (("in.value", 123), ("in.threshold", 110)):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.noise.quantize",
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
                "network_id": "net.logic.noise.quantize",
                "extensions": {"field_modifier_stubs": {"field.magnetic_flux_stub": 1}},
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
        return {"status": "fail", "message": "logic evaluation did not complete for quantize-noise fixture"}
    first_rows = list(dict(first.get("logic_eval_state") or {}).get("logic_noise_decision_rows") or [])
    second_rows = list(dict(second.get("logic_eval_state") or {}).get("logic_noise_decision_rows") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "quantize noise decisions drifted across equivalent runs"}
    quantized_rows = [dict(row) for row in first_rows if str(dict(row).get("reason", "")).strip() == "quantized"]
    if not quantized_rows:
        return {"status": "fail", "message": "quantize noise fixture produced no noise decision rows"}
    row = dict(quantized_rows[0])
    if str(row.get("input_value_hash", "")) == str(row.get("output_value_hash", "")):
        return {"status": "fail", "message": "quantize noise fixture did not alter the sampled scalar as expected"}
    return {"status": "pass", "message": "quantize noise is deterministic and logged"}
