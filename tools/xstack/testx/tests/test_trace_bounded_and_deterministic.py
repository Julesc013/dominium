"""STRICT test: LOGIC-7 traces remain bounded and deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_trace_bounded_and_deterministic"
TEST_TAGS = ["strict", "logic", "debug", "trace"]


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
                "network_id": "net.logic.debug.trace",
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
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
                    "request_id": "request.logic.trace.det",
                    "subject_id": "net.logic.debug.trace",
                    "measurement_point_ids": ["measure.logic.signal"],
                    "tick_start": 1,
                    "tick_end": 3,
                    "sampling_policy_id": "debug.sample.default",
                    "extensions": {
                        "targets": [
                            {
                                "subject_id": "net.logic.debug.trace",
                                "network_id": "net.logic.debug.trace",
                                "element_id": "inst.logic.and.1",
                                "port_id": "out.q",
                                "measurement_point_id": "measure.logic.signal",
                            }
                        ]
                    },
                },
                "authority_context": {"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
                "has_physical_access": True,
                "available_instrument_type_ids": ["instrument.logic_probe"],
            }
        ],
    }
    first = replay_trace_window_from_payload(repo_root=repo_root, payload=payload)
    second = replay_trace_window_from_payload(repo_root=repo_root, payload=payload)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "trace replay fixture did not complete twice"}
    if str(first.get("logic_debug_trace_hash_chain", "")) != str(second.get("logic_debug_trace_hash_chain", "")):
        return {"status": "fail", "message": "trace hash chain drifted across equivalent runs"}
    if int(first.get("trace_artifact_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "bounded trace replay emitted no trace artifacts"}
    if dict(first.get("final_logic_debug_state") or {}) != dict(second.get("final_logic_debug_state") or {}):
        return {"status": "fail", "message": "final logic debug state drifted across equivalent trace runs"}
    return {"status": "pass", "message": "trace capture is bounded and deterministic"}
