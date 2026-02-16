"""STRICT test: collision outcomes remain invariant across worker-count variation."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "testx.embodiment.thread_count_invariance_for_collision"
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
                "assembly_id": "body.left",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 300,
                    "height_mm": 1000,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": -900, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            },
            {
                "assembly_id": "body.right",
                "owner_assembly_id": "object.earth",
                "shape_type": "capsule",
                "shape_parameters": {
                    "radius_mm": 300,
                    "height_mm": 1000,
                    "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                    "vertex_ref_id": "",
                },
                "collision_layer": "layer.default",
                "dynamic": True,
                "ghost": False,
                "transform_mm": {"x": 900, "y": 0, "z": 0},
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


def _intents() -> list[dict]:
    return [
        {
            "intent_id": "intent.body_move.left.001",
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "body.left",
                "delta_transform_mm": {"x": 1200, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
        {
            "intent_id": "intent.body_move.right.001",
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "body.right",
                "delta_transform_mm": {"x": -1200, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.scheduler import replay_intent_script_srz

    base_state = _state()
    intents = _intents()
    common = {
        "repo_root": repo_root,
        "law_profile": _law_profile(),
        "authority_context": _authority_context(),
        "navigation_indices": {},
        "policy_context": {},
        "pack_lock_hash": "0" * 64,
        "registry_hashes": {},
        "logical_shards": 1,
    }
    workers_1 = replay_intent_script_srz(
        universe_state=copy.deepcopy(base_state),
        intents=copy.deepcopy(intents),
        worker_count=1,
        **common,
    )
    workers_2 = replay_intent_script_srz(
        universe_state=copy.deepcopy(base_state),
        intents=copy.deepcopy(intents),
        worker_count=2,
        **common,
    )
    if str(workers_1.get("result", "")) != "complete" or str(workers_2.get("result", "")) != "complete":
        return {"status": "fail", "message": "collision scheduler run failed for worker-count invariance check"}
    if str(workers_1.get("final_state_hash", "")) != str(workers_2.get("final_state_hash", "")):
        return {"status": "fail", "message": "collision final_state_hash changed across worker-count variation"}
    if list(workers_1.get("tick_hash_anchors") or []) != list(workers_2.get("tick_hash_anchors") or []):
        return {"status": "fail", "message": "collision tick_hash_anchors changed across worker-count variation"}
    if canonical_sha256(dict(workers_1.get("universe_state") or {})) != canonical_sha256(dict(workers_2.get("universe_state") or {})):
        return {"status": "fail", "message": "collision universe_state payload changed across worker-count variation"}
    return {"status": "pass", "message": "collision worker-count invariance check passed"}

