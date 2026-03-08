"""STRICT test: LOGIC-7 trace replay hashes are stable, including protocol summaries."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_trace_hash_match"
TEST_TAGS = ["strict", "logic", "debug", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.tool_replay_trace_window import replay_trace_window_from_payload
    from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, seed_signal_requests

    inputs = load_eval_inputs(repo_root)
    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "tick": 0,
                "network_id": "net.logic.debug.protocol",
                "element_id": "inst.logic.bus.1",
                "port_id": "bus.out",
                "signal_type_id": "signal.bus",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {
                    "bus_id": "bus.logic.debug.protocol",
                    "encoding_id": "encoding.frame",
                    "sub_signals": [
                        {"field_id": "dst", "value": 1},
                        {"field_id": "src", "value": 2},
                    ],
                },
                "bus_definition_rows": [
                    {
                        "bus_id": "bus.logic.debug.protocol",
                        "encoding_id": "encoding.frame",
                        "width": 16,
                        "fields": [
                            {"field_id": "dst", "signal_type_id": "signal.boolean"},
                            {"field_id": "src", "signal_type_id": "signal.boolean"},
                        ],
                    }
                ],
                "protocol_definition_rows": [
                    {
                        "protocol_id": "protocol.simple_frame_stub",
                        "bus_id": "bus.logic.debug.protocol",
                        "framing_rules_ref": "stub.frame.local",
                        "arbitration_policy_id": "arb.none",
                        "error_detection_policy_id": "err.none",
                    }
                ],
                "bus_id": "bus.logic.debug.protocol",
                "protocol_id": "protocol.simple_frame_stub",
            }
        ],
        inputs=inputs,
    )
    payload = {
        "logic_network_state": {},
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "compiled_model_rows": [],
        "state_vector_snapshot_rows": [],
        "probe_requests": [],
        "trace_requests": [
            {
                "tick": 1,
                "trace_request": {
                    "request_id": "request.logic.trace.protocol",
                    "subject_id": "net.logic.debug.protocol",
                    "measurement_point_ids": ["measure.logic.protocol_frame"],
                    "tick_start": 1,
                    "tick_end": 2,
                    "sampling_policy_id": "debug.sample.default",
                    "extensions": {
                        "targets": [
                            {
                                "subject_id": "net.logic.debug.protocol",
                                "network_id": "net.logic.debug.protocol",
                                "element_id": "inst.logic.bus.1",
                                "port_id": "bus.out",
                                "measurement_point_id": "measure.logic.protocol_frame",
                            }
                        ]
                    },
                },
                "authority_context": {"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
                "has_physical_access": True,
                "available_instrument_type_ids": ["instrument.protocol_sniffer_stub"],
            }
        ],
    }
    first = replay_trace_window_from_payload(repo_root=repo_root, payload=payload)
    second = replay_trace_window_from_payload(repo_root=repo_root, payload=payload)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "protocol trace replay fixture did not complete twice"}
    if str(first.get("logic_debug_trace_hash_chain", "")) != str(second.get("logic_debug_trace_hash_chain", "")):
        return {"status": "fail", "message": "trace replay hash chain drifted"}
    if str(first.get("logic_protocol_summary_hash_chain", "")) != str(second.get("logic_protocol_summary_hash_chain", "")):
        return {"status": "fail", "message": "protocol summary hash chain drifted"}
    if int(first.get("protocol_summary_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "protocol sniffer replay emitted no protocol summaries"}
    return {"status": "pass", "message": "trace replay hashes remain stable, including protocol summaries"}
