"""STRICT test: perception-interest culling remains deterministic and stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.interest_policy_determinism"
TEST_TAGS = ["strict", "net", "observation"]


def _truth_fixture():
    return {
        "universe_state": {
            "simulation_time": {"tick": 11},
            "agent_states": [
                {"entity_id": "entity.zulu"},
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.echo"},
                {"entity_id": "entity.bravo"},
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.test.entities",
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
        "lens_id": "lens.test.entities",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.core.time", "ch.core.entities", "ch.camera.state"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.test.entities",
        "allowed_lenses": ["lens.test.entities"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.test.entities",
        "law_profile_id": "law.test.entities",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.entities", "visibility_level": "diegetic", "max_objects": 2},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.entities",
        "allowed_observation_channels": ["ch.core.time", "ch.core.entities", "ch.camera.state"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.interest_cull.v1",
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

    first = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.entities",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        perception_interest_limit=2,
    )
    second = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.entities",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        perception_interest_limit=2,
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "interest-cull observation unexpectedly refused"}
    if str(first.get("perceived_model_hash", "")) != str(second.get("perceived_model_hash", "")):
        return {"status": "fail", "message": "interest-cull perceived hash mismatch across identical inputs"}

    model = dict(first.get("perceived_model") or {})
    observed_entities = list(model.get("observed_entities") or [])
    if observed_entities != ["entity.alpha", "entity.bravo"]:
        return {
            "status": "fail",
            "message": "interest-cull selected entities must be deterministic sorted prefix (expected entity.alpha/entity.bravo)",
        }
    return {"status": "pass", "message": "perception-interest selection remains deterministic"}

