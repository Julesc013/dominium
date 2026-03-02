"""FAST test: itinerary creation refuses spec-incompatible vehicle/edge pairing."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.travel.spec_noncompliance_refusal"
TEST_TAGS = ["fast", "mobility", "travel", "spec", "refusal"]


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

    state = seed_state(vehicle_gauge_mm=1000, edge_gauge_mm=1435)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.travel.spec.refusal.001",
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
        policy_context=copy.deepcopy(policy_context(vehicle_gauge_mm=1000, edge_gauge_mm=1435)),
    )
    if str(result.get("result", "")) == "complete":
        return {"status": "fail", "message": "expected spec-noncompliance refusal but itinerary_create completed"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.mob.spec_noncompliant":
        return {"status": "fail", "message": "expected refusal.mob.spec_noncompliant for itinerary_create"}
    return {"status": "pass", "message": "itinerary_create spec noncompliance refusal emitted deterministically"}

