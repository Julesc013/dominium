"""STRICT test: LOGIC-5 timing replay produces stable timing hash summaries."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_replay_timing_hash_match"
TEST_TAGS = ["strict", "logic", "timing", "replay", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.signal import process_signal_set
    from tools.logic.tool_replay_timing_window import replay_timing_window_from_payload
    from tools.xstack.testx.tests._logic_eval_test_utils import (
        load_eval_inputs,
        make_chain_network,
        make_relay_feedback_oscillator_network,
        make_watchdog_network,
    )

    inputs = load_eval_inputs(repo_root)
    _, oscillator_state = make_relay_feedback_oscillator_network(network_id="net.logic.timing.replay.osc")
    oscillator_state = copy.deepcopy(oscillator_state)
    oscillator_state["logic_network_binding_rows"][0]["extensions"]["logic_policy_id"] = "logic.lab_experimental"
    _, watchdog_state = make_watchdog_network(network_id="net.logic.timing.replay.watchdog")
    _, timing_state = make_chain_network(
        network_id="net.logic.timing.replay.constraint",
        delay_policy_id="delay.fixed_ticks",
        delay_extensions={"fixed_ticks": 2},
        binding_extensions={
            "timing_constraint": {
                "constraint_id": "logic.constraint.replay",
                "max_propagation_ticks": 1,
            }
        },
    )

    signal_store_state = None
    for request in (
        ("net.logic.timing.replay.watchdog", "inst.logic.watchdog.1", "in.enable", 1),
        ("net.logic.timing.replay.constraint", "inst.logic.and.1", "in.a", 1),
        ("net.logic.timing.replay.constraint", "inst.logic.and.1", "in.b", 1),
    ):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": request[0],
                "element_id": request[1],
                "port_id": request[2],
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": request[3]},
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
        "logic_network_state": {
            "logic_network_graph_rows": list(oscillator_state["logic_network_graph_rows"])
            + list(watchdog_state["logic_network_graph_rows"])
            + list(timing_state["logic_network_graph_rows"]),
            "logic_network_binding_rows": list(oscillator_state["logic_network_binding_rows"])
            + list(watchdog_state["logic_network_binding_rows"])
            + list(timing_state["logic_network_binding_rows"]),
            "logic_network_validation_records": list(oscillator_state["logic_network_validation_records"])
            + list(watchdog_state["logic_network_validation_records"])
            + list(timing_state["logic_network_validation_records"]),
            "logic_network_change_records": [],
            "logic_network_explain_artifact_rows": [],
            "compute_runtime_state": {},
        },
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "state_vector_snapshot_rows": [],
        "evaluation_requests": (
            [{"tick": tick, "network_id": "net.logic.timing.replay.osc"} for tick in range(1, 10)]
            + [{"tick": tick, "network_id": "net.logic.timing.replay.watchdog"} for tick in range(1, 5)]
            + [{"tick": 1, "network_id": "net.logic.timing.replay.constraint"}]
        ),
    }

    first = replay_timing_window_from_payload(repo_root=repo_root, payload=scenario)
    second = replay_timing_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "timing replay tool did not complete"}
    for key in (
        "deterministic_fingerprint",
        "logic_oscillation_record_hash_chain",
        "logic_timing_violation_hash_chain",
        "logic_watchdog_timeout_hash_chain",
    ):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "timing replay hash '{}' drifted across equivalent runs".format(key)}
    if int(first.get("oscillation_record_count", 0) or 0) < 1:
        return {"status": "fail", "message": "timing replay scenario did not produce oscillation records"}
    if int(first.get("watchdog_timeout_count", 0) or 0) < 1:
        return {"status": "fail", "message": "timing replay scenario did not produce watchdog timeout events"}
    if int(first.get("timing_violation_count", 0) or 0) < 1:
        return {"status": "fail", "message": "timing replay scenario did not produce timing violations"}
    return {"status": "pass", "message": "timing replay hash summary is stable"}
