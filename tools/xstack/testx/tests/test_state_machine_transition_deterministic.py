"""FAST test: core state-machine transition selection is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.state_machine_transition_deterministic"
TEST_TAGS = ["fast", "core", "state_machine", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from core.state.state_machine_engine import apply_transition
    from tools.xstack.compatx.canonical_json import canonical_sha256

    machine = {
        "schema_version": "1.0.0",
        "machine_id": "machine.state.test",
        "machine_type_id": "state_machine.test",
        "state_id": "idle",
        "transitions": [
            {
                "transition_id": "transition.high",
                "from_state_id": "idle",
                "to_state_id": "running",
                "trigger_process_id": "process.machine_start",
                "priority": 10,
                "extensions": {},
            },
            {
                "transition_id": "transition.low",
                "from_state_id": "idle",
                "to_state_id": "blocked",
                "trigger_process_id": "process.machine_start",
                "priority": 1,
                "extensions": {},
            },
        ],
        "extensions": {},
    }

    first = apply_transition(machine, trigger_process_id="process.machine_start", current_tick=50)
    second = apply_transition(machine, trigger_process_id="process.machine_start", current_tick=50)
    if first != second:
        return {"status": "fail", "message": "apply_transition returned non-deterministic outputs"}

    applied = dict(first.get("applied_transition") or {})
    if str(applied.get("transition_id", "")) != "transition.high":
        return {"status": "fail", "message": "state machine must choose highest-priority deterministic transition"}
    result_machine = dict(first.get("machine") or {})
    if str(result_machine.get("state_id", "")) != "running":
        return {"status": "fail", "message": "state machine resulting state mismatch"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "state machine output hash diverged"}

    return {"status": "pass", "message": "State-machine deterministic transition passed"}

