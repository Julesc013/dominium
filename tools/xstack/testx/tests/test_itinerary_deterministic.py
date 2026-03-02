"""FAST test: MOB-4 itinerary creation is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.travel.itinerary_deterministic"
TEST_TAGS = ["fast", "mobility", "travel", "itinerary", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.itinerary.det.001",
            "process_id": "process.itinerary_create",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "graph_id": "graph.mob.travel.alpha",
                "from_node_id": "node.mob.travel.a",
                "to_node_id": "node.mob.travel.b",
                "speed_policy_id": "speed_policy.spec_based",
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.itinerary_create"])),
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
        return {"status": "fail", "message": "itinerary_create refused in deterministic fixture"}
    if str(first_result.get("itinerary_id", "")).strip() != str(second_result.get("itinerary_id", "")).strip():
        return {"status": "fail", "message": "itinerary_id drifted across equivalent itinerary_create runs"}
    if list((dict(first.get("state") or {})).get("itineraries") or []) != list((dict(second.get("state") or {})).get("itineraries") or []):
        return {"status": "fail", "message": "itinerary rows drifted across equivalent runs"}
    return {"status": "pass", "message": "itinerary_create deterministic across equivalent macro travel inputs"}

