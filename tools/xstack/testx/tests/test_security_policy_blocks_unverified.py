"""STRICT test: LOGIC-8 protocol security policies block unverified signal propagation."""

from __future__ import annotations

import sys


TEST_ID = "test_security_policy_blocks_unverified"
TEST_TAGS = ["strict", "logic", "security", "protocol"]


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
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_chain_network(network_id="net.logic.security.block")
    graph_row = dict(logic_network_state["logic_network_graph_rows"][0])
    graph_row["edges"] = [
        dict(
            edge,
            payload=dict(
                dict(edge.get("payload") or {}),
                extensions=dict(dict(dict(edge.get("payload") or {}).get("extensions") or {}), security_policy_id="sec.auth_required_stub"),
            ),
        )
        if str(edge.get("edge_id", "")) == "edge.and.to.not"
        else dict(edge)
        for edge in list(graph_row.get("edges") or [])
    ]
    logic_network_state["logic_network_graph_rows"] = [graph_row]

    signal_store_state = process_signal_set(
        current_tick=0,
        signal_store_state=None,
        signal_request={
            "network_id": "net.logic.security.block",
            "element_id": "inst.logic.not.1",
            "port_id": "in.a",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.sig",
            "value_payload": {"value": 1},
            "extensions": {
                "security_context": {
                    "authenticated": False,
                    "credential_verified": False,
                    "verification_state": "failed",
                }
            },
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
    ).get("signal_store_state")

    result = process_logic_network_evaluate(
        current_tick=1,
        logic_network_state=logic_network_state,
        signal_store_state=signal_store_state,
        logic_eval_state=None,
        evaluation_request={"network_id": "net.logic.security.block"},
        state_vector_snapshot_rows=[],
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
        return {"status": "fail", "message": "security-policy fixture did not complete deterministic evaluation"}
    security_rows = list(dict(result.get("logic_eval_state") or {}).get("logic_security_fail_rows") or [])
    if not security_rows:
        return {"status": "fail", "message": "unverified protocol link did not emit a security-fail row"}
    row = dict(security_rows[0])
    if str(row.get("security_policy_id", "")).strip() != "sec.auth_required_stub":
        return {"status": "fail", "message": "security fail row did not preserve the applied security policy id"}
    snapshot = dict(result.get("sense_snapshot") or {})
    not_inputs = dict(dict(snapshot.get("inputs_by_element") or {}).get("inst.logic.not.1") or {})
    if int(dict(not_inputs.get("in.a") or {}).get("value", 1)) != 0:
        return {"status": "fail", "message": "security gate did not force a safe default value on the blocked input"}
    explain_rows = [dict(row) for row in list(result.get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if not any(str(dict(row.get("extensions") or {}).get("event_kind_id", "")).strip() == "explain.logic_spoof_detected" for row in explain_rows):
        return {"status": "fail", "message": "blocked security fixture did not emit explain.logic_spoof_detected"}
    return {"status": "pass", "message": "security policies deterministically block unverified protocol-linked signals"}
