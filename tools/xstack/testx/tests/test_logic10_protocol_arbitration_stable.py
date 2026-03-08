"""STRICT test: LOGIC-10 protocol arbitration remains deterministic under contention."""

from __future__ import annotations

import sys


TEST_ID = "test_protocol_arbitration_stable"
TEST_TAGS = ["strict", "logic", "envelope", "protocol", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.tool_run_logic_protocol_stress import run_protocol_stress

    first = run_protocol_stress(repo_root=repo_root, frame_count=12, tick_count=6, use_sig=False)
    second = run_protocol_stress(repo_root=repo_root, frame_count=12, tick_count=6, use_sig=False)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "protocol arbitration stress fixture did not complete twice"}
    for key in (
        "deterministic_fingerprint",
        "logic_protocol_frame_hash_chain",
        "logic_protocol_event_hash_chain",
        "max_queue_depth",
        "blocked_event_count",
    ):
        if first.get(key) != second.get(key):
            return {"status": "fail", "message": "protocol arbitration drifted for '{}'".format(key)}
    return {"status": "pass", "message": "protocol arbitration is stable under deterministic contention"}
