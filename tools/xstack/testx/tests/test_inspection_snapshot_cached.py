"""FAST test: maintenance inspection snapshots are cached deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.inspection_snapshot_cached"
TEST_TAGS = ["fast", "materials", "maintenance", "inspection", "cache"]


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
        asset_id="asset.health.inspect",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=2_000,
        wear_by_mode={"failure.wear.general": 3_200},
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
            "intent_id": "intent.maintenance.inspect.snapshot.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.inspect.snapshot.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspect_generate_snapshot should complete for maintenance asset"}
    if bool(first.get("cache_hit", False)):
        return {"status": "fail", "message": "first maintenance inspection snapshot should be cache miss"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second maintenance inspection snapshot should be cache hit"}
    if str(first.get("snapshot_hash", "")) != str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "maintenance inspection snapshot hash drifted under cache reuse"}
    snapshot = dict(second.get("inspection_snapshot") or {})
    target_payload = dict(snapshot.get("target_payload") or {})
    extensions = dict(target_payload.get("extensions") or {})
    risk_summary = dict(extensions.get("failure_risk_summary") or {})
    if not list(risk_summary.get("risk_rows") or []):
        return {"status": "fail", "message": "maintenance inspection snapshot missing quantized failure risk summary"}
    return {"status": "pass", "message": "maintenance inspection snapshot cache determinism passed"}
