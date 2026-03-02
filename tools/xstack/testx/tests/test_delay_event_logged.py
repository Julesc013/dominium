"""FAST test: congestion-induced macro delay emits explicit deterministic travel events."""

from __future__ import annotations

import copy
import sys

TEST_ID = "testx.mobility.traffic.delay_event_logged"
TEST_TAGS = ["fast", "mobility", "traffic", "congestion", "events"]


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
            "intent_id": "intent.mob.traffic.delay.itinerary.alpha.001",
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
            "intent_id": "intent.mob.traffic.delay.itinerary.beta.001",
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
            "intent_id": "intent.mob.traffic.delay.start.alpha.001",
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
            "intent_id": "intent.mob.traffic.delay.start.beta.001",
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
            "intent_id": "intent.mob.traffic.delay.tick.001",
            "process_id": "process.travel_tick",
            "inputs": {"max_vehicle_updates_per_tick": 8},
        }
    )
    return {"result": ticked, "state": state}


def _congestion_delay_events(state: dict) -> list[dict]:
    rows = [dict(row) for row in list(state.get("travel_events") or []) if isinstance(row, dict)]
    out = []
    for row in rows:
        if str(row.get("kind", "")).strip() != "delay":
            continue
        details = dict(row.get("details") or {})
        if str(details.get("reason", "")).strip() != "event.delay.congestion":
            continue
        out.append(row)
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "congestion delay fixture failed"}

    first_delay_events = _congestion_delay_events(dict(first.get("state") or {}))
    second_delay_events = _congestion_delay_events(dict(second.get("state") or {}))
    if not first_delay_events or not second_delay_events:
        return {"status": "fail", "message": "expected congestion delay events were not logged"}
    if first_delay_events != second_delay_events:
        return {"status": "fail", "message": "congestion delay event payload drifted across runs"}
    if int(first_result.get("congestion_delay_count", 0)) <= 0:
        return {"status": "fail", "message": "travel_tick did not report congestion_delay_count"}
    traffic_logs = [dict(row) for row in list((dict(first.get("state") or {})).get("mobility_traffic_decision_logs") or []) if isinstance(row, dict)]
    if not traffic_logs:
        return {"status": "fail", "message": "missing mobility_traffic_decision_logs for congestion delay"}
    return {"status": "pass", "message": "congestion delay events and decision logs are deterministic"}

