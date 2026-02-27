"""FAST test: MAT-9 bounded history query produces deterministic event summaries."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.history_query_deterministic"
TEST_TAGS = ["fast", "materials", "inspection", "history", "determinism"]


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

    asset_id = "asset.health.inspect.history"
    state = with_asset_health(
        base_state(),
        asset_id=asset_id,
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=2_000,
        wear_by_mode={"failure.wear.general": 1_000},
    )
    law = law_profile(["process.inspection_perform", "process.inspect_generate_snapshot"])
    admin_authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    observer_authority = authority_context(["entitlement.inspect"], privilege_level="observer")
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

    inspected_asset = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.history.seed.001",
            "process_id": "process.inspection_perform",
            "inputs": {"asset_id": asset_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(admin_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(inspected_asset.get("result", "")) != "complete":
        return {"status": "fail", "message": "maintenance inspection seed step failed for history test"}

    inputs = {
        "target_id": asset_id,
        "desired_fidelity": "meso",
        "cost_units": 12,
        "time_range": {"start_tick": 0, "end_tick": 1_000},
    }
    first = execute_intent(
        state=state,
        intent={"intent_id": "intent.inspect.history.001", "process_id": "process.inspect_generate_snapshot", "inputs": dict(inputs)},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(observer_authority),
        navigation_indices={},
        policy_context=policy,
    )
    second = execute_intent(
        state=state,
        intent={"intent_id": "intent.inspect.history.002", "process_id": "process.inspect_generate_snapshot", "inputs": dict(inputs)},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(observer_authority),
        navigation_indices={},
        policy_context=policy,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "history inspection query refused unexpectedly"}
    if str(first.get("snapshot_hash", "")) != str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "history inspection snapshot hash drifted for equivalent inputs"}
    snapshot = dict(second.get("inspection_snapshot") or {})
    sections = dict(snapshot.get("summary_sections") or {})
    event_section = dict(sections.get("section.events_summary") or {})
    event_data = dict(event_section.get("data") or {})
    if int(event_data.get("event_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "history inspection did not report any bounded event summary rows"}
    return {"status": "pass", "message": "history inspection determinism passed"}

