"""FAST test: maintenance failure risk is quantized by epistemic visibility."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.epistemic_quantization_of_failure_risk"
TEST_TAGS = ["fast", "materials", "maintenance", "epistemic"]


def _risk_value(result: dict) -> int:
    snapshot = dict(result.get("inspection_snapshot") or {})
    target_payload = dict(snapshot.get("target_payload") or {})
    extensions = dict(target_payload.get("extensions") or {})
    risk_rows = list((dict(extensions.get("failure_risk_summary") or {})).get("risk_rows") or [])
    if not risk_rows:
        return -1
    first = dict(sorted((dict(row) for row in risk_rows if isinstance(row, dict)), key=lambda row: str(row.get("failure_mode_id", "")))[0])
    return int(first.get("risk_permille_quantized", -1) or -1)


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
        asset_id="asset.health.epistemic",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=0,
        wear_by_mode={"failure.wear.general": 3_750},
    )
    law = law_profile(["process.inspect_generate_snapshot"])
    policy = policy_context(failure_threshold_raw=10_000, failure_base_rate_raw=2_000)
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

    diegetic_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.inspect.epistemic.diegetic",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.epistemic", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(
            ["entitlement.inspect"],
            privilege_level="observer",
            visibility_level="diegetic",
        ),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    lab_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.inspect.epistemic.lab",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "asset.health.epistemic", "cost_units": 1},
        },
        law_profile=copy.deepcopy(law),
        authority_context=authority_context(
            ["entitlement.inspect"],
            privilege_level="observer",
            visibility_level="nondiegetic",
        ),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(diegetic_result.get("result", "")) != "complete" or str(lab_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "epistemic quantization inspect fixture refused unexpectedly"}

    diegetic_risk = _risk_value(dict(diegetic_result))
    lab_risk = _risk_value(dict(lab_result))
    if diegetic_risk < 0 or lab_risk < 0:
        return {"status": "fail", "message": "risk rows missing from maintenance inspection snapshot"}
    if diegetic_risk == lab_risk:
        return {"status": "fail", "message": "diegetic and lab risk quantization should differ for same asset"}
    if diegetic_risk % 200 != 0:
        return {"status": "fail", "message": "diegetic risk quantization step should be coarse (200 permille)"}
    if lab_risk % 50 != 0:
        return {"status": "fail", "message": "lab risk quantization step should follow policy extension (50 permille)"}
    return {"status": "pass", "message": "epistemic failure-risk quantization passed"}

