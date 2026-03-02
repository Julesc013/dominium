"""FAST test: travel reenactment event-stream index is deterministic per itinerary."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.travel.reenactment_event_stream_index_deterministic"
TEST_TAGS = ["fast", "mobility", "travel", "reenactment", "determinism"]


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
            "intent_id": "intent.mob.travel.stream.itinerary.001",
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

    started = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.stream.start.001",
            "process_id": "process.travel_start",
            "inputs": {"vehicle_id": "vehicle.mob.travel.alpha", "itinerary_id": itinerary_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(started.get("result", "")) != "complete":
        return {"result": started, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.stream.tick.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_vehicle_updates_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"result": ticked, "state": state}

    stream_rows = sorted(
        [
            dict(row)
            for row in list(state.get("event_stream_indices") or [])
            if isinstance(row, dict) and str(row.get("target_id", "")).strip() == itinerary_id
        ],
        key=lambda row: str(row.get("stream_id", "")),
    )
    if not stream_rows:
        return {"result": {"result": "fail"}, "state": state}
    stream_row = dict(stream_rows[-1])
    return {
        "result": ticked,
        "state": state,
        "itinerary_id": itinerary_id,
        "stream_id": str(stream_row.get("stream_id", "")).strip(),
        "stream_hash": str(stream_row.get("stream_hash", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str((dict(first.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "first reenactment stream fixture run did not complete"}
    if str((dict(second.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "second reenactment stream fixture run did not complete"}
    if str(first.get("stream_id", "")) != str(second.get("stream_id", "")):
        return {"status": "fail", "message": "travel event stream id drifted across equivalent runs"}
    if str(first.get("stream_hash", "")) != str(second.get("stream_hash", "")):
        return {"status": "fail", "message": "travel event stream hash drifted across equivalent runs"}
    return {"status": "pass", "message": "travel reenactment event stream index deterministic per itinerary"}

