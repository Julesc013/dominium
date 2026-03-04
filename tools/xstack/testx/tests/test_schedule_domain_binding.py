"""FAST test: schedule execution resolves non-canonical temporal domains deterministically."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_schedule_domain_binding"
TEST_TAGS = ["fast", "time", "temp1", "schedule"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

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
    policy["session_warp_factor"] = 2000

    itinerary = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.temp1.schedule.itinerary.001",
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
        return {"status": "fail", "message": "itinerary_create failed: {}".format(itinerary)}

    itinerary_id = str(itinerary.get("itinerary_id", "")).strip()
    scheduled = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.temp1.schedule.bind.001",
            "process_id": "process.travel_schedule_set",
            "inputs": {
                "schedule_id": "schedule.temp1.warp.alpha",
                "vehicle_id": "vehicle.mob.travel.alpha",
                "itinerary_id": itinerary_id,
                "temporal_domain_id": "time.warp",
                "target_time_value": 0,
                "evaluation_policy_id": "schedule.eval.gte_target",
                "active": True,
                "recurrence_rule": {
                    "rule_type": "none",
                    "interval_ticks": 0,
                    "trigger_process_id": "process.travel_start",
                },
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(scheduled.get("result", "")) != "complete":
        return {"status": "fail", "message": "travel_schedule_set failed: {}".format(scheduled)}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.temp1.schedule.tick.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_schedule_updates_per_tick": 8, "max_vehicle_updates_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "travel_tick failed: {}".format(ticked)}

    bindings = [
        dict(row)
        for row in list(state.get("schedule_time_bindings") or [])
        if isinstance(row, dict) and str(row.get("schedule_id", "")).strip() == "schedule.temp1.warp.alpha"
    ]
    if not bindings:
        return {"status": "fail", "message": "schedule_time_binding row missing for non-canonical schedule"}
    if str(bindings[0].get("temporal_domain_id", "")).strip() != "time.warp":
        return {"status": "fail", "message": "schedule_time_binding temporal_domain_id not persisted"}

    evaluations = [
        dict(row)
        for row in list(state.get("schedule_domain_evaluations") or [])
        if isinstance(row, dict) and str(row.get("schedule_id", "")).strip() == "schedule.temp1.warp.alpha"
    ]
    if not evaluations:
        return {"status": "fail", "message": "schedule domain evaluations were not emitted"}
    if not any(str(row.get("temporal_domain_id", "")).strip() == "time.warp" for row in evaluations):
        return {"status": "fail", "message": "schedule domain evaluations missing time.warp row"}

    schedule_hash = str(state.get("schedule_domain_evaluation_hash", "")).strip().lower()
    if not _HASH64.fullmatch(schedule_hash):
        return {"status": "fail", "message": "schedule_domain_evaluation_hash missing or invalid"}

    return {"status": "pass", "message": "non-canonical schedule domain binding is enforced deterministically"}
