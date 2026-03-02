"""FAST test: macro travel tick progress is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.travel.tick_progress_deterministic"
TEST_TAGS = ["fast", "mobility", "travel", "tick", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    allowed = ["process.itinerary_create", "process.travel_start", "process.travel_tick"]
    state = seed_state()
    law = law_profile(allowed)
    authority = authority_context()
    policy = policy_context()

    itinerary = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.tick.itinerary.001",
            "process_id": "process.itinerary_create",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "graph_id": "graph.mob.travel.alpha",
                "from_node_id": "node.mob.travel.a",
                "to_node_id": "node.mob.travel.b",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(itinerary.get("result", "")) != "complete":
        return {"result": itinerary, "state": state}
    itinerary_id = str(itinerary.get("itinerary_id", "")).strip()

    start = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.tick.start.001",
            "process_id": "process.travel_start",
            "inputs": {"vehicle_id": "vehicle.mob.travel.alpha", "itinerary_id": itinerary_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(start.get("result", "")) != "complete":
        return {"result": start, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.tick.run.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_vehicle_updates_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": ticked, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "travel_tick fixture failed to execute deterministically"}
    first_states = [
        dict(row)
        for row in list((dict(first.get("state") or {})).get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.travel.alpha"
    ]
    second_states = [
        dict(row)
        for row in list((dict(second.get("state") or {})).get("vehicle_motion_states") or [])
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.travel.alpha"
    ]
    if not first_states or not second_states:
        return {"status": "fail", "message": "missing vehicle motion state row after travel_tick"}
    first_macro = dict(first_states[0].get("macro_state") or {})
    second_macro = dict(second_states[0].get("macro_state") or {})
    if int(first_macro.get("progress_fraction_q16", 0)) <= 0:
        return {"status": "fail", "message": "travel_tick did not advance macro progress fraction"}
    if first_macro != second_macro:
        return {"status": "fail", "message": "macro progress state drifted across equivalent travel_tick runs"}
    if list((dict(first.get("state") or {})).get("travel_events") or []) != list((dict(second.get("state") or {})).get("travel_events") or []):
        return {"status": "fail", "message": "travel event rows drifted across equivalent travel_tick runs"}
    return {"status": "pass", "message": "macro travel tick progress deterministic"}

