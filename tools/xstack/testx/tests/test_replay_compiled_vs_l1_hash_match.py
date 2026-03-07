"""STRICT test: LOGIC-6 compiled replay matches L1 output/state hashes on eligible fixtures."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_compiled_vs_l1_hash_match"
TEST_TAGS = ["strict", "logic", "compile", "replay", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.tool_replay_compiled_logic_window import replay_compiled_logic_window_from_payload
    from tools.xstack.testx.tests._logic_eval_test_utils import (
        load_eval_inputs,
        make_chain_network,
        seed_signal_requests,
    )

    inputs = load_eval_inputs(repo_root)
    _, logic_network_state = make_chain_network(network_id="net.logic.compile.replay_match")
    signal_store_state = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "network_id": "net.logic.compile.replay_match",
                "element_id": "inst.logic.and.1",
                "port_id": "in.a",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
            {
                "network_id": "net.logic.compile.replay_match",
                "element_id": "inst.logic.and.1",
                "port_id": "in.b",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
        ],
        inputs=inputs,
    )
    scenario = {
        "logic_network_state": logic_network_state,
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [
            {"tick": 1, "network_id": "net.logic.compile.replay_match"},
            {"tick": 2, "network_id": "net.logic.compile.replay_match"},
        ],
    }
    report = replay_compiled_logic_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "compiled replay parity fixture did not complete: {}".format(report.get("reason_code"))}
    if not bool(report.get("compiled_path_observed", False)):
        return {"status": "fail", "message": "compiled replay parity fixture never observed the compiled path"}
    if not bool(report.get("signals_match", False)) or not bool(report.get("states_match", False)):
        return {"status": "fail", "message": "compiled replay parity fixture drifted from L1"}
    if not bool(report.get("tick_signal_match", False)):
        return {"status": "fail", "message": "compiled replay tick-by-tick signal hashes drifted from L1"}
    return {"status": "pass", "message": "compiled replay matches L1 output/state hashes"}
