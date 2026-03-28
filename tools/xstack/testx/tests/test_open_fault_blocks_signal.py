"""STRICT test: LOGIC-8 open faults block signal visibility during SENSE."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_open_fault_blocks_signal"
TEST_TAGS = ["strict", "logic", "fault", "sense"]


def _load(repo_root: str, rel_path: str) -> dict:
    with open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import process_logic_network_evaluate
    from logic.fault import process_logic_fault_set
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
    fault_registry = _load(repo_root, "data/registries/logic_fault_kind_registry.json")
    _, logic_network_state = make_chain_network(network_id="net.logic.fault.open")

    signal_store_state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.fault.open",
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

    fault_result = process_logic_fault_set(
        current_tick=0,
        logic_fault_state_rows=[],
        fault_request={
            "fault_kind_id": "fault.open",
            "target_kind": "node",
            "target_id": "node.and.in.a",
        },
        logic_fault_kind_registry_payload=fault_registry,
    )
    if str(fault_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic fault set refused valid open-fault fixture"}

    result = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=signal_store_state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.fault.open"},
        state_vector_snapshot_rows=[],
        logic_fault_state_rows=fault_result.get("logic_fault_state_rows"),
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
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic evaluation did not complete with a valid open-fault fixture"}
    snapshot = dict(result.get("sense_snapshot") or {})
    inputs_by_element = dict(snapshot.get("inputs_by_element") or {})
    and_inputs = dict(inputs_by_element.get("inst.logic.and.1") or {})
    if int(dict(and_inputs.get("in.a") or {}).get("value", 1)) != 0:
        return {"status": "fail", "message": "open fault did not block the targeted input signal"}
    explain_rows = [dict(row) for row in list(result.get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if not any(str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip() == "explain.logic_fault_open" for row in explain_rows):
        return {"status": "fail", "message": "open fault did not produce explain.logic_fault_open"}
    return {"status": "pass", "message": "open faults deterministically block targeted signal inputs"}
