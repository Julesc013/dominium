"""STRICT test: LOGIC-5 timing violations are detected and gate later L1 evaluation."""

from __future__ import annotations

import sys


TEST_ID = "test_timing_violation_detected"
TEST_TAGS = ["strict", "logic", "timing", "constraint"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import REFUSAL_LOGIC_EVAL_TIMING_VIOLATION, process_logic_network_evaluate
    from logic.signal import process_signal_emit_pulse, process_signal_set
    from system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_chain_network(
        network_id="net.logic.timing.constraint",
        delay_policy_id="delay.fixed_ticks",
        delay_extensions={"fixed_ticks": 2},
        binding_extensions={
            "timing_constraint": {
                "constraint_id": "logic.constraint.tight",
                "max_propagation_ticks": 1,
            }
        },
    )
    signal_store_state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.timing.constraint",
                "element_id": "inst.logic.and.1",
                "port_id": port_id,
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
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

    first = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=signal_store_state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.timing.constraint"},
        state_vector_snapshot_rows=[],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        state_vector_definition_rows=inputs["state_vector_definition_rows"],
        **dict((key, value) for key, value in inputs.items() if key != "state_vector_definition_rows"),
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "timing-constraint fixture did not complete the first tick"}
    first_eval_state = dict(first.get("logic_eval_state") or {})
    timing_rows = list(first_eval_state.get("logic_timing_violation_event_rows") or [])
    if not timing_rows:
        return {"status": "fail", "message": "timing violation event was not emitted"}
    runtime_row = next(
        (
            dict(row)
            for row in list(first_eval_state.get("logic_network_runtime_state_rows") or [])
            if str(row.get("network_id", "")).strip() == "net.logic.timing.constraint"
        ),
        {},
    )
    runtime_extensions = dict(runtime_row.get("extensions") or {})
    if not bool(runtime_extensions.get("requires_l2_timing", False)):
        return {"status": "fail", "message": "timing violation did not mark the network for L2 timing"}

    second = process_logic_network_evaluate(
        current_tick=2,
        logic_network_state=logic_network_state,
        signal_store_state=first.get("signal_store_state"),
        logic_eval_state=first.get("logic_eval_state"),
        evaluation_request={"network_id": "net.logic.timing.constraint"},
        state_vector_snapshot_rows=first.get("state_vector_snapshot_rows") or [],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        state_vector_definition_rows=first.get("state_vector_definition_rows") or inputs["state_vector_definition_rows"],
        **dict((key, value) for key, value in inputs.items() if key != "state_vector_definition_rows"),
    )
    if str(second.get("reason_code", "")) != REFUSAL_LOGIC_EVAL_TIMING_VIOLATION:
        return {"status": "fail", "message": "timing-gated network did not refuse later L1 evaluation"}
    return {"status": "pass", "message": "timing violations are detected and gate later L1 evaluation"}
