"""STRICT test: LOGIC-4 propagation delay policies are applied deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_propagation_delay_applied"
TEST_TAGS = ["strict", "logic", "eval", "delay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_chain_network(
        network_id="net.logic.eval.delay",
        delay_policy_id="delay.fixed_ticks",
        delay_extensions={"fixed_ticks": 2},
    )
    state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=state,
            signal_request={
                "network_id": "net.logic.eval.delay",
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
        state = dict(seeded.get("signal_store_state") or {})

    eval1 = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.eval.delay"},
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
    pending_rows = list(dict(eval1.get("logic_eval_state") or {}).get("logic_pending_signal_update_rows") or [])
    if not pending_rows or int(pending_rows[0].get("deliver_tick", 0)) != 3:
        return {"status": "fail", "message": "fixed tick delay did not schedule delivery for tick 3"}

    eval2 = process_logic_network_evaluate(
        current_tick=2,
        logic_network_state=logic_network_state,
        signal_store_state=eval1.get("signal_store_state"),
        logic_eval_state=eval1.get("logic_eval_state"),
        evaluation_request={"network_id": "net.logic.eval.delay"},
        state_vector_snapshot_rows=eval1.get("state_vector_snapshot_rows") or [],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=__import__("logic.signal", fromlist=["process_signal_emit_pulse"]).process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        state_vector_definition_rows=eval1.get("state_vector_definition_rows") or inputs["state_vector_definition_rows"],
        **dict((key, value) for key, value in inputs.items() if key != "state_vector_definition_rows"),
    )
    target_before = [
        row for row in list(dict(eval2.get("signal_store_state") or {}).get("signal_rows") or [])
        if str(dict(row.get("extensions") or {}).get("slot", {}).get("element_id", "")).strip() == "inst.logic.not.1"
        and str(dict(row.get("extensions") or {}).get("slot", {}).get("port_id", "")).strip() == "in.a"
    ]
    if target_before:
        return {"status": "fail", "message": "delayed propagation became visible before the declared tick"}

    eval3 = process_logic_network_evaluate(
        current_tick=3,
        logic_network_state=logic_network_state,
        signal_store_state=eval2.get("signal_store_state"),
        logic_eval_state=eval2.get("logic_eval_state"),
        evaluation_request={"network_id": "net.logic.eval.delay"},
        state_vector_snapshot_rows=eval2.get("state_vector_snapshot_rows") or [],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=__import__("logic.signal", fromlist=["process_signal_emit_pulse"]).process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        state_vector_definition_rows=eval2.get("state_vector_definition_rows") or inputs["state_vector_definition_rows"],
        **dict((key, value) for key, value in inputs.items() if key != "state_vector_definition_rows"),
    )
    target_after = [
        row for row in list(dict(eval3.get("signal_store_state") or {}).get("signal_rows") or [])
        if str(dict(row.get("extensions") or {}).get("slot", {}).get("element_id", "")).strip() == "inst.logic.not.1"
        and str(dict(row.get("extensions") or {}).get("slot", {}).get("port_id", "")).strip() == "in.a"
    ]
    if not target_after:
        return {"status": "fail", "message": "delayed propagation was not delivered at the declared tick"}
    return {"status": "pass", "message": "propagation delay policy applied deterministically"}

