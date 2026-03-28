"""FAST test: locked switch refuses switch_set_state transitions."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.switch_lock_refusal"
TEST_TAGS = ["fast", "mobility", "switch", "signal", "interlocking"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from mobility.signals import build_switch_lock, deterministic_switch_lock_id
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import seed_switch_handoff_state
    from tools.xstack.testx.tests.mobility_signal_testlib import authority_context, law_profile, policy_context

    state = seed_switch_handoff_state()
    machine_id = "state_machine.mob.micro.switch"
    state["mobility_switch_state_machines"] = [
        {
            "schema_version": "1.0.0",
            "machine_id": machine_id,
            "machine_type_id": "state_machine.mobility.switch",
            "state_id": "edge.mob.micro.branch",
            "transitions": [
                "transition.mob.switch.to.main",
                "transition.mob.switch.to.branch",
            ],
            "transition_rows": [
                {
                    "schema_version": "1.0.0",
                    "transition_id": "transition.mob.switch.to.main",
                    "from_state": "edge.mob.micro.branch",
                    "to_state": "edge.mob.micro.main",
                    "trigger_process_id": "process.switch_set_state",
                    "guard_conditions": {},
                    "priority": 0,
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "transition_id": "transition.mob.switch.to.branch",
                    "from_state": "edge.mob.micro.main",
                    "to_state": "edge.mob.micro.branch",
                    "trigger_process_id": "process.switch_set_state",
                    "guard_conditions": {},
                    "priority": 0,
                    "extensions": {},
                },
            ],
            "extensions": {},
        }
    ]
    state["mobility_switch_locks"] = [
        build_switch_lock(
            switch_lock_id=deterministic_switch_lock_id(machine_id=machine_id, switch_node_id="node.mob.micro.main.b"),
            machine_id=machine_id,
            switch_node_id="node.mob.micro.main.b",
            status="locked",
            locked_tick=0,
            reason_code="manual_lock",
            extensions={},
        )
    ]

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.switch.lock.refusal.001",
            "process_id": "process.switch_set_state",
            "inputs": {
                "machine_id": machine_id,
                "target_edge_id": "edge.mob.micro.main",
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.switch_set_state"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "switch_set_state should refuse when switch is locked"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.mob.signal_violation":
        return {"status": "fail", "message": "expected refusal.mob.signal_violation for locked switch"}
    return {"status": "pass", "message": "locked switch deterministically refused"}
