"""STRICT test: embodied move/rotate sequence is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.embodiment.move_determinism"
TEST_TAGS = ["strict", "session", "embodiment", "movement"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.embodied_move",
        "allowed_processes": [
            "process.agent_move",
            "process.agent_rotate",
            "process.body_move_attempt",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.agent_move": "entitlement.agent.move",
            "process.agent_rotate": "entitlement.agent.rotate",
            "process.body_move_attempt": "entitlement.control.possess",
        },
        "process_privilege_requirements": {
            "process.agent_move": "operator",
            "process.agent_rotate": "operator",
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
            "entitlement.agent.rotate",
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
                "shard_id": "shard.0",
                "transform_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        ],
        "collision_state": {
            "last_tick_resolved_pairs": [],
            "last_tick_unresolved_pairs": [],
            "last_tick_pair_count": 0,
            "last_tick_anchor": "",
        },
    }


def _intents() -> list:
    return [
        {
            "intent_id": "intent.agent.rotate.001",
            "process_id": "process.agent_rotate",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.alpha",
                "yaw_delta": 90000,
            },
        },
        {
            "intent_id": "intent.agent.move.001",
            "process_id": "process.agent_move",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.alpha",
                "owner_peer_id": "peer.alpha",
                "move_vector_local": {"x": 1200, "y": 0, "z": 0},
                "speed_scalar": 1000,
                "tick_duration": 1,
            },
        },
        {
            "intent_id": "intent.agent.move.002",
            "process_id": "process.agent_move",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.alpha",
                "owner_peer_id": "peer.alpha",
                "move_vector_local": {"x": 0, "y": 800, "z": 0},
                "speed_scalar": 1000,
                "tick_duration": 1,
            },
        },
    ]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        intents=_intents(),
        navigation_indices={},
        policy_context={},
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "embodied move replay must complete"}

    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "embodied move final state hash diverged across replay"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "embodied move state hash anchors diverged across replay"}

    final_state = dict(first.get("universe_state") or {})
    body_rows = sorted(
        (dict(row) for row in list(final_state.get("body_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("assembly_id", "")),
    )
    body = {}
    for row in body_rows:
        if str(row.get("assembly_id", "")) == "body.agent.alpha":
            body = dict(row)
            break
    if not body:
        return {"status": "fail", "message": "embodied move final state missing body.agent.alpha"}
    transform = dict(body.get("transform_mm") or {})
    if int(transform.get("x", 0) or 0) == 0 and int(transform.get("y", 0) or 0) == 0:
        return {"status": "fail", "message": "embodied move sequence did not change body transform"}
    return {"status": "pass", "message": "embodied move replay determinism check passed"}
