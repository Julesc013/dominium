"""FAST test: safety interlock pattern deterministically locks conflicting switch transitions."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_interlock_prevents_conflict"
TEST_TAGS = ["fast", "safety", "interlock", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context, seed_switch_state

    machine_id = "machine.safety.switch.main"
    state = seed_switch_state(base_state(current_tick=10), machine_id=machine_id)
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.interlock.main",
            "pattern_id": "safety.interlock_block",
            "target_ids": [machine_id],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.safety.interlock.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {
                "condition_overrides": {
                    machine_id: {
                        "mob.edge.current_occupancy": 1,
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
        return {"status": "fail", "message": "safety tick failed for interlock fixture"}
    lock_rows = [dict(row) for row in list(state.get("mobility_switch_locks") or []) if isinstance(row, dict)]
    lock_row = {}
    for row in lock_rows:
        if str(row.get("machine_id", "")).strip() == machine_id:
            lock_row = dict(row)
            break
    if not lock_row:
        return {"status": "fail", "message": "interlock did not produce switch lock row"}
    if str(lock_row.get("status", "")).strip() != "locked":
        return {"status": "fail", "message": "switch lock status should be locked under interlock conflict"}
    return {"status": "pass", "message": "interlock conflict deterministically locked switch"}
