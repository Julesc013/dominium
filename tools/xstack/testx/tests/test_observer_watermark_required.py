"""STRICT test: observer-truth watermark policy requires entitlement.observer.truth."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.observer_watermark_required"
TEST_TAGS = ["strict", "session", "view", "camera", "observation"]


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
                "lens_id": "lens.nondiegetic.debug",
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
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.view.watermark",
        "allowed_processes": ["process.camera_set_view_mode"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_set_view_mode": "entitlement.control.camera",
        },
        "process_privilege_requirements": {
            "process.camera_set_view_mode": "observer",
        },
        "allowed_lenses": ["lens.nondiegetic.debug"],
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
                    "view_mode_id": "view.test.observer_watermark",
                    "allowed_lens_ids": ["lens.nondiegetic.debug"],
                    "requires_embodiment": False,
                    "required_entitlements": ["entitlement.control.camera"],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": "watermark.observer.required",
                    "extensions": {"spectator_pattern": "observer_truth"},
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
                "intent_id": "intent.view.observer_mode.001",
                "process_id": "process.camera_set_view_mode",
                "inputs": {
                    "controller_id": "controller.alpha",
                    "camera_id": "camera.main",
                    "view_mode_id": "view.test.observer_watermark",
                    "target_type": "none",
                },
            }
        ],
        navigation_indices=copy.deepcopy(_navigation_indices()),
        policy_context={},
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "observer watermark mode without entitlement.observer.truth must refuse"}
    reason_code = str((dict(result.get("refusal") or {}).get("reason_code", "")))
    if reason_code != "refusal.view.watermark_required":
        return {"status": "fail", "message": "unexpected observer watermark refusal code '{}'".format(reason_code)}
    return {"status": "pass", "message": "observer watermark entitlement requirement check passed"}
