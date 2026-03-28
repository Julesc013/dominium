"""STRICT test: LOGIC-4 refuses combinational loops at L1 evaluation time."""

from __future__ import annotations

import sys


TEST_ID = "test_loop_refusal_behavior"
TEST_TAGS = ["strict", "logic", "eval", "loops"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import REFUSAL_LOGIC_EVAL_LOOP_POLICY, process_logic_network_evaluate
    from logic.signal import process_signal_set
    from system import (
        build_state_vector_definition_row,
        deserialize_state,
        normalize_state_vector_definition_rows,
        normalize_state_vector_snapshot_rows,
        serialize_state,
        state_vector_snapshot_rows_by_owner,
    )
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_loop_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_loop_network(network_id="net.logic.eval.loop")
    result = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=None,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.eval.loop"},
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
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected loop topology fixture to be refused"}
    if str(result.get("reason_code", "")) != REFUSAL_LOGIC_EVAL_LOOP_POLICY:
        return {"status": "fail", "message": "loop refusal returned unexpected reason code"}
    return {"status": "pass", "message": "loop policy refusal is enforced at L1 evaluation time"}

