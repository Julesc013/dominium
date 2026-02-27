"""FAST test: MAT-9 inspection snapshot derivation is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.inspection_snapshot_deterministic"
TEST_TAGS = ["fast", "materials", "inspection", "determinism"]


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
        asset_id="asset.health.inspect.det",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=1_500,
        wear_by_mode={"failure.wear.general": 2_500},
    )
    law = law_profile(["process.inspect_generate_snapshot"])
    authority = authority_context(["entitlement.inspect"], privilege_level="observer")
    policy = policy_context()
    policy["inspection_cache_policy_id"] = "cache.off"
    policy["inspection_cache_policy_registry"] = {
        "policies": [
            {
                "cache_policy_id": "cache.off",
                "enable_caching": False,
                "invalidation_rules": [],
                "max_cache_entries": 0,
                "eviction_rule_id": "evict.none",
                "extensions": {},
            }
        ]
    }

    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.det.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.det", "desired_fidelity": "meso", "cost_units": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.det.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.inspect.det", "desired_fidelity": "meso", "cost_units": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspection snapshot determinism fixture refused unexpectedly"}
    if str(first.get("snapshot_hash", "")) != str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "inspection snapshot hash drifted for equivalent inputs"}
    first_snapshot = dict(first.get("inspection_snapshot") or {})
    second_snapshot = dict(second.get("inspection_snapshot") or {})
    if str(first_snapshot.get("deterministic_fingerprint", "")) != str(second_snapshot.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "inspection deterministic_fingerprint drifted for equivalent inputs"}
    return {"status": "pass", "message": "inspection snapshot determinism passed"}

