"""STRICT test: agent movement is deterministically blocked by collision substrate."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.embodiment.movement_collision_blocking"
TEST_TAGS = ["strict", "session", "embodiment", "movement", "collision"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.embodied_move",
        "allowed_processes": [
            "process.agent_move",
            "process.body_move_attempt",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.agent_move": "entitlement.agent.move",
            "process.body_move_attempt": "entitlement.control.possess",
        },
        "process_privilege_requirements": {
            "process.agent_move": "operator",
            "process.body_move_attempt": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "entitlement.agent.move",
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
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "state_hash": "0" * 64,
                "body_id": "body.agent.alpha",
                "owner_peer_id": "peer.alpha",
                "controller_id": "controller.alpha",
                "shard_id": "shard.0",
                "intent_scope_id": "",
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
        "controller_assemblies": [
            {
                "assembly_id": "controller.alpha",
                "controller_type": "script",
                "owner_peer_id": "peer.alpha",
                "allowed_actions": ["control.action.possess_agent"],
                "binding_ids": ["binding.control.possess.agent_alpha"],
                "status": "active",
            }
        ],
        "control_bindings": [
            {
                "binding_id": "binding.control.possess.agent_alpha",
                "controller_id": "controller.alpha",
                "binding_type": "possess",
                "target_id": "agent.alpha",
                "created_tick": 0,
                "active": True,
                "required_entitlements": ["entitlement.control.possess"],
            }
        ],
        "body_assemblies": [
            {
                "assembly_id": "body.agent.alpha",
                "owner_assembly_id": "agent.alpha",
                "owner_agent_id": "agent.alpha",
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
                "assembly_id": "body.obstacle.static",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 500,
                    "height_mm": 1200,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": False,
                "ghost": False,
                "transform_mm": {"x": 1800, "y": 0, "z": 0},
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

    state = copy.deepcopy(_state())
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.agent.move.collision.001",
            "process_id": "process.agent_move",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.alpha",
                "owner_peer_id": "peer.alpha",
                "move_vector_local": {"x": 1500, "y": 0, "z": 0},
                "speed_scalar": 1000,
                "tick_duration": 1,
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
        return {"status": "fail", "message": "movement collision test must complete"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "movement collision state hash anchor diverged across replay"}
    if first_state != second_state:
        return {"status": "fail", "message": "movement collision final state diverged across replay"}

    mover = {}
    for row in list(first_state.get("body_assemblies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")) == "body.agent.alpha":
            mover = dict(row)
            break
    if not mover:
        return {"status": "fail", "message": "movement collision test missing body.agent.alpha"}
    final_x = int((mover.get("transform_mm") or {}).get("x", 0) or 0)
    if final_x >= 1500:
        return {"status": "fail", "message": "collision blocking failed; mover reached full requested displacement"}
    if final_x > 800:
        return {"status": "fail", "message": "collision resolution exceeded expected static contact boundary"}
    return {"status": "pass", "message": "movement collision blocking determinism check passed"}
