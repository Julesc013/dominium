"""STRICT test: identical perceived streams yield identical memory store hashes."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.epistemics.memory_determinism"
TEST_TAGS = ["strict", "epistemics", "observation"]


def _truth(tick: int) -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": int(tick)},
            "agent_states": [
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.bravo"},
                {"entity_id": "entity.charlie"},
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 1200 + int(tick), "y": 20, "z": 5},
                    "orientation_mdeg": {"yaw": 10, "pitch": 20, "roll": 30},
                    "lens_id": "lens.memory.test",
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
                            {
                                "rule_id": "ttl.default",
                                "channel_id": "*",
                                "subject_kind": "*",
                                "ttl_ticks": 64,
                            }
                        ],
                        "refresh_rules": [
                            {
                                "rule_id": "refresh.default",
                                "channel_id": "*",
                                "subject_kind": "*",
                                "refresh_on_observed": True,
                            }
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
                        "description": "oldest first",
                        "algorithm_id": "evict.oldest_first",
                        "priority_by_channel": {},
                        "priority_by_subject_kind": {},
                        "extensions": {},
                    }
                ]
            },
        },
    }


def _observe_stream(observe_truth) -> tuple[list[str], dict]:
    lens = {
        "lens_id": "lens.memory.test",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.core.time", "ch.camera.state", "ch.core.entities"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 2},
    }
    law = {
        "law_profile_id": "law.memory.test",
        "allowed_lenses": ["lens.memory.test"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.memory.test",
        "law_profile_id": "law.memory.test",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.memory.test", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.memory.test",
        "allowed_observation_channels": ["ch.core.time", "ch.camera.state", "ch.core.entities"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.session_basic",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": [
            "filter.channel_allow_deny.v1",
            "filter.quantize_precision.v1",
            "filter.interest_cull.v1",
        ],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.session_basic",
        "memory_allowed": True,
        "max_memory_items": 64,
        "decay_model_id": "ep.decay.session_basic",
        "eviction_rule_id": "evict.oldest_first",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }
    memory_state = {}
    hashes: list[str] = []
    for tick in (1, 2, 3):
        observed = observe_truth(
            truth_model=_truth(tick=tick),
            lens=copy.deepcopy(lens),
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            viewpoint_id="view.memory.det",
            epistemic_policy=copy.deepcopy(epistemic_policy),
            retention_policy=copy.deepcopy(retention_policy),
            memory_state=copy.deepcopy(memory_state),
        )
        if str(observed.get("result", "")) != "complete":
            return [], {}
        perceived = dict(observed.get("perceived_model") or {})
        store_hash = str(((perceived.get("memory") or {}).get("store_hash", "")))
        hashes.append(store_hash)
        memory_state = dict(observed.get("memory_state") or {})
    return hashes, memory_state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    first_hashes, first_state = _observe_stream(observe_truth=observe_truth)
    second_hashes, second_state = _observe_stream(observe_truth=observe_truth)
    if not first_hashes or not second_hashes:
        return {"status": "fail", "message": "memory observation stream refused unexpectedly"}
    if first_hashes != second_hashes:
        return {"status": "fail", "message": "memory store hash sequence diverged for identical perceived streams"}
    if dict(first_state) != dict(second_state):
        return {"status": "fail", "message": "memory_state payload diverged for identical perceived streams"}
    return {"status": "pass", "message": "memory determinism hash sequence check passed"}

