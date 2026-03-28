"""STRICT test: LOGIC-4 compute throttling is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_compute_budget_throttle_deterministic"
TEST_TAGS = ["strict", "logic", "eval", "compute"]


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
    _, logic_network_state = make_chain_network(network_id="net.logic.eval.throttle")
    logic_policy_registry_payload = copy.deepcopy(inputs["logic_policy_registry_payload"])
    policy_rows = list(dict(logic_policy_registry_payload.get("record") or {}).get("logic_policies") or [])
    for row in policy_rows:
        if str(row.get("policy_id", "")).strip() == "logic.default":
            row["extensions"] = dict(row.get("extensions") or {}, network_compute_cap_units=1)
    dict(logic_policy_registry_payload.get("record") or {})["logic_policies"] = policy_rows
    logic_policy_registry_payload["record"] = dict(logic_policy_registry_payload.get("record") or {}, logic_policies=policy_rows)

    state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=state,
            signal_request={
                "network_id": "net.logic.eval.throttle",
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

    def run_once():
        return process_logic_network_evaluate(
            current_tick=1,
            logic_network_state=copy.deepcopy(logic_network_state),
            signal_store_state=copy.deepcopy(state),
            logic_eval_state=None,
            evaluation_request={"network_id": "net.logic.eval.throttle"},
            state_vector_snapshot_rows=[],
            process_signal_set_fn=process_signal_set,
            process_signal_emit_pulse_fn=__import__("logic.signal", fromlist=["process_signal_emit_pulse"]).process_signal_emit_pulse,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            serialize_state=serialize_state,
            logic_policy_registry_payload=logic_policy_registry_payload,
            **dict((key, value) for key, value in inputs.items() if key != "logic_policy_registry_payload"),
        )

    first = run_once()
    second = run_once()
    if str(first.get("result", "")) != "throttled" or str(second.get("result", "")) != "throttled":
        return {"status": "fail", "message": "expected deterministic compute throttling fixture to throttle"}
    first_record = dict(first.get("eval_record_row") or {})
    second_record = dict(second.get("eval_record_row") or {})
    if first_record != second_record:
        return {"status": "fail", "message": "throttle eval record drifted across equivalent runs"}
    if int(first_record.get("elements_evaluated_count", 0)) != 1:
        return {"status": "fail", "message": "network compute cap did not stop evaluation after first element"}
    if list(first.get("throttle_event_rows") or []) != list(second.get("throttle_event_rows") or []):
        return {"status": "fail", "message": "throttle events drifted across equivalent runs"}
    return {"status": "pass", "message": "compute throttling is deterministic"}

