"""STRICT test: deterministic epistemic filter pipeline for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.epistemic_filter_determinism"
TEST_TAGS = ["strict", "net", "observation"]


def _truth_fixture():
    return {
        "universe_state": {
            "simulation_time": {"tick": 7},
            "agent_states": [
                {"entity_id": "entity.gamma"},
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.beta"},
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 1234, "y": 567, "z": 89},
                    "orientation_mdeg": {"yaw": 110, "pitch": 220, "roll": 330},
                    "lens_id": "lens.diegetic.sensor",
                }
            ],
        }
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = _truth_fixture()
    lens = {
        "lens_id": "lens.diegetic.sensor",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
        ],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 2},
    }
    law = {
        "law_profile_id": "law.test.ep",
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.test",
        "law_profile_id": "law.test.ep",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.test.det",
        "allowed_observation_channels": [
            "ch.core.time",
            "ch.camera.state",
            "ch.diegetic.compass",
            "ch.diegetic.clock",
        ],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.test.det",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [
            {
                "rule_id": "camera.default",
                "channel_id": "ch.camera.state",
                "max_distance_mm": 1000000000,
                "position_quantization_mm": 5,
                "orientation_quantization_mdeg": 5,
            }
        ],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.precision_quantize.v1",
            "filter.interest_cull.v1",
        ],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.test.det",
        "memory_allowed": True,
        "max_memory_items": 8,
        "decay_model_id": "none",
        "deterministic_eviction_rule_id": "evict.tick_channel_hash",
        "extensions": {},
    }
    memory_state = {"entries": []}

    first = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.client.det",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        memory_state=copy.deepcopy(memory_state),
        perception_interest_limit=2,
    )
    second = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.client.det",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        memory_state=copy.deepcopy(memory_state),
        perception_interest_limit=2,
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "epistemic observation unexpectedly refused for deterministic fixture"}
    if str(first.get("perceived_model_hash", "")) != str(second.get("perceived_model_hash", "")):
        return {"status": "fail", "message": "epistemic filter produced hash mismatch across identical inputs"}
    if dict(first.get("perceived_model") or {}) != dict(second.get("perceived_model") or {}):
        return {"status": "fail", "message": "epistemic filter produced payload mismatch across identical inputs"}
    if dict(first.get("memory_state") or {}) != dict(second.get("memory_state") or {}):
        return {"status": "fail", "message": "retention memory_state mismatch across identical observation inputs"}

    return {"status": "pass", "message": "epistemic filter determinism check passed"}

