"""FAST test: travel_tick budget degradation is deterministic under identical load."""

from __future__ import annotations

import copy
import sys

TEST_ID = "testx.mobility.traffic.budget_degrade_stable"
TEST_TAGS = ["fast", "mobility", "traffic", "budget", "degrade", "determinism"]


def _seed_two_vehicle_state() -> dict:
    from src.mobility.vehicle.vehicle_engine import (
        build_motion_state,
        build_vehicle,
        deterministic_motion_state_ref,
    )
    from tools.xstack.testx.tests.mobility_travel_testlib import seed_state

    state = seed_state()
    vehicle_id = "vehicle.mob.travel.beta"
    state["vehicles"] = list(state.get("vehicles") or []) + [
        build_vehicle(
            vehicle_id=vehicle_id,
            parent_structure_instance_id=None,
            vehicle_class_id="veh.rail_handcart",
            spatial_id="spatial.mob.travel.alpha",
            spec_ids=["spec.mob.travel.vehicle"],
            capability_bindings={},
            port_ids=[],
            interior_graph_id=None,
            pose_slot_ids=[],
            mount_point_ids=[],
            motion_state_ref=deterministic_motion_state_ref(vehicle_id=vehicle_id),
            hazard_ids=[],
            maintenance_policy_id="maintenance.policy.default",
            extensions={},
        )
    ]
    state["vehicle_motion_states"] = list(state.get("vehicle_motion_states") or []) + [
        build_motion_state(
            vehicle_id=vehicle_id,
            tier="macro",
            macro_state={},
            meso_state={},
            micro_state={},
            last_update_tick=0,
            extensions={},
        )
    ]
    return state


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_travel_testlib import (
        authority_context,
        law_profile,
        policy_context,
    )

    state = _seed_two_vehicle_state()
    law = law_profile(["process.itinerary_create", "process.travel_start", "process.travel_tick"])
    authority = authority_context()
    policy = policy_context()

    def _exec(intent: dict) -> dict:
        return execute_intent(
            state=state,
            intent=intent,
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )

    itinerary_alpha = _exec(
        {
            "intent_id": "intent.mob.traffic.budget.itinerary.alpha.001",
            "process_id": "process.itinerary_create",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "graph_id": "graph.mob.travel.alpha",
                "from_node_id": "node.mob.travel.a",
                "to_node_id": "node.mob.travel.b",
            },
        }
    )
    if str(itinerary_alpha.get("result", "")) != "complete":
        return {"result": itinerary_alpha, "state": state}
    itinerary_beta = _exec(
        {
            "intent_id": "intent.mob.traffic.budget.itinerary.beta.001",
            "process_id": "process.itinerary_create",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.beta",
                "graph_id": "graph.mob.travel.alpha",
                "from_node_id": "node.mob.travel.a",
                "to_node_id": "node.mob.travel.b",
            },
        }
    )
    if str(itinerary_beta.get("result", "")) != "complete":
        return {"result": itinerary_beta, "state": state}

    start_alpha = _exec(
        {
            "intent_id": "intent.mob.traffic.budget.start.alpha.001",
            "process_id": "process.travel_start",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.alpha",
                "itinerary_id": str(itinerary_alpha.get("itinerary_id", "")).strip(),
            },
        }
    )
    if str(start_alpha.get("result", "")) != "complete":
        return {"result": start_alpha, "state": state}
    start_beta = _exec(
        {
            "intent_id": "intent.mob.traffic.budget.start.beta.001",
            "process_id": "process.travel_start",
            "inputs": {
                "vehicle_id": "vehicle.mob.travel.beta",
                "itinerary_id": str(itinerary_beta.get("itinerary_id", "")).strip(),
            },
        }
    )
    if str(start_beta.get("result", "")) != "complete":
        return {"result": start_beta, "state": state}

    ticked = _exec(
        {
            "intent_id": "intent.mob.traffic.budget.tick.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_vehicle_updates_per_tick": 1},
        }
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
        return {"status": "fail", "message": "budget degrade fixture failed"}
    if str(first_result.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome under max_vehicle_updates_per_tick=1"}

    fields = (
        "processed_vehicle_ids",
        "deferred_vehicle_ids",
        "budget_deferred_vehicle_ids",
        "cadence_deferred_vehicle_ids",
        "budget_outcome",
    )
    for key in fields:
        if first_result.get(key) != second_result.get(key):
            return {"status": "fail", "message": "budget degradation field '{}' drifted across runs".format(key)}
    if list(first_result.get("deferred_vehicle_ids") or []) != ["vehicle.mob.travel.beta"]:
        return {"status": "fail", "message": "expected deterministic deferred vehicle ordering by vehicle_id"}
    return {"status": "pass", "message": "budget degradation deterministic and stable"}

