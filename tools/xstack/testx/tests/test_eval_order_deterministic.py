"""STRICT test: LOGIC-4 evaluation order and outputs are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_eval_order_deterministic"
TEST_TAGS = ["strict", "logic", "eval", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.eval import process_logic_network_evaluate
    from src.logic.signal import canonical_signal_hash, process_signal_set
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
    _, logic_network_state = make_chain_network(network_id="net.logic.eval.det")

    def seed_inputs():
        state = None
        for port_id in ("in.a", "in.b"):
            seeded = process_signal_set(
                current_tick=0,
                signal_store_state=state,
                signal_request={
                    "network_id": "net.logic.eval.det",
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
        return state

    def run_once():
        state_vector_rows = normalize_state_vector_definition_rows(inputs["state_vector_definition_rows"])
        result = process_logic_network_evaluate(
            current_tick=1,
            logic_network_state=copy.deepcopy(logic_network_state),
            signal_store_state=seed_inputs(),
            logic_eval_state=None,
            evaluation_request={"network_id": "net.logic.eval.det"},
            state_vector_snapshot_rows=[],
            process_signal_set_fn=process_signal_set,
            process_signal_emit_pulse_fn=__import__("src.logic.signal", fromlist=["process_signal_emit_pulse"]).process_signal_emit_pulse,
            build_state_vector_definition_row=build_state_vector_definition_row,
            normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
            normalize_state_vector_snapshot_rows=normalize_state_vector_snapshot_rows,
            state_vector_snapshot_rows_by_owner=state_vector_snapshot_rows_by_owner,
            deserialize_state=deserialize_state,
            serialize_state=serialize_state,
            **inputs,
        )
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "logic evaluation did not complete in deterministic fixture"}
        return {
            "status": "pass",
            "eval_record_row": dict(result.get("eval_record_row") or {}),
            "pending_rows": list(dict(result.get("logic_eval_state") or {}).get("logic_pending_signal_update_rows") or []),
            "signal_hash": canonical_signal_hash(state=result.get("signal_store_state")),
        }

    first = run_once()
    second = run_once()
    if first.get("status") != "pass" or second.get("status") != "pass":
        return first if first.get("status") != "pass" else second
    if first["eval_record_row"] != second["eval_record_row"]:
        return {"status": "fail", "message": "logic eval record drifted across equivalent runs"}
    if first["pending_rows"] != second["pending_rows"]:
        return {"status": "fail", "message": "pending propagation rows drifted across equivalent runs"}
    if first["signal_hash"] != second["signal_hash"]:
        return {"status": "fail", "message": "signal snapshot hash drifted across equivalent runs"}
    return {"status": "pass", "message": "logic evaluation order is deterministic"}

