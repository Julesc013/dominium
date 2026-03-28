"""STRICT test: LOGIC-8 replay tool produces stable fault/noise/security hashes."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_replay_fault_hash_match"
TEST_TAGS = ["strict", "logic", "fault", "noise", "security", "replay", "proof"]


def _load(repo_root: str, rel_path: str) -> dict:
    with open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.fault import process_logic_fault_set
    from logic.signal import process_signal_set
    from tools.logic.tool_replay_fault_window import replay_fault_window_from_payload
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network, make_scalar_comparator_network

    inputs = load_eval_inputs(repo_root)
    fault_registry = _load(repo_root, "data/registries/logic_fault_kind_registry.json")

    _, chain_state = make_chain_network(network_id="net.logic.replay.fault")
    chain_graph = dict(chain_state["logic_network_graph_rows"][0])
    chain_graph["edges"] = [
        dict(
            edge,
            payload=dict(
                dict(edge.get("payload") or {}),
                extensions=dict(dict(dict(edge.get("payload") or {}).get("extensions") or {}), security_policy_id="sec.auth_required_stub"),
            ),
        )
        if str(edge.get("edge_id", "")) == "edge.and.to.not"
        else dict(edge)
        for edge in list(chain_graph.get("edges") or [])
    ]
    chain_state["logic_network_graph_rows"] = [chain_graph]

    _, scalar_state = make_scalar_comparator_network(network_id="net.logic.replay.noise")
    scalar_graph = dict(scalar_state["logic_network_graph_rows"][0])
    scalar_graph["edges"] = [
        dict(edge, payload=dict(dict(edge.get("payload") or {}), noise_policy_id="noise.named_rng_optional"))
        if str(edge.get("edge_id", "")) == "edge.scalar.value"
        else dict(edge)
        for edge in list(scalar_graph.get("edges") or [])
    ]
    scalar_state["logic_network_graph_rows"] = [scalar_graph]

    signal_store_state = None
    for request in (
        {
            "network_id": "net.logic.replay.fault",
            "element_id": "inst.logic.and.1",
            "port_id": "in.a",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value": 1},
        },
        {
            "network_id": "net.logic.replay.fault",
            "element_id": "inst.logic.and.1",
            "port_id": "in.b",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value": 1},
        },
        {
            "network_id": "net.logic.replay.fault",
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
        {
            "network_id": "net.logic.replay.noise",
            "element_id": "inst.logic.comparator.1",
            "port_id": "in.value",
            "signal_type_id": "signal.scalar",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value_fixed": 75},
        },
        {
            "network_id": "net.logic.replay.noise",
            "element_id": "inst.logic.comparator.1",
            "port_id": "in.threshold",
            "signal_type_id": "signal.scalar",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value_fixed": 60},
        },
    ):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request=request,
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
        return {"status": "fail", "message": "fault replay fixture could not set the canonical open fault"}

    scenario = {
        "logic_network_state": {
            "logic_network_graph_rows": list(chain_state.get("logic_network_graph_rows") or [])
            + list(scalar_state.get("logic_network_graph_rows") or []),
            "logic_network_binding_rows": list(chain_state.get("logic_network_binding_rows") or [])
            + list(scalar_state.get("logic_network_binding_rows") or []),
            "logic_network_validation_records": list(chain_state.get("logic_network_validation_records") or [])
            + list(scalar_state.get("logic_network_validation_records") or []),
            "logic_network_change_records": [],
            "logic_network_explain_artifact_rows": [],
            "compute_runtime_state": {},
        },
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "logic_fault_state_rows": fault_result.get("logic_fault_state_rows") or [],
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [
            {"tick": 1, "network_id": "net.logic.replay.fault"},
            {"tick": 1, "network_id": "net.logic.replay.noise", "extensions": {"allow_named_rng_noise": True}},
        ],
    }

    first = replay_fault_window_from_payload(repo_root=repo_root, payload=scenario)
    second = replay_fault_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "fault replay tool did not complete"}
    for key in (
        "deterministic_fingerprint",
        "logic_fault_state_hash_chain",
        "logic_noise_decision_hash_chain",
        "logic_security_fail_hash_chain",
    ):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "fault replay hash '{}' drifted across equivalent runs".format(key)}
    return {"status": "pass", "message": "fault/noise/security replay hashes are stable"}
