"""STRICT test: player view mode blocks observer/non-player lens overrides."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.player_view_forbids_observer_lens"
TEST_TAGS = ["strict", "session", "view", "camera"]


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
                "binding_id": "binding.camera.test",
                "view_mode_id": "view.first_person.player",
                "owner_peer_id": "peer.alpha",
                "target_id": "body.agent.alpha",
                "target_type": "body",
                "offset_params": {"x_mm": 0, "y_mm": 0, "z_mm": 0, "yaw_mdeg": 0, "pitch_mdeg": 0, "roll_mdeg": 0},
            }
        ],
        "controller_assemblies": [],
        "control_bindings": [],
        "body_assemblies": [
            {
                "assembly_id": "body.agent.alpha",
                "owner_assembly_id": "agent.alpha",
                "owner_agent_id": "agent.alpha",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 500,
                    "height_mm": 1600,
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
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.view.player_lens",
        "allowed_processes": ["process.camera_set_lens"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_set_lens": "entitlement.control.lens_override",
        },
        "process_privilege_requirements": {
            "process.camera_set_lens": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
    }


def _authority() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "session.boot",
            "entitlement.control.lens_override",
            "lens.nondiegetic.access",
        ],
    }


def _navigation_indices() -> dict:
    return {
        "view_mode_registry": {
            "view_modes": [
                {
                    "view_mode_id": "view.first_person.player",
                    "allowed_lens_ids": ["lens.diegetic.sensor"],
                    "requires_embodiment": True,
                    "required_entitlements": ["entitlement.control.camera"],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": None,
                    "extensions": {"spectator_pattern": "none"},
                }
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script

    result = replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law()),
        authority_context=copy.deepcopy(_authority()),
        intents=[
            {
                "intent_id": "intent.view.set_lens.001",
                "process_id": "process.camera_set_lens",
                "inputs": {
                    "controller_id": "controller.alpha",
                    "camera_id": "camera.main",
                    "lens_id": "lens.nondiegetic.debug",
                },
            }
        ],
        navigation_indices=copy.deepcopy(_navigation_indices()),
        policy_context={},
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "player first-person view should refuse incompatible observer/nondiegetic lens"}
    reason_code = str((dict(result.get("refusal") or {}).get("reason_code", "")))
    if reason_code != "refusal.view.mode_forbidden":
        return {"status": "fail", "message": "unexpected player view lens refusal code '{}'".format(reason_code)}
    return {"status": "pass", "message": "player view mode lens restriction check passed"}
