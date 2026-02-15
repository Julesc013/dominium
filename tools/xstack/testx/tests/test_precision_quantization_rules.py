"""STRICT test: epistemic precision quantization applies deterministic distance rules."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.precision_quantization_rules"
TEST_TAGS = ["strict", "net", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": {
            "simulation_time": {"tick": 9},
            "agent_states": [{"entity_id": "entity.alpha"}],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 12345, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 123, "pitch": 12, "roll": 6},
                    "lens_id": "lens.test.quantized",
                }
            ],
        }
    }
    lens = {
        "lens_id": "lens.test.quantized",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.camera.state", "ch.core.time"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.test.quantized",
        "allowed_lenses": ["lens.test.quantized"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.test",
        "law_profile_id": "law.test.quantized",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.quantized", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.quantized",
        "allowed_observation_channels": ["ch.camera.state", "ch.core.time"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [
            {
                "rule_id": "near",
                "channel_id": "ch.camera.state",
                "max_distance_mm": 1000,
                "position_quantization_mm": 1,
                "orientation_quantization_mdeg": 1,
            },
            {
                "rule_id": "far",
                "channel_id": "ch.camera.state",
                "max_distance_mm": 1000000000,
                "position_quantization_mm": 100,
                "orientation_quantization_mdeg": 50,
            },
        ],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.precision_quantize.v1",
        ],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "none",
        "deterministic_eviction_rule_id": "evict.none",
        "extensions": {},
    }

    observed = observe_truth(
        truth_model=truth,
        lens=lens,
        law_profile=law,
        authority_context=authority,
        viewpoint_id="view.quantized",
        epistemic_policy=epistemic_policy,
        retention_policy=retention_policy,
    )
    if str(observed.get("result", "")) != "complete":
        reason = str(((observed.get("refusal") or {}).get("reason_code", "")) if isinstance(observed, dict) else "")
        return {"status": "fail", "message": "quantization observation refused ({})".format(reason)}

    camera = dict((dict(observed.get("perceived_model") or {}).get("camera_viewpoint") or {}))
    position = dict(camera.get("position_mm") or {})
    orientation = dict(camera.get("orientation_mdeg") or {})
    if int(position.get("x", -1)) != 12300:
        return {"status": "fail", "message": "expected far-distance x quantization to 12300 mm"}
    if int(orientation.get("yaw", -1)) != 100:
        return {"status": "fail", "message": "expected far-distance yaw quantization to 100 mdeg"}
    return {"status": "pass", "message": "precision quantization rules applied deterministically"}

