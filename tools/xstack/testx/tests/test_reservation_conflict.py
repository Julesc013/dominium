"""FAST test: overlapping reservations deterministically refuse when capacity is exceeded."""

from __future__ import annotations

import copy
import sys

TEST_ID = "testx.mobility.traffic.reservation_conflict"
TEST_TAGS = ["fast", "mobility", "traffic", "reservation", "refusal"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_state,
    )

    state = seed_state()
    law = law_profile(["process.mobility_reserve_edge"])
    authority = authority_context()
    policy = policy_context()

    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.traffic.reserve.first.001",
            "process_id": "process.mobility_reserve_edge",
            "inputs": {
                "graph_id": "graph.mob.travel.alpha",
                "vehicle_id": "vehicle.mob.travel.alpha",
                "edge_id": "edge.mob.travel.ab",
                "start_tick": 0,
                "end_tick": 12,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.traffic.reserve.second.001",
            "process_id": "process.mobility_reserve_edge",
            "inputs": {
                "graph_id": "graph.mob.travel.alpha",
                "vehicle_id": "vehicle.mob.travel.beta",
                "edge_id": "edge.mob.travel.ab",
                "start_tick": 0,
                "end_tick": 12,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"first": first, "second": second}


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
        return {"status": "fail", "message": "initial reservation should complete"}
    if str(first_second.get("result", "")) != "refused" or str(second_second.get("result", "")) != "refused":
        return {"status": "fail", "message": "conflicting reservation should refuse"}

    reason_a = str(dict(first_second.get("refusal") or {}).get("reason_code", "")).strip()
    reason_b = str(dict(second_second.get("refusal") or {}).get("reason_code", "")).strip()
    if reason_a != "refusal.mob.reservation_conflict" or reason_b != "refusal.mob.reservation_conflict":
        return {"status": "fail", "message": "reservation conflict refusal code mismatch"}
    if first_second != second_second:
        return {"status": "fail", "message": "reservation conflict refusal payload drifted across runs"}
    return {"status": "pass", "message": "reservation conflict deterministic and explicit"}

