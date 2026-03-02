"""FAST test: MOB-10 boundary exchange uses deterministic FieldLayer sampling."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "test_boundary_field_exchange_deterministic"
TEST_TAGS = ["fast", "mobility", "interior", "fields", "determinism"]


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from mobility_interior_testlib import attach_field_layers, authority_context, law_profile, policy_context, seed_state
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = seed_state(include_vehicle=True, vehicle_position_x=100)
    state = attach_field_layers(
        state,
        cell_id="cell.mob10.exchange",
        temperature=14,
        moisture=610,
        friction=780,
        radiation=5,
        visibility=470,
        wind={"x": 300, "y": 0, "z": 0},
    )
    law = law_profile(["process.compartment_flow_tick"])
    auth = authority_context(["session.boot"], privilege_level="observer", visibility_level="diegetic")
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob10.boundary.exchange.001",
            "process_id": "process.compartment_flow_tick",
            "inputs": {"graph_id": "interior.graph.mob10.alpha", "dt_ticks": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "compartment_flow_tick refused in boundary fixture"}
    portal_row = next(
        (
            dict(row)
            for row in list(state.get("portal_flow_params") or [])
            if isinstance(row, dict) and str(row.get("portal_id", "")).strip() == "portal.mob10.cabin_hatch"
        ),
        {},
    )
    boundary = dict((dict(portal_row.get("extensions") or {})).get("field_boundary") or {})
    return {
        "status": "pass",
        "result": dict(result),
        "boundary": boundary,
        "conductance_air": int(portal_row.get("conductance_air", -1) or -1),
    }


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_sha256

    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if str(first.get("status", "")) != "pass":
        return first
    if str(second.get("status", "")) != "pass":
        return second

    first_payload = {
        "result": {
            "owner_vehicle_id": dict(first.get("result") or {}).get("owner_vehicle_id"),
            "owner_vehicle_motion_tier": dict(first.get("result") or {}).get("owner_vehicle_motion_tier"),
            "owner_vehicle_speed_mm_per_tick": dict(first.get("result") or {}).get("owner_vehicle_speed_mm_per_tick"),
            "field_boundary_portal_count": dict(first.get("result") or {}).get("field_boundary_portal_count"),
        },
        "boundary": dict(first.get("boundary") or {}),
        "conductance_air": int(first.get("conductance_air", -1) or -1),
    }
    second_payload = {
        "result": {
            "owner_vehicle_id": dict(second.get("result") or {}).get("owner_vehicle_id"),
            "owner_vehicle_motion_tier": dict(second.get("result") or {}).get("owner_vehicle_motion_tier"),
            "owner_vehicle_speed_mm_per_tick": dict(second.get("result") or {}).get("owner_vehicle_speed_mm_per_tick"),
            "field_boundary_portal_count": dict(second.get("result") or {}).get("field_boundary_portal_count"),
        },
        "boundary": dict(second.get("boundary") or {}),
        "conductance_air": int(second.get("conductance_air", -1) or -1),
    }
    if canonical_sha256(first_payload) != canonical_sha256(second_payload):
        return {"status": "fail", "message": "boundary exchange payload drifted across equivalent runs"}

    boundary = dict(first_payload.get("boundary") or {})
    sample_position = dict(boundary.get("sample_position_mm") or {})
    wind_vector = dict(boundary.get("wind_vector") or {})
    if int(boundary.get("temperature", -999) or -999) != 14:
        return {"status": "fail", "message": "boundary temperature sample mismatch"}
    if int(boundary.get("moisture", -999) or -999) != 610:
        return {"status": "fail", "message": "boundary moisture sample mismatch"}
    if int(boundary.get("visibility", -999) or -999) != 470:
        return {"status": "fail", "message": "boundary visibility sample mismatch"}
    if int(boundary.get("vehicle_speed_mm_per_tick", -1) or -1) != 80:
        return {"status": "fail", "message": "boundary exchange should include owner micro speed"}
    if int(boundary.get("wind_magnitude", -1) or -1) != 300:
        return {"status": "fail", "message": "wind magnitude mismatch in field boundary"}
    if int(boundary.get("ram_air_boost_air_conductance", -1) or -1) != 20:
        return {"status": "fail", "message": "ram-air boost mismatch"}
    if int(boundary.get("wind_boost_air_conductance", -1) or -1) != 170:
        return {"status": "fail", "message": "wind boost mismatch"}
    if int(sample_position.get("x", -1) or -1) != 125:
        return {"status": "fail", "message": "boundary sample position mismatch"}
    if int(wind_vector.get("x", 0) or 0) != 300:
        return {"status": "fail", "message": "wind vector sample mismatch"}
    if int(first_payload.get("conductance_air", -1) or -1) != 290:
        return {"status": "fail", "message": "portal conductance_air did not include deterministic wind/ram boost"}
    return {"status": "pass", "message": "boundary field exchange remains deterministic and field-driven"}

