"""STRICT test: inspection snapshots are reused from deterministic cache when truth is unchanged."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.inspection_cache_reuse"
TEST_TAGS = ["strict", "performance", "inspection", "determinism"]


def _law_profile():
    return {
        "law_profile_id": "law.test.performance.inspect",
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.inspect_generate_snapshot": "entitlement.inspect",
        },
        "process_privilege_requirements": {
            "process.inspect_generate_snapshot": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"allow_hidden_state_access": True},
    }


def _authority():
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.performance.inspect",
        "experience_id": "profile.test.performance.inspect",
        "law_profile_id": "law.test.performance.inspect",
        "entitlements": ["entitlement.inspect"],
        "epistemic_scope": {"scope_id": "scope.test.performance.inspect", "visibility_level": "nondiegetic"},
        "privilege_level": "observer",
    }


def _policy_context():
    return {
        "physics_profile_id": "physics.test.performance",
        "pack_lock_hash": "a" * 64,
        "budget_policy": {
            "policy_id": "policy.budget.inspect",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": 0,
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.inspect",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.inspect",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": 0,
                    "max_inspection_cost_units_per_tick": 32,
                    "extensions": {},
                }
            ]
        },
        "inspection_cache_policy_id": "cache.default",
        "inspection_cache_policy_registry": {
            "policies": [
                {
                    "cache_policy_id": "cache.default",
                    "enable_caching": True,
                    "invalidation_rules": [
                        "invalidate.on_target_truth_hash_change",
                    ],
                    "max_cache_entries": 32,
                    "eviction_rule_id": "evict.deterministic_lru",
                    "extensions": {},
                }
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import base_state

    state = copy.deepcopy(base_state())
    law = _law_profile()
    authority = _authority()
    policy_context = _policy_context()

    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.inspect.reuse.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "region.earth", "cost_units": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=None,
        policy_context=policy_context,
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.inspect.reuse.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "region.earth", "cost_units": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=None,
        policy_context=policy_context,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspection cache reuse fixture refused unexpectedly"}
    if bool(first.get("cache_hit", False)):
        return {"status": "fail", "message": "first inspection snapshot should be a cache miss"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second inspection snapshot should be served from cache"}
    if str(first.get("snapshot_hash", "")) != str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "cached snapshot hash drifted for unchanged truth"}
    return {"status": "pass", "message": "inspection snapshot cache reuse passed"}

