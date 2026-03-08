"""STRICT test: LOGIC-10 replay window proof hashes remain stable for bounded fixtures."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_window_hash_match"
TEST_TAGS = ["strict", "logic", "envelope", "replay", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.logic10_stress_common import generate_logic_stress_scenario
    from tools.logic.tool_replay_logic_window import replay_logic_window_from_payload

    scenario = generate_logic_stress_scenario(
        repo_root=repo_root,
        seed=1010,
        tick_count=4,
        network_count=4,
        mega_node_count=1_000_000,
    )
    payload = dict(dict(scenario.get("scale_networks") or {}).get("eval_uncompiled_payload") or {})
    first = replay_logic_window_from_payload(repo_root=repo_root, payload=payload)
    second = replay_logic_window_from_payload(repo_root=repo_root, payload=payload)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic replay window did not complete twice"}
    for key in (
        "deterministic_fingerprint",
        "logic_eval_record_hash_chain",
        "logic_throttle_event_hash_chain",
        "logic_output_signal_hash_chain",
        "forced_expand_event_hash_chain",
    ):
        if first.get(key) != second.get(key):
            return {"status": "fail", "message": "logic replay proof surface drifted for '{}'".format(key)}
    return {"status": "pass", "message": "logic replay window proof hashes are stable"}
