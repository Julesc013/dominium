"""FAST test: route block reservation conflicts resolve deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.route_reservation_conflict_deterministic"
TEST_TAGS = ["fast", "mobility", "signal", "reservation", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_signal_testlib import authority_context, law_profile, policy_context
    from tools.xstack.testx.tests.mobility_travel_testlib import seed_state

    state = seed_state()
    law = law_profile(["process.itinerary_create", "process.route_reserve_blocks"])
    authority = authority_context()
    policy = policy_context()

    create = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.route.reserve.itinerary.001",
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
    if str(create.get("result", "")) != "complete":
        return {"result": create, "state": state}
    itinerary_id = str(create.get("itinerary_id", "")).strip()
    if not itinerary_id:
        return {"result": {"result": "refused"}, "state": state}

    first_reserve = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.route.reserve.first.001",
            "process_id": "process.route_reserve_blocks",
            "inputs": {"vehicle_id": "vehicle.mob.travel.alpha", "itinerary_id": itinerary_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second_reserve = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.signal.route.reserve.second.001",
            "process_id": "process.route_reserve_blocks",
            "inputs": {"vehicle_id": "vehicle.mob.travel.alpha", "itinerary_id": itinerary_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"first": first_reserve, "second": second_reserve, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()

    first_first = dict(first.get("first") or {})
    first_second = dict(first.get("second") or {})
    second_first = dict(second.get("first") or {})
    second_second = dict(second.get("second") or {})

    if str(first_first.get("result", "")) != "complete" or str(second_first.get("result", "")) != "complete":
        return {"status": "fail", "message": "initial route_reserve_blocks should complete in fixture"}
    if str(first_second.get("result", "")) == "complete" or str(second_second.get("result", "")) == "complete":
        return {"status": "fail", "message": "second route_reserve_blocks call should conflict deterministically"}

    refusal_a = dict(first_second.get("refusal") or {})
    refusal_b = dict(second_second.get("refusal") or {})
    if str(refusal_a.get("reason_code", "")).strip() != "refusal.mob.signal_violation":
        return {"status": "fail", "message": "expected refusal.mob.signal_violation for reservation conflict"}
    if refusal_a != refusal_b:
        return {"status": "fail", "message": "reservation conflict refusal details drifted across runs"}
    return {"status": "pass", "message": "route reservation conflict deterministic"}

