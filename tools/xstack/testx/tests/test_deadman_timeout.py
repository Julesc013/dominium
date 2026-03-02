"""FAST test: deadman/watchdog pattern applies deterministic stop effect after timeout."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_deadman_timeout"
TEST_TAGS = ["fast", "safety", "deadman", "watchdog"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context, seed_switch_state

    target_id = "machine.safety.watchdog"
    state = seed_switch_state(base_state(current_tick=25), machine_id=target_id)
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.deadman.main",
            "pattern_id": "safety.deadman_basic",
            "target_ids": [target_id],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["safety_runtime_state"] = {
        "schema_version": "1.0.0",
        "last_tick": 0,
        "last_budget_outcome": "complete",
        "last_processed_instance_count": 0,
        "last_deferred_instance_count": 0,
        "last_triggered_instance_count": 0,
        "last_event_count": 0,
        "heartbeat_rows": [
            {
                "target_id": target_id,
                "last_heartbeat_tick": 10,
                "timeout_ticks": 5,
            }
        ],
        "extensions": {},
    }
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.safety.deadman.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {},
        },
        law_profile=copy.deepcopy(law_profile(["process.safety_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "safety tick failed for deadman fixture"}
    effect_rows = [dict(row) for row in list(state.get("effect_rows") or []) if isinstance(row, dict)]
    matches = [
        row
        for row in effect_rows
        if str(row.get("target_id", "")).strip() == target_id
        and str(row.get("effect_type_id", "")).strip() == "effect.speed_cap"
    ]
    if not matches:
        return {"status": "fail", "message": "deadman timeout should apply effect.speed_cap to target"}
    return {"status": "pass", "message": "deadman timeout applied deterministic speed-cap effect"}
