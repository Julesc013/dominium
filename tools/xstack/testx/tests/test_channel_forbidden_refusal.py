"""STRICT test: forbidden epistemic channel request refuses deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.channel_forbidden_refusal"
TEST_TAGS = ["strict", "net", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": {
            "simulation_time": {"tick": 0},
            "agent_states": [{"entity_id": "entity.alpha"}],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.test.forbidden",
                }
            ],
        }
    }
    lens = {
        "lens_id": "lens.test.forbidden",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": [
            "ch.camera.state",
            "ch.truth.overlay.terrain_height",
        ],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.test.player",
        "allowed_lenses": ["lens.test.forbidden"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.test",
        "law_profile_id": "law.test.player",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.player", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.player",
        "allowed_observation_channels": ["ch.camera.state"],
        "forbidden_channels": ["ch.truth.overlay.terrain_height"],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
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
        viewpoint_id="view.player",
        epistemic_policy=epistemic_policy,
        retention_policy=retention_policy,
    )
    if str(observed.get("result", "")) != "refused":
        return {"status": "fail", "message": "channel-forbidden scenario must refuse"}
    refusal_payload = dict(observed.get("refusal") or {})
    reason_code = str(refusal_payload.get("reason_code", ""))
    if reason_code != "refusal.ep.channel_forbidden":
        return {"status": "fail", "message": "unexpected refusal code '{}' for forbidden channel".format(reason_code)}
    return {"status": "pass", "message": "forbidden epistemic channel refusal is deterministic"}

