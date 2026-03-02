"""FAST test: MOB-10 interior sampling remains attached to vehicle motion/frame updates."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "test_vehicle_interior_moves_with_vehicle"
TEST_TAGS = ["fast", "mobility", "interior", "vehicle", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from mobility_interior_testlib import (
        attach_field_layers,
        authority_context,
        law_profile,
        policy_context,
        seed_state,
        set_vehicle_position,
    )
    from tools.xstack.sessionx.process_runtime import execute_intent

    vehicle_id = "vehicle.mob10.alpha"
    state = seed_state(include_vehicle=True, vehicle_position_x=100)
    state = attach_field_layers(
        state,
        cell_id="cell.mob10.alpha",
        temperature=12,
        moisture=450,
        visibility=840,
        wind={"x": 200, "y": 0, "z": 0},
    )
    law = law_profile(["process.vehicle_apply_environment_hooks", "process.compartment_flow_tick"])
    auth = authority_context(["session.boot"], privilege_level="observer", visibility_level="diegetic")
    policy = policy_context()

    hook = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob10.interior.frame_sync.001",
            "process_id": "process.vehicle_apply_environment_hooks",
            "inputs": {"vehicle_ids": [vehicle_id]},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(hook.get("result", "")) != "complete":
        return {"status": "fail", "message": "vehicle frame-sync hook refused unexpectedly"}
    frame_updates = dict(hook.get("interior_frame_updates") or {})
    if int(frame_updates.get("updated_volume_count", 0) or 0) < 1:
        return {"status": "fail", "message": "frame-sync did not attach interior volumes to vehicle spatial frame"}
    if any(
        str(dict(row).get("parent_spatial_id", "")).strip() != "spatial.vehicle.alpha"
        for row in list(state.get("interior_volumes") or [])
        if isinstance(row, dict)
    ):
        return {"status": "fail", "message": "interior volume parent_spatial_id did not normalize to vehicle spatial node"}

    def _sample_x(intent_id: str) -> int:
        result = execute_intent(
            state=state,
            intent={
                "intent_id": intent_id,
                "process_id": "process.compartment_flow_tick",
                "inputs": {"graph_id": "interior.graph.mob10.alpha", "dt_ticks": 1},
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(auth),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(result.get("result", "")) != "complete":
            raise RuntimeError("flow tick failed")
        portal_row = next(
            (
                dict(row)
                for row in list(state.get("portal_flow_params") or [])
                if isinstance(row, dict) and str(row.get("portal_id", "")).strip() == "portal.mob10.cabin_hatch"
            ),
            {},
        )
        boundary = dict((dict(portal_row.get("extensions") or {})).get("field_boundary") or {})
        sample_position = dict(boundary.get("sample_position_mm") or {})
        return int(sample_position.get("x", 0) or 0)

    first_x = _sample_x("intent.mob10.interior.flow.sample.001")
    state = set_vehicle_position(state, vehicle_id=vehicle_id, x=300, y=0, z=0)
    second_x = _sample_x("intent.mob10.interior.flow.sample.002")

    if first_x != 125:
        return {"status": "fail", "message": "initial interior boundary sample position unexpected: {}".format(first_x)}
    if second_x != 325:
        return {"status": "fail", "message": "moved interior boundary sample position unexpected: {}".format(second_x)}
    if int(second_x - first_x) != 200:
        return {"status": "fail", "message": "interior sampling did not move with vehicle displacement"}
    return {"status": "pass", "message": "vehicle interior boundary sampling tracks vehicle motion deterministically"}

