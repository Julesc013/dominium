"""FAST test: fail-safe pattern drives signal state to STOP on fault predicates."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fail_safe_defaults"
TEST_TAGS = ["fast", "safety", "failsafe", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context, seed_signal_state

    signal_id = "signal.safety.fail_safe"
    machine_id = "state_machine.safety.fail_safe"
    state = seed_signal_state(
        base_state(current_tick=12),
        signal_id=signal_id,
        machine_id=machine_id,
        initial_aspect="clear",
    )
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.fail_safe.main",
            "pattern_id": "safety.fail_safe_stop",
            "target_ids": [signal_id],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.safety.fail_safe.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {
                "condition_overrides": {
                    signal_id: {
                        "hazard.active": True,
                    }
                }
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.safety_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "safety tick failed for fail-safe fixture"}
    machine_rows = [dict(row) for row in list(state.get("mobility_signal_state_machines") or []) if isinstance(row, dict)]
    machine_row = {}
    for row in machine_rows:
        if str(row.get("machine_id", "")).strip() == machine_id:
            machine_row = dict(row)
            break
    if not machine_row:
        return {"status": "fail", "message": "missing signal state machine row after fail-safe evaluation"}
    if str(machine_row.get("state_id", "")).strip().lower() != "stop":
        return {"status": "fail", "message": "fail-safe should transition signal state to stop"}
    return {"status": "pass", "message": "fail-safe defaults enforced deterministic stop state"}
