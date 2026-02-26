"""STRICT test: RS-5 cost accounting outputs are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.cost_accounting_deterministic"
TEST_TAGS = ["strict", "performance", "determinism"]


def _policy_context():
    from tools.xstack.testx.tests.cohort_testlib import policy_context_for_roi

    context = policy_context_for_roi(max_entities_micro=16, mapping_max_micro=16)
    context["physics_profile_id"] = "physics.test.performance"
    context["budget_envelope_id"] = "budget.test.cost"
    context["budget_envelope_registry"] = {
        "envelopes": [
            {
                "envelope_id": "budget.test.cost",
                "max_micro_entities_per_shard": 32,
                "max_micro_regions_per_shard": 8,
                "max_solver_cost_units_per_tick": 256,
                "max_inspection_cost_units_per_tick": 16,
                "extensions": {},
            }
        ]
    }
    context["arbitration_policy_id"] = "arb.equal_share"
    context["arbitration_policy_registry"] = {
        "policies": [
            {
                "arbitration_policy_id": "arb.equal_share",
                "mode": "equal_share",
                "weight_source": "none",
                "tie_break_rule_id": "tie.player_region_tick",
                "extensions": {},
            }
        ]
    }
    context["inspection_cache_policy_id"] = "cache.default"
    context["inspection_cache_policy_registry"] = {
        "policies": [
            {
                "cache_policy_id": "cache.default",
                "enable_caching": True,
                "invalidation_rules": [],
                "max_cache_entries": 64,
                "eviction_rule_id": "evict.deterministic_lru",
                "extensions": {},
            }
        ]
    }
    return context


def _run_once():
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, navigation_indices_for_roi

    state = copy.deepcopy(base_state())
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.cost.tick.001",
            "process_id": "process.region_management_tick",
            "inputs": {},
        },
        law_profile=law_profile(["process.region_management_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices=navigation_indices_for_roi(),
        policy_context=_policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return result
    return {
        "result": "complete",
        "state_hash_anchor": str(result.get("state_hash_anchor", "")),
        "cost_snapshot": dict(result.get("cost_snapshot") or {}),
        "budget_outcome": str(result.get("budget_outcome", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "cost accounting fixture refused unexpectedly"}
    if dict(first.get("cost_snapshot") or {}) != dict(second.get("cost_snapshot") or {}):
        return {"status": "fail", "message": "cost snapshot drifted across identical runs"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "state hash anchor drifted across identical runs"}
    if str(first.get("budget_outcome", "")) != str(second.get("budget_outcome", "")):
        return {"status": "fail", "message": "budget outcome drifted across identical runs"}
    return {"status": "pass", "message": "cost accounting determinism check passed"}

