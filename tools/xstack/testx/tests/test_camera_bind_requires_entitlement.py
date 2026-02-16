"""STRICT test: camera binding requires entitlement.control.camera."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.camera_bind_requires_entitlement"
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
                "binding_id": None,
                "view_mode_id": "view.free.lab",
                "owner_peer_id": None,
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
        "law_profile_id": "law.test.view.entitlement",
        "allowed_processes": ["process.camera_bind_target"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_bind_target": "entitlement.control.camera",
        },
        "process_privilege_requirements": {
            "process.camera_bind_target": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "observer",
        "entitlements": ["session.boot"],
    }


def _navigation_indices() -> dict:
    return {
        "view_mode_registry": {
            "view_modes": [
                {
                    "view_mode_id": "view.free.lab",
                    "allowed_lens_ids": ["lens.diegetic.sensor"],
                    "requires_embodiment": False,
                    "required_entitlements": [],
                    "allowed_in_policies": ["lockstep", "authoritative", "hybrid"],
                    "watermark_policy_id": None,
                    "extensions": {"spectator_pattern": "orbit_body"},
                }
            ]
        },
    }


def _intent() -> dict:
    return {
        "intent_id": "intent.view.bind_camera.001",
        "process_id": "process.camera_bind_target",
        "inputs": {
            "controller_id": "controller.test",
            "camera_id": "camera.main",
            "target_type": "none",
            "view_mode_id": "view.free.lab",
        },
    }


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law()),
        authority_context=copy.deepcopy(_authority()),
        intents=[_intent()],
        navigation_indices=copy.deepcopy(_navigation_indices()),
        policy_context={},
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "refused" or str(second.get("result", "")) != "refused":
        return {"status": "fail", "message": "camera bind without entitlement.control.camera must refuse"}
    reason_first = str((dict(first.get("refusal") or {}).get("reason_code", "")))
    reason_second = str((dict(second.get("refusal") or {}).get("reason_code", "")))
    if reason_first != "refusal.control.entitlement_missing" or reason_second != "refusal.control.entitlement_missing":
        return {"status": "fail", "message": "unexpected refusal code for camera bind entitlement gating"}
    if dict(first.get("refusal") or {}) != dict(second.get("refusal") or {}):
        return {"status": "fail", "message": "camera bind entitlement refusal payload must be deterministic"}
    if int(first.get("script_step", -1)) != 0:
        return {"status": "fail", "message": "camera bind entitlement refusal must occur at script step 0"}
    return {"status": "pass", "message": "camera bind entitlement gating determinism check passed"}
