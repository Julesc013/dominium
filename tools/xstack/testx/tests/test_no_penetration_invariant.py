"""STRICT test: strict contract mode refuses unresolved no-penetration violations."""

from __future__ import annotations

import sys


TEST_ID = "testx.embodiment.no_penetration_invariant"
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
                "assembly_id": "body.static.left",
                "owner_assembly_id": "object.earth",
                "shape_type": "aabb",
                "shape_parameters": {
                    "radius_mm": 0,
                    "height_mm": 0,
                    "half_extents_mm": {"x": 800, "y": 800, "z": 800},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": False,
                "ghost": False,
                "transform_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            },
            {
                "assembly_id": "body.static.right",
                "owner_assembly_id": "object.earth",
                "shape_type": "aabb",
                "shape_parameters": {
                    "radius_mm": 0,
                    "height_mm": 0,
                    "half_extents_mm": {"x": 800, "y": 800, "z": 800},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": False,
                "ghost": False,
                "transform_mm": {"x": 200, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            },
            {
                "assembly_id": "body.dynamic.mover",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 200,
                    "height_mm": 600,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": -2000, "y": 0, "z": 0},
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.body_move.strict_no_penetration.001",
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "body.dynamic.mover",
                "delta_transform_mm": {"x": 1000, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={"strict_contracts": True},
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "strict no-penetration mode must refuse unresolved overlaps"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.contract.no_penetration_violation":
        return {"status": "fail", "message": "expected refusal.contract.no_penetration_violation reason code"}
    return {"status": "pass", "message": "strict no-penetration contract refusal check passed"}

