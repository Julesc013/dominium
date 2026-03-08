"""STRICT test: LOGIC-10 security blocks are deterministic and logged."""

from __future__ import annotations

import sys


TEST_ID = "test_security_block_stable"
TEST_TAGS = ["strict", "logic", "envelope", "security", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.tool_replay_fault_window import replay_fault_window_from_payload
    from tools.logic.tool_run_logic_fault_stress import build_logic_fault_stress_scenario

    payload = build_logic_fault_stress_scenario(repo_root=repo_root, tick_count=6)
    first = replay_fault_window_from_payload(repo_root=repo_root, payload=payload)
    second = replay_fault_window_from_payload(repo_root=repo_root, payload=payload)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic fault/security replay fixture did not complete twice"}
    if int(first.get("security_fail_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "logic fault/security replay emitted no security block events"}
    for key in ("logic_security_fail_hash_chain", "deterministic_fingerprint", "security_fail_count"):
        if first.get(key) != second.get(key):
            return {"status": "fail", "message": "logic security block surface drifted for '{}'".format(key)}
    return {"status": "pass", "message": "logic security blocks are deterministic and logged"}
