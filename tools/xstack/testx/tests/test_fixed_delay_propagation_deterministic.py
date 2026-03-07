"""STRICT test: LOGIC-5 fixed-delay propagation remains deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fixed_delay_propagation_deterministic"
TEST_TAGS = ["strict", "logic", "timing", "delay"]


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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_chain_network(
        network_id="net.logic.timing.fixed_delay",
        delay_policy_id="delay.fixed_ticks",
        delay_extensions={"fixed_ticks": 2},
    )
    signal_store_state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.timing.fixed_delay",
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

    def run_once():
        return process_logic_network_evaluate(
            current_tick=1,
            logic_network_state=copy.deepcopy(logic_network_state),
            signal_store_state=copy.deepcopy(signal_store_state),
            logic_eval_state=None,
            evaluation_request={"network_id": "net.logic.timing.fixed_delay"},
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

    first = run_once()
    second = run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "fixed-delay evaluation did not complete deterministically"}

    first_pending = list(dict(first.get("logic_eval_state") or {}).get("logic_pending_signal_update_rows") or [])
    second_pending = list(dict(second.get("logic_eval_state") or {}).get("logic_pending_signal_update_rows") or [])
    if first_pending != second_pending:
        return {"status": "fail", "message": "fixed-delay pending propagation rows drifted across equivalent runs"}
    if not first_pending or int(first_pending[0].get("deliver_tick", 0) or 0) != 3:
        return {"status": "fail", "message": "fixed-delay propagation was not scheduled for tick 3"}
    return {"status": "pass", "message": "fixed-delay propagation is deterministic"}
