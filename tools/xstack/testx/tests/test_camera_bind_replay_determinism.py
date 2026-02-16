"""STRICT test: camera bind/view replay emits deterministic hash anchors."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.camera_bind_replay_determinism"
TEST_TAGS = ["strict", "session", "view", "camera", "determinism"]


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
                "binding_id": None,
                "view_mode_id": "view.free.lab",
                "owner_peer_id": "peer.alpha",
                "target_id": None,
                "target_type": "none",
                "offset_params": {"x_mm": 0, "y_mm": 0, "z_mm": 0, "yaw_mdeg": 0, "pitch_mdeg": 0, "roll_mdeg": 0},
            }
        ],
        "controller_assemblies": [],
        "control_bindings": [],
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "state_hash": "0" * 64,
                "body_id": "",
                "owner_peer_id": "peer.alpha",
                "controller_id": "controller.alpha",
                "shard_id": "shard.0",
                "intent_scope_id": "",
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
        "body_assemblies": [],
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.view.replay",
        "allowed_processes": [
            "process.camera_bind_target",
            "process.camera_set_view_mode",
            "process.camera_unbind_target",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_bind_target": "entitlement.control.camera",
            "process.camera_set_view_mode": "entitlement.control.camera",
            "process.camera_unbind_target": "entitlement.control.camera",
        },
        "process_privilege_requirements": {
            "process.camera_bind_target": "observer",
            "process.camera_set_view_mode": "observer",
            "process.camera_unbind_target": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "observer",
        "entitlements": [
            "session.boot",
            "entitlement.control.camera",
            "entitlement.view.follow",
            "entitlement.view.spectator",
        ],
    }


def _navigation_indices() -> dict:
    return {
        "view_mode_registry": {
            "view_modes": [
                {
                    "view_mode_id": "view.free.lab",
                    "allowed_lens_ids": ["lens.diegetic.sensor"],
                    "requires_embodiment": False,
                    "required_entitlements": ["entitlement.control.camera"],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": None,
                    "extensions": {"spectator_pattern": "orbit_body"},
                },
                {
                    "view_mode_id": "view.follow.spectator",
                    "allowed_lens_ids": ["lens.diegetic.sensor"],
                    "requires_embodiment": False,
                    "required_entitlements": ["entitlement.view.follow", "entitlement.view.spectator"],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": None,
                    "extensions": {"spectator_pattern": "follow_agent"},
                },
            ]
        },
    }


def _intents() -> list:
    return [
        {
            "intent_id": "intent.view.bind.001",
            "process_id": "process.camera_bind_target",
            "inputs": {
                "controller_id": "controller.alpha",
                "camera_id": "camera.main",
                "target_type": "agent",
                "target_id": "agent.alpha",
                "view_mode_id": "view.follow.spectator",
            },
        },
        {
            "intent_id": "intent.view.mode.002",
            "process_id": "process.camera_set_view_mode",
            "inputs": {
                "controller_id": "controller.alpha",
                "camera_id": "camera.main",
                "view_mode_id": "view.free.lab",
                "target_type": "none",
            },
        },
        {
            "intent_id": "intent.view.unbind.003",
            "process_id": "process.camera_unbind_target",
            "inputs": {
                "controller_id": "controller.alpha",
                "camera_id": "camera.main",
            },
        },
    ]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law()),
        authority_context=copy.deepcopy(_authority()),
        intents=copy.deepcopy(_intents()),
        navigation_indices=copy.deepcopy(_navigation_indices()),
        policy_context={},
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "camera bind replay should complete for deterministic fixture"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "camera bind replay final state hash diverged"}
    first_anchors = list(first.get("state_hash_anchors") or [])
    second_anchors = list(second.get("state_hash_anchors") or [])
    if first_anchors != second_anchors:
        return {"status": "fail", "message": "camera bind replay state hash anchors diverged"}
    if len(first_anchors) != 3:
        return {"status": "fail", "message": "camera bind replay expected exactly 3 state hash anchors"}
    return {"status": "pass", "message": "camera bind replay determinism check passed"}
