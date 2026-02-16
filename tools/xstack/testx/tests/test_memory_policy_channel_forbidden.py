"""STRICT test: forbidden channels never enter memory store items."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.epistemics.memory_policy_channel_forbidden"
TEST_TAGS = ["strict", "epistemics", "observation"]


def _truth() -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": 5},
            "agent_states": [
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.bravo"},
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 100, "y": 200, "z": 10},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.memory.allowed_only",
                }
            ],
        },
        "registry_payloads": {
            "decay_model_registry": {
                "decay_models": [
                    {
                        "decay_model_id": "ep.decay.session_basic",
                        "description": "test decay",
                        "ttl_rules": [
                            {"rule_id": "ttl.default", "channel_id": "*", "subject_kind": "*", "ttl_ticks": 30}
                        ],
                        "refresh_rules": [
                            {"rule_id": "refresh.default", "channel_id": "*", "subject_kind": "*", "refresh_on_observed": True}
                        ],
                        "eviction_rule_id": "evict.oldest_first",
                        "extensions": {},
                    }
                ]
            },
            "eviction_rule_registry": {
                "eviction_rules": [
                    {
                        "eviction_rule_id": "evict.oldest_first",
                        "description": "oldest",
                        "algorithm_id": "evict.oldest_first",
                        "priority_by_channel": {},
                        "priority_by_subject_kind": {},
                        "extensions": {},
                    }
                ]
            },
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    lens = {
        "lens_id": "lens.memory.allowed_only",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.core.time", "ch.camera.state"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.memory.allowed_only",
        "allowed_lenses": ["lens.memory.allowed_only"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.memory.allowed_only",
        "law_profile_id": "law.memory.allowed_only",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.memory.allowed_only", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.memory.allowed_only",
        "allowed_observation_channels": ["ch.core.time", "ch.camera.state"],
        "forbidden_channels": ["ch.core.entities"],
        "retention_policy_id": "ep.retention.session_basic",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1", "filter.quantize_precision.v1"],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.session_basic",
        "memory_allowed": True,
        "max_memory_items": 16,
        "decay_model_id": "ep.decay.session_basic",
        "eviction_rule_id": "evict.oldest_first",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }

    observed = observe_truth(
        truth_model=_truth(),
        lens=copy.deepcopy(lens),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        viewpoint_id="view.memory.allowed_only",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        memory_state={},
    )
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "observation refused unexpectedly for channel-allow fixture"}
    memory = dict((dict(observed.get("perceived_model") or {}).get("memory") or {}))
    items = list(memory.get("items") or [])
    channels = sorted(set(str((row or {}).get("channel_id", "")) for row in items if isinstance(row, dict)))
    if "ch.core.entities" in channels:
        return {"status": "fail", "message": "forbidden channel ch.core.entities leaked into memory store items"}
    if any(channel not in ("ch.camera.state", "ch.core.time") for channel in channels):
        return {"status": "fail", "message": "memory store contains channel outside allowed observation set"}
    return {"status": "pass", "message": "forbidden channels are excluded from memory items"}

