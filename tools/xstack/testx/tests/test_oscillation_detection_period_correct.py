"""STRICT test: LOGIC-5 oscillation detection reports the expected period."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_oscillation_detection_period_correct"
TEST_TAGS = ["strict", "logic", "timing", "oscillation"]


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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_relay_feedback_oscillator_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_relay_feedback_oscillator_network(network_id="net.logic.timing.oscillator")
    logic_network_state = copy.deepcopy(logic_network_state)
    logic_network_state["logic_network_binding_rows"][0]["extensions"]["logic_policy_id"] = "logic.lab_experimental"

    signal_store_state = None
    logic_eval_state = None
    state_vector_snapshot_rows = []
    state_vector_definition_rows = inputs["state_vector_definition_rows"]
    for tick in range(1, 10):
        result = process_logic_network_evaluate(
            current_tick=tick,
            logic_network_state=logic_network_state,
            signal_store_state=signal_store_state,
            logic_eval_state=logic_eval_state,
            evaluation_request={"network_id": "net.logic.timing.oscillator"},
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
            return {"status": "fail", "message": "oscillator fixture refused before stable period classification"}
        signal_store_state = dict(result.get("signal_store_state") or {})
        logic_eval_state = dict(result.get("logic_eval_state") or {})
        state_vector_snapshot_rows = list(result.get("state_vector_snapshot_rows") or [])
        state_vector_definition_rows = list(result.get("state_vector_definition_rows") or state_vector_definition_rows)

    oscillation_rows = [
        dict(row)
        for row in list(logic_eval_state.get("logic_oscillation_record_rows") or [])
        if isinstance(row, dict)
    ]
    matching = [
        row for row in oscillation_rows if bool(row.get("stable", False)) and int(row.get("period_ticks", 0) or 0) == 3
    ]
    if not matching:
        return {"status": "fail", "message": "stable oscillator period was not classified as three ticks"}
    return {"status": "pass", "message": "oscillation period classification is deterministic and correct"}
