"""FAST test: MAT-9 inspection cache reuses snapshot for identical truth anchor + request profile."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.cache_reuse_same_anchor"
TEST_TAGS = ["fast", "materials", "inspection", "cache"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.maintenance_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_asset_health,
    )

    state = with_asset_health(
        base_state(),
        asset_id="asset.health.inspect.cache",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=900,
        wear_by_mode={"failure.wear.general": 1_100},
    )
    law = law_profile(["process.inspect_generate_snapshot"])
    authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    policy = policy_context()
    policy["inspection_cache_policy_id"] = "cache.default"
    policy["inspection_cache_policy_registry"] = {
        "policies": [
            {
                "cache_policy_id": "cache.default",
                "enable_caching": True,
                "invalidation_rules": ["invalidate.on_target_truth_hash_change"],
                "max_cache_entries": 32,
                "eviction_rule_id": "evict.deterministic_lru",
                "extensions": {},
            }
        ]
    }

    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.cache.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.cache", "desired_fidelity": "macro", "cost_units": 4},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.cache.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.cache", "desired_fidelity": "macro", "cost_units": 4},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspection cache reuse fixture refused unexpectedly"}
    if bool(first.get("cache_hit", False)):
        return {"status": "fail", "message": "first inspection snapshot should be a cache miss"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second inspection snapshot should be a cache hit"}
    if str(first.get("cache_key", "")) != str(second.get("cache_key", "")):
        return {"status": "fail", "message": "cache key drifted under identical truth anchor/request"}
    return {"status": "pass", "message": "inspection cache reuse under same anchor passed"}

