"""STRICT test: ranked control policy forbids free camera view mode."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.ranked_profile_forbids_free_view"
TEST_TAGS = ["strict", "session", "view", "camera", "net"]


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
                "view_mode_id": "view.first_person.player",
                "owner_peer_id": "peer.alpha",
                "target_id": None,
                "target_type": "none",
                "offset_params": {"x_mm": 0, "y_mm": 0, "z_mm": 0, "yaw_mdeg": 0, "pitch_mdeg": 0, "roll_mdeg": 0},
            }
        ],
        "controller_assemblies": [],
        "control_bindings": [],
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.view.ranked",
        "allowed_processes": ["process.camera_set_view_mode"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_set_view_mode": "entitlement.control.camera",
        },
        "process_privilege_requirements": {
            "process.camera_set_view_mode": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
    }


def _authority() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "observer",
        "entitlements": ["session.boot", "entitlement.control.camera"],
    }


def _navigation_indices() -> dict:
    return {
        "view_mode_registry": {
            "view_modes": [
                {
                    "view_mode_id": "view.free.lab",
                    "allowed_lens_ids": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
                    "requires_embodiment": False,
                    "required_entitlements": ["entitlement.control.camera"],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": None,
                    "extensions": {"spectator_pattern": "orbit_body"},
                }
            ]
        },
    }


def _policy_context() -> dict:
    return {
        "replication_policy_id": "policy.net.server_authoritative",
        "control_policy": {
            "allowed_view_modes": [
                "view.first_person.player",
                "view.third_person.player",
                "view.follow.spectator",
            ],
            "allow_cross_shard_follow": False,
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
                "intent_id": "intent.view.ranked.free_refuse.001",
                "process_id": "process.camera_set_view_mode",
                "inputs": {
                    "controller_id": "controller.alpha",
                    "camera_id": "camera.main",
                    "view_mode_id": "view.free.lab",
                    "target_type": "none",
                },
            }
        ],
        navigation_indices=copy.deepcopy(_navigation_indices()),
        policy_context=copy.deepcopy(_policy_context()),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "ranked control policy should refuse view.free.lab"}
    reason_code = str((dict(result.get("refusal") or {}).get("reason_code", "")))
    if reason_code != "refusal.view.mode_forbidden":
        return {"status": "fail", "message": "unexpected ranked free-view refusal '{}'".format(reason_code)}
    return {"status": "pass", "message": "ranked control policy free-view refusal check passed"}
