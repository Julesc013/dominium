"""FAST test: safety instance evaluation/defer ordering is deterministic by instance_id."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_deterministic_ordering_of_instances"
TEST_TAGS = ["fast", "safety", "ordering", "determinism", "budget"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context, seed_switch_state

    state = seed_switch_state(base_state(current_tick=15), machine_id="machine.safety.ordering")
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.02",
            "pattern_id": "safety.interlock_block",
            "target_ids": ["instance.target.02"],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.01",
            "pattern_id": "safety.interlock_block",
            "target_ids": ["instance.target.01"],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.safety.ordering.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {
                "max_instance_updates_per_tick": 1,
                "condition_overrides": {
                    "instance.target.01": {"mob.edge.current_occupancy": 1},
                    "instance.target.02": {"mob.edge.current_occupancy": 1},
                },
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.safety_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "safety ordering fixture failed"}
    for key in ("processed_instance_ids", "deferred_instance_ids", "triggered_instance_ids", "budget_outcome"):
        if first_result.get(key) != second_result.get(key):
            return {"status": "fail", "message": "safety ordering metadata drifted across identical runs for '{}'".format(key)}
    if list(first_result.get("processed_instance_ids") or []) != ["instance.safety.01"]:
        return {"status": "fail", "message": "processed instances should be deterministically sorted by instance_id"}
    if list(first_result.get("deferred_instance_ids") or []) != ["instance.safety.02"]:
        return {"status": "fail", "message": "deferred instances should preserve deterministic ordering"}
    return {"status": "pass", "message": "safety instance ordering deterministic under budget constraints"}
