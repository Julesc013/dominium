"""FAST test: safety tick emits deterministic safety event records."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_safety_event_logged"
TEST_TAGS = ["fast", "safety", "events", "provenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context, seed_switch_state

    machine_id = "machine.safety.event"
    state = seed_switch_state(base_state(current_tick=8), machine_id=machine_id)
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.log.main",
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
            "intent_id": "intent.safety.log.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {
                "condition_overrides": {
                    machine_id: {"mob.edge.current_occupancy": 1},
                }
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.safety_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "safety tick failed for event logging fixture"}
    event_rows = [dict(row) for row in list(state.get("safety_events") or []) if isinstance(row, dict)]
    if not event_rows:
        return {"status": "fail", "message": "safety tick should emit at least one safety event"}
    matches = [
        row
        for row in event_rows
        if str(row.get("pattern_id", "")).strip() == "safety.interlock_block"
        and str(row.get("status", "")).strip() == "triggered"
    ]
    if not matches:
        return {"status": "fail", "message": "expected triggered safety.interlock_block event record"}
    return {"status": "pass", "message": "safety event logging deterministic and present"}
