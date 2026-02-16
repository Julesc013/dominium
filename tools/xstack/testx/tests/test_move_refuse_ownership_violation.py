"""STRICT test: process.agent_move refuses ownership violations deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.embodiment.move_refuse_ownership_violation"
TEST_TAGS = ["strict", "session", "embodiment", "movement"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.embodied_move",
        "allowed_processes": ["process.agent_move"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.agent_move": "entitlement.agent.move",
        },
        "process_privilege_requirements": {
            "process.agent_move": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "entitlement.agent.move",
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
                "owner_peer_id": "peer.owner",
                "controller_id": "controller.beta",
                "shard_id": "shard.0",
                "intent_scope_id": "",
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
        "controller_assemblies": [
            {
                "assembly_id": "controller.beta",
                "controller_type": "script",
                "owner_peer_id": "peer.other",
                "allowed_actions": ["control.action.possess_agent"],
                "binding_ids": ["binding.control.possess.agent_alpha"],
                "status": "active",
            }
        ],
        "control_bindings": [
            {
                "binding_id": "binding.control.possess.agent_alpha",
                "controller_id": "controller.beta",
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


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = copy.deepcopy(_state())
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.agent.move.ownership.001",
            "process_id": "process.agent_move",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.beta",
                "owner_peer_id": "peer.other",
                "move_vector_local": {"x": 500, "y": 0, "z": 0},
                "tick_duration": 1,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={},
    )
    return result


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "refused" or str(second.get("result", "")) != "refused":
        return {"status": "fail", "message": "ownership-violating movement should deterministically refuse"}

    refusal_first = dict(first.get("refusal") or {})
    refusal_second = dict(second.get("refusal") or {})
    if str(refusal_first.get("reason_code", "")) != "refusal.agent.ownership_violation":
        return {"status": "fail", "message": "expected refusal.agent.ownership_violation for ownership mismatch"}
    if refusal_first != refusal_second:
        return {"status": "fail", "message": "ownership violation refusal payload must be deterministic"}
    return {"status": "pass", "message": "ownership violation movement refusal determinism check passed"}
