"""FAST test: meso edge occupancy updates are deterministic."""

from __future__ import annotations

import copy
import sys

TEST_ID = "testx.mobility.traffic.occupancy_deterministic"
TEST_TAGS = ["fast", "mobility", "traffic", "occupancy", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    law = law_profile(["process.itinerary_create", "process.travel_start", "process.travel_tick"])
    authority = authority_context()
    policy = policy_context()

    itinerary = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.traffic.occupancy.itinerary.001",
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
            "intent_id": "intent.mob.traffic.occupancy.start.001",
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
            "intent_id": "intent.mob.traffic.occupancy.tick.001",
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
        return {"status": "fail", "message": "travel_tick occupancy fixture failed"}

    first_rows = [dict(row) for row in list((dict(first.get("state") or {})).get("edge_occupancies") or []) if isinstance(row, dict)]
    second_rows = [dict(row) for row in list((dict(second.get("state") or {})).get("edge_occupancies") or []) if isinstance(row, dict)]
    if first_rows != second_rows:
        return {"status": "fail", "message": "edge occupancy rows drifted across equivalent runs"}
    target_rows = [row for row in first_rows if str(row.get("edge_id", "")).strip() == "edge.mob.travel.ab"]
    if not target_rows:
        return {"status": "fail", "message": "missing occupancy row for edge.mob.travel.ab"}
    if int(target_rows[0].get("current_occupancy", -1)) != 1:
        return {"status": "fail", "message": "expected occupancy=1 for active single-vehicle edge"}
    return {"status": "pass", "message": "edge occupancy deterministic for equivalent macro travel runs"}

