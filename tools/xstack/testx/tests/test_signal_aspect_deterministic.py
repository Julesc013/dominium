"""FAST test: signal aspect evaluation is deterministic under identical state."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.signal_aspect_deterministic"
TEST_TAGS = ["fast", "mobility", "signal", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_signal_testlib import authority_context, law_profile, policy_context, seed_signal_state

    state = seed_signal_state(signal_count=2, initial_aspect="clear", initial_velocity=0)
    state["edge_occupancies"] = [
        {
            "schema_version": "1.0.0",
            "edge_id": "edge.mob.micro.main",
            "capacity_units": 1,
            "current_occupancy": 1,
            "congestion_ratio": 1.0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.tick.det.001",
            "process_id": "process.signal_tick",
            "inputs": {"max_signal_updates_per_tick": 8},
        },
        law_profile=copy.deepcopy(law_profile(["process.signal_tick"])),
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
        return {"status": "fail", "message": "signal tick fixture failed"}

    first_rows = list((dict(first.get("state") or {})).get("mobility_signal_state_machines") or [])
    second_rows = list((dict(second.get("state") or {})).get("mobility_signal_state_machines") or [])
    if first_rows != second_rows:
        return {"status": "fail", "message": "signal state machines drifted across identical signal tick runs"}
    if not first_rows:
        return {"status": "fail", "message": "missing signal state machine rows after signal tick"}
    if any(str(dict(row).get("state_id", "")).strip().lower() != "stop" for row in first_rows if isinstance(row, dict)):
        return {"status": "fail", "message": "occupied edge should force STOP aspect for all attached signals"}

    keys = ("processed_signal_ids", "deferred_signal_ids", "budget_outcome", "cost_units")
    for key in keys:
        if first_result.get(key) != second_result.get(key):
            return {"status": "fail", "message": "signal tick metadata '{}' drifted across identical runs".format(key)}
    return {"status": "pass", "message": "signal aspect evaluation deterministic"}

