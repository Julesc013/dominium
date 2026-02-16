"""STRICT test: memory eviction order is deterministic under bounded capacity."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.epistemics.memory_eviction_deterministic"
TEST_TAGS = ["strict", "epistemics", "observation"]


def _truth() -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": 9},
            "agent_states": [
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.bravo"},
                {"entity_id": "entity.charlie"},
                {"entity_id": "entity.delta"},
            ],
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.memory.evict",
                }
            ],
            "process_log": [
                {"tick": 9, "process_id": "process.agent_move", "outcome": "complete"},
                {"tick": 9, "process_id": "process.time_pause", "outcome": "complete"},
            ],
        },
        "registry_payloads": {
            "decay_model_registry": {
                "decay_models": [
                    {
                        "decay_model_id": "ep.decay.session_basic",
                        "description": "test",
                        "ttl_rules": [{"rule_id": "ttl.default", "channel_id": "*", "subject_kind": "*", "ttl_ticks": 64}],
                        "refresh_rules": [{"rule_id": "refresh.default", "channel_id": "*", "subject_kind": "*", "refresh_on_observed": True}],
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


def _run_once(observe_truth) -> list[str]:
    lens = {
        "lens_id": "lens.memory.evict",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "observation_channels": ["ch.core.time", "ch.core.entities", "ch.core.process_log"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.memory.evict",
        "allowed_lenses": ["lens.memory.evict"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "profile.memory.evict",
        "law_profile_id": "law.memory.evict",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.memory.evict", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    epistemic_policy = {
        "epistemic_policy_id": "ep.policy.memory.evict",
        "allowed_observation_channels": ["ch.core.time", "ch.core.entities", "ch.core.process_log"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.session_basic",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
        "extensions": {},
    }
    retention_policy = {
        "retention_policy_id": "ep.retention.session_basic",
        "memory_allowed": True,
        "max_memory_items": 2,
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
        viewpoint_id="view.memory.evict",
        epistemic_policy=copy.deepcopy(epistemic_policy),
        retention_policy=copy.deepcopy(retention_policy),
        memory_state={},
    )
    if str(observed.get("result", "")) != "complete":
        return []
    memory = dict((dict(observed.get("perceived_model") or {}).get("memory") or {}))
    items = list(memory.get("items") or [])
    return [str((row or {}).get("memory_item_id", "")) for row in items if isinstance(row, dict)]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    first = _run_once(observe_truth=observe_truth)
    second = _run_once(observe_truth=observe_truth)
    if not first or not second:
        return {"status": "fail", "message": "eviction fixture refused unexpectedly"}
    if len(first) != 2 or len(second) != 2:
        return {"status": "fail", "message": "bounded eviction must cap memory item count to max_memory_items"}
    if first != second:
        return {"status": "fail", "message": "evicted memory item set differs across identical runs"}
    return {"status": "pass", "message": "deterministic memory eviction ordering check passed"}

