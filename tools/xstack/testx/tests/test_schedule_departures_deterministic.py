"""FAST test: timetable-triggered departures are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.travel.schedule_departures_deterministic"
TEST_TAGS = ["fast", "mobility", "travel", "schedule", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    allowed = [
        "process.itinerary_create",
        "process.travel_schedule_set",
        "process.travel_tick",
    ]
    state = seed_state()
    law = law_profile(allowed)
    authority = authority_context()
    policy = policy_context()

    itinerary = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.schedule.itinerary.001",
            "process_id": "process.itinerary_create",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "graph_id": "graph.mob.travel.alpha",
                "from_node_id": "node.mob.travel.a",
                "to_node_id": "node.mob.travel.b",
                "departure_tick": 0,
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

    scheduled = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.schedule.set.001",
            "process_id": "process.travel_schedule_set",
            "inputs": {
                "schedule_id": "schedule.mob.travel.alpha",
                "vehicle_id": "vehicle.mob.travel.alpha",
                "itinerary_id": itinerary_id,
                "start_tick": 0,
                "active": True,
                "recurrence_rule": {"rule_type": "none", "interval_ticks": 0, "trigger_process_id": "process.travel_start"},
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(scheduled.get("result", "")) != "complete":
        return {"result": scheduled, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.schedule.tick.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_schedule_updates_per_tick": 8, "max_vehicle_updates_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": ticked, "state": state, "itinerary_id": itinerary_id}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "travel_tick schedule fixture failed"}
    if list((dict(first.get("state") or {})).get("travel_events") or []) != list((dict(second.get("state") or {})).get("travel_events") or []):
        return {"status": "fail", "message": "schedule-triggered travel events drifted across equivalent runs"}
    first_events = [
        dict(row)
        for row in list((dict(first.get("state") or {})).get("travel_events") or [])
        if isinstance(row, dict) and str(row.get("kind", "")).strip() == "depart"
    ]
    if not first_events:
        return {"status": "fail", "message": "schedule tick did not produce depart event"}
    return {"status": "pass", "message": "timetable departures deterministic and event-sourced"}

