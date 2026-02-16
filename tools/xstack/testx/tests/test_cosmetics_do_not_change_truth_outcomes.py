"""STRICT test: cosmetic assignments stay representation-only and do not change truth hash outcomes."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.representation.cosmetics_do_not_change_truth_outcomes"
TEST_TAGS = ["strict", "session", "representation", "cosmetics"]


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
                "allowed_actions": ["control.action.possess_agent", "control.action.assign_cosmetic"],
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


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.representation.cosmetics",
        "allowed_processes": [
            "process.cosmetic_assign",
            "process.agent_move",
            "process.body_move_attempt",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.cosmetic_assign": "entitlement.cosmetic.assign",
            "process.agent_move": "entitlement.agent.move",
            "process.body_move_attempt": "entitlement.control.possess",
        },
        "process_privilege_requirements": {
            "process.cosmetic_assign": "operator",
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
            "session.boot",
            "entitlement.cosmetic.assign",
            "entitlement.agent.move",
            "entitlement.control.possess",
        ],
    }


def _policy_context() -> dict:
    return {
        "cosmetic_policy_id": "policy.cosmetics.private_relaxed",
        "cosmetic_registry": {
            "cosmetics": [
                {
                    "cosmetic_id": "cosmetic.default.pill",
                    "render_proxy_id": "render.proxy.pill_default",
                    "extensions": {"pack_id": "pack.representation.base"},
                },
                {
                    "cosmetic_id": "cosmetic.humanoid.lowpoly.default",
                    "render_proxy_id": "render.proxy.humanoid_lowpoly",
                    "extensions": {"pack_id": "pack.representation.base"},
                },
            ]
        },
        "cosmetic_policy_registry": {
            "policies": [
                {
                    "policy_id": "policy.cosmetics.private_relaxed",
                    "allow_unsigned_packs": True,
                    "require_signed_packs": False,
                    "allowed_cosmetic_ids": [],
                    "allowed_pack_ids": [],
                    "extensions": {},
                }
            ]
        },
        "resolved_packs": [
            {"pack_id": "pack.representation.base", "signature_status": "unsigned"},
        ],
        "representation_state": {"assignments": {}, "events": []},
    }


def _run_once(cosmetic_id: str):
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law_profile()),
        authority_context=copy.deepcopy(_authority_context()),
        intents=[
            {
                "intent_id": "intent.cosmetic.assign.{}".format(str(cosmetic_id)),
                "process_id": "process.cosmetic_assign",
                "inputs": {"agent_id": "agent.alpha", "cosmetic_id": str(cosmetic_id)},
            },
            {
                "intent_id": "intent.agent.move.001",
                "process_id": "process.agent_move",
                "inputs": {
                    "agent_id": "agent.alpha",
                    "controller_id": "controller.alpha",
                    "owner_peer_id": "peer.alpha",
                    "move_vector_local": {"x": 1000, "y": 0, "z": 0},
                    "speed_scalar": 1000,
                    "tick_duration": 1,
                },
            },
        ],
        navigation_indices={},
        policy_context=copy.deepcopy(_policy_context()),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once("cosmetic.default.pill")
    second = _run_once("cosmetic.humanoid.lowpoly.default")

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "cosmetic truth-outcome test replay did not complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "cosmetic variation changed final truth state hash"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "cosmetic variation changed truth state hash anchors"}
    return {"status": "pass", "message": "cosmetic variation leaves truth outcomes unchanged"}

