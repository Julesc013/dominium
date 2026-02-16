"""STRICT test: capsule-capsule collision resolution is deterministic."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "testx.embodiment.capsule_capsule_collision_deterministic"
TEST_TAGS = ["strict", "session", "collision", "embodiment"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.collision",
        "allowed_processes": ["process.body_move_attempt"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.body_move_attempt": "entitlement.control.possess",
        },
        "process_privilege_requirements": {
            "process.body_move_attempt": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "entitlement.control.possess",
        ],
    }


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "history_anchors": [],
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "body_assemblies": [
            {
                "assembly_id": "body.a",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 500,
                    "height_mm": 1200,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            },
            {
                "assembly_id": "body.b",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 500,
                    "height_mm": 1200,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": 700, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            },
        ],
        "collision_state": {
            "last_tick_resolved_pairs": [],
            "last_tick_unresolved_pairs": [],
            "last_tick_pair_count": 0,
            "last_tick_anchor": "",
        },
    }


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.body_move.capsule_pair.001",
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "body.a",
                "delta_transform_mm": {"x": 400, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={},
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
        return {"status": "fail", "message": "capsule-capsule move attempt must complete deterministically"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if canonical_sha256(first_state) != canonical_sha256(second_state):
        return {"status": "fail", "message": "capsule-capsule final state hash diverged across identical runs"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "state hash anchor diverged for capsule-capsule deterministic run"}

    first_collision = dict(first_state.get("collision_state") or {})
    if "body.a::body.b" not in list(first_collision.get("last_tick_resolved_pairs") or []):
        return {"status": "fail", "message": "expected resolved pair body.a::body.b was not recorded"}
    if list(first_collision.get("last_tick_unresolved_pairs") or []):
        return {"status": "fail", "message": "capsule-capsule test should not leave unresolved overlap pairs"}

    first_bodies = sorted(
        (dict(row) for row in list(first_state.get("body_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("assembly_id", "")),
    )
    second_bodies = sorted(
        (dict(row) for row in list(second_state.get("body_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("assembly_id", "")),
    )
    if first_bodies != second_bodies:
        return {"status": "fail", "message": "capsule body transforms diverged across identical runs"}
    return {"status": "pass", "message": "capsule-capsule collision determinism check passed"}

