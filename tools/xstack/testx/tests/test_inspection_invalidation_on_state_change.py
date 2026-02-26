"""STRICT test: inspection cache invalidates when truth hash changes."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.inspection_invalidation_on_state_change"
TEST_TAGS = ["strict", "performance", "inspection", "determinism"]


def _law_profile():
    return {
        "law_profile_id": "law.test.performance.inspect.invalidate",
        "allowed_processes": ["process.inspect_generate_snapshot", "process.camera_move"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.inspect_generate_snapshot": "entitlement.inspect",
            "process.camera_move": "entitlement.camera_control",
        },
        "process_privilege_requirements": {
            "process.inspect_generate_snapshot": "observer",
            "process.camera_move": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"allow_hidden_state_access": True},
    }


def _authority():
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.performance.inspect.invalidate",
        "experience_id": "profile.test.performance.inspect.invalidate",
        "law_profile_id": "law.test.performance.inspect.invalidate",
        "entitlements": ["entitlement.inspect", "entitlement.camera_control"],
        "epistemic_scope": {"scope_id": "scope.test.performance.inspect.invalidate", "visibility_level": "nondiegetic"},
        "privilege_level": "observer",
    }


def _policy_context():
    return {
        "physics_profile_id": "physics.test.performance",
        "pack_lock_hash": "a" * 64,
        "budget_policy": {
            "policy_id": "policy.budget.inspect.invalidate",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": 0,
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.inspect.invalidate",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.inspect.invalidate",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": 0,
                    "max_inspection_cost_units_per_tick": 64,
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
            "intent_id": "intent.performance.inspect.invalidate.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "region.earth", "cost_units": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=None,
        policy_context=policy_context,
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "initial inspection snapshot refused unexpectedly"}

    moved = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.inspect.invalidate.002",
            "process_id": "process.camera_move",
            "inputs": {"delta_local_mm": {"x": 10, "y": 0, "z": 0}, "dt_ticks": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=None,
        policy_context=policy_context,
    )
    if str(moved.get("result", "")) != "complete":
        return {"status": "fail", "message": "camera move mutation refused unexpectedly"}

    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.inspect.invalidate.003",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "region.earth", "cost_units": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices=None,
        policy_context=policy_context,
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "second inspection snapshot refused unexpectedly"}
    if bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "inspection cache should miss after deterministic truth mutation"}
    if str(first.get("snapshot_hash", "")) == str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "snapshot hash did not change after truth mutation"}
    return {"status": "pass", "message": "inspection cache invalidation on truth change passed"}

