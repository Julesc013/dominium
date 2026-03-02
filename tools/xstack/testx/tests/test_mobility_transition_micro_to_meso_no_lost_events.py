"""STRICT test: micro->meso downgrade preserves prior event stream rows and state anchors."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.transition_micro_to_meso_no_lost_events"
TEST_TAGS = ["strict", "mobility", "transition", "determinism"]


def _event_ids(rows: object) -> list[str]:
    out = []
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        token = str(row.get("event_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.mobility.travel import build_travel_event, deterministic_travel_event_id
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_micro_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_micro_state,
    )

    state = seed_micro_state(initial_velocity=14, include_second_vehicle=True)
    state["travel_events"] = [
        build_travel_event(
            event_id=deterministic_travel_event_id(
                vehicle_id="vehicle.mob.micro.beta",
                itinerary_id="itinerary.mob.micro.beta",
                kind="incident_stub",
                tick=0,
                sequence=0,
            ),
            tick=0,
            vehicle_id="vehicle.mob.micro.beta",
            itinerary_id="itinerary.mob.micro.beta",
            kind="incident_stub",
            details={"reason_code": "event.seed"},
            extensions={"source_process_id": "test.seed"},
        )
    ]
    before_event_ids = _event_ids(state.get("travel_events"))
    before_beta_motion = {}
    for row in list(state.get("vehicle_motion_states") or []):
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.beta":
            before_beta_motion = dict(row)
            break
    if not before_beta_motion:
        return {"status": "fail", "message": "missing beta motion state before downgrade fixture"}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob.transition.micro_to_meso.001",
            "process_id": "process.mobility_micro_tick",
            "inputs": {
                "vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "roi_vehicle_ids": ["vehicle.mob.micro.alpha", "vehicle.mob.micro.beta"],
                "max_vehicle_updates_per_tick": 1,
                "downgrade_to_meso_on_budget": True,
                "control_inputs_by_vehicle": {
                    "vehicle.mob.micro.alpha": {"throttle_permille": 650, "brake_permille": 0},
                    "vehicle.mob.micro.beta": {"throttle_permille": 650, "brake_permille": 0},
                },
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.mobility_micro_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(ticked.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "micro->meso downgrade fixture refused"}
    deferred_ids = [str(item).strip() for item in list(ticked.get("deferred_vehicle_ids") or []) if str(item).strip()]
    if deferred_ids != ["vehicle.mob.micro.beta"]:
        return {"status": "fail", "message": "expected deterministic deferred vehicle ordering for downgrade"}

    after_event_ids = _event_ids(state.get("travel_events"))
    if not set(before_event_ids).issubset(set(after_event_ids)):
        return {"status": "fail", "message": "micro->meso downgrade lost prior travel event ids"}

    after_beta_motion = {}
    for row in list(state.get("vehicle_motion_states") or []):
        if isinstance(row, dict) and str(row.get("vehicle_id", "")).strip() == "vehicle.mob.micro.beta":
            after_beta_motion = dict(row)
            break
    if not after_beta_motion:
        return {"status": "fail", "message": "missing beta motion state after downgrade"}
    if str(after_beta_motion.get("tier", "")).strip() != "meso":
        return {"status": "fail", "message": "deferred beta vehicle did not collapse to meso"}

    before_micro = dict(before_beta_motion.get("micro_state") or {})
    after_micro = dict(after_beta_motion.get("micro_state") or {})
    if before_micro != after_micro:
        return {"status": "fail", "message": "micro->meso collapse changed stored micro anchor state"}
    return {"status": "pass", "message": "micro->meso downgrade preserved events and state anchors"}
