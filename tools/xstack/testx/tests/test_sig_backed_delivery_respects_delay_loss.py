"""STRICT test: LOGIC-9 SIG-backed protocol delivery respects deterministic delay/loss handling."""

from __future__ import annotations

import sys


TEST_ID = "test_sig_backed_delivery_respects_delay_loss"
TEST_TAGS = ["strict", "logic", "protocol", "sig"]


def _select_signal_row(signal_store_state: dict, *, network_id: str, element_id: str, port_id: str) -> dict:
    selected = {}
    for row in list(dict(signal_store_state or {}).get("signal_rows") or []):
        if not isinstance(row, dict):
            continue
        slot = dict(dict(row.get("extensions") or {}).get("slot") or {})
        if (
            str(slot.get("network_id", "")).strip() == str(network_id).strip()
            and str(slot.get("element_id", "")).strip() == str(element_id).strip()
            and str(slot.get("port_id", "")).strip() == str(port_id).strip()
        ):
            selected = dict(row)
    return selected


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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_protocol_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_protocol_network(
        network_id="net.logic.protocol.sig",
        carrier_type_id="carrier.sig",
    )

    signal_store_state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.protocol.sig",
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
        evaluation_request={"network_id": "net.logic.protocol.sig"},
        state_vector_snapshot_rows=[],
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        **inputs,
    )
    if str(first.get("result", "")) not in {"complete", "throttled"}:
        return {"status": "fail", "message": "first SIG-backed protocol evaluation did not complete"}
    if _select_signal_row(dict(first.get("signal_store_state") or {}), network_id="net.logic.protocol.sig", element_id="inst.logic.not.1", port_id="in.a"):
        return {"status": "fail", "message": "SIG-backed protocol delivery became visible too early"}
    first_events = [
        dict(row)
        for row in list(dict(first.get("logic_eval_state") or {}).get("logic_protocol_event_record_rows") or [])
        if isinstance(row, dict)
    ]
    if any(str(row.get("result", "")).strip() == "delivered" for row in first_events):
        return {"status": "fail", "message": "SIG-backed protocol delivery was marked delivered before the receipt tick"}

    second = process_logic_network_evaluate(
        current_tick=2,
        logic_network_state=logic_network_state,
        signal_store_state=dict(first.get("signal_store_state") or {}),
        logic_eval_state=dict(first.get("logic_eval_state") or {}),
        evaluation_request={"network_id": "net.logic.protocol.sig"},
        signal_transport_state=dict(first.get("signal_transport_state") or {}),
        state_vector_snapshot_rows=list(first.get("state_vector_snapshot_rows") or []),
        process_signal_set_fn=process_signal_set,
        process_signal_emit_pulse_fn=process_signal_emit_pulse,
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
        state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
        deserialize_state=deserialize_state,
        serialize_state=serialize_state,
        **inputs,
    )
    if str(second.get("result", "")) not in {"complete", "throttled"}:
        return {"status": "fail", "message": "second SIG-backed protocol evaluation did not complete"}
    delivered_row = _select_signal_row(
        dict(second.get("signal_store_state") or {}),
        network_id="net.logic.protocol.sig",
        element_id="inst.logic.not.1",
        port_id="in.a",
    )
    if not delivered_row:
        return {"status": "fail", "message": "SIG-backed protocol delivery did not become visible on the next tick"}
    transport_state = dict(second.get("signal_transport_state") or {})
    if not list(transport_state.get("message_delivery_event_rows") or []):
        return {"status": "fail", "message": "SIG-backed protocol delivery did not emit delivery event rows"}
    second_events = [
        dict(row)
        for row in list(dict(second.get("logic_eval_state") or {}).get("logic_protocol_event_record_rows") or [])
        if isinstance(row, dict)
    ]
    if not any(str(row.get("result", "")).strip() == "delivered" for row in second_events):
        return {"status": "fail", "message": "SIG-backed protocol delivery did not record a delivered protocol event on receipt"}
    return {"status": "pass", "message": "SIG-backed protocol delivery respects deterministic delay/loss handling"}
