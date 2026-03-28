"""STRICT test: LOGIC-9 protocol replay tool produces stable protocol hash summaries."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_protocol_hash_match"
TEST_TAGS = ["strict", "logic", "protocol", "replay", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.signal import process_signal_set
    from tools.logic.tool_replay_protocol_window import replay_protocol_window_from_payload
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_protocol_network

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_protocol_network(
        network_id="net.logic.protocol.replay",
        carrier_type_id="carrier.sig",
    )
    signal_store_state = None
    for port_id in ("in.a", "in.b"):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": "net.logic.protocol.replay",
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

    scenario = {
        "logic_network_state": logic_network_state,
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [
            {"tick": 1, "network_id": "net.logic.protocol.replay"},
            {"tick": 2, "network_id": "net.logic.protocol.replay"},
            {"tick": 3, "network_id": "net.logic.protocol.replay"},
        ],
    }
    first = replay_protocol_window_from_payload(repo_root=repo_root, payload=scenario)
    second = replay_protocol_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "protocol replay tool did not complete"}
    for key in (
        "deterministic_fingerprint",
        "logic_protocol_frame_hash_chain",
        "logic_arbitration_state_hash_chain",
        "logic_protocol_event_hash_chain",
    ):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "protocol replay hash '{}' drifted across equivalent runs".format(key)}
    return {"status": "pass", "message": "protocol replay hash summary is stable"}
