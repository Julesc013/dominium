"""STRICT test: LOGIC-5 watchdog patterns trigger deterministic timeout events."""

from __future__ import annotations

import sys


TEST_ID = "test_watchdog_triggers_timeout"
TEST_TAGS = ["strict", "logic", "timing", "watchdog"]


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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_watchdog_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_watchdog_network(network_id="net.logic.timing.watchdog")
    seeded = process_signal_set(
        current_tick=0,
        signal_store_state=None,
        signal_request={
            "network_id": "net.logic.timing.watchdog",
            "element_id": "inst.logic.watchdog.1",
            "port_id": "in.enable",
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
    logic_eval_state = None
    state_vector_snapshot_rows = []
    state_vector_definition_rows = inputs["state_vector_definition_rows"]
    tick_four_result = None
    for tick in range(1, 5):
        result = process_logic_network_evaluate(
            current_tick=tick,
            logic_network_state=logic_network_state,
            signal_store_state=signal_store_state,
            logic_eval_state=logic_eval_state,
            evaluation_request={"network_id": "net.logic.timing.watchdog"},
            state_vector_snapshot_rows=state_vector_snapshot_rows,
            process_signal_set_fn=process_signal_set,
            process_signal_emit_pulse_fn=process_signal_emit_pulse,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            serialize_state=serialize_state,
            state_vector_definition_rows=state_vector_definition_rows,
            **dict((key, value) for key, value in inputs.items() if key != "state_vector_definition_rows"),
        )
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "watchdog fixture refused before timeout"}
        signal_store_state = dict(result.get("signal_store_state") or {})
        logic_eval_state = dict(result.get("logic_eval_state") or {})
        state_vector_snapshot_rows = list(result.get("state_vector_snapshot_rows") or [])
        state_vector_definition_rows = list(result.get("state_vector_definition_rows") or state_vector_definition_rows)
        if tick == 4:
            tick_four_result = dict(result)

    watchdog_rows = list(dict(logic_eval_state or {}).get("logic_watchdog_timeout_event_rows") or [])
    if not watchdog_rows or int(dict(watchdog_rows[0]).get("tick", 0) or 0) != 4:
        return {"status": "fail", "message": "watchdog timeout was not emitted at tick 4"}
    explain_rows = [dict(row) for row in list(dict(tick_four_result or {}).get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if not any(str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip() == "explain.watchdog_timeout" for row in explain_rows):
        return {"status": "fail", "message": "watchdog timeout explain artifact was not emitted"}
    return {"status": "pass", "message": "watchdog timeout detection is deterministic"}
