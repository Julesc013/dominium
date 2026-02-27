"""FAST test: maintenance process deterministically reduces backlog and wear."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.maintenance_reduces_backlog_deterministic"
TEST_TAGS = ["fast", "materials", "maintenance", "determinism"]


def _run_once() -> dict:
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
        asset_id="asset.health.maint",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=8_000,
        wear_by_mode={"failure.wear.general": 12_000},
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.maintenance.perform.001",
            "process_id": "process.maintenance_perform",
            "inputs": {
                "asset_id": "asset.health.maint",
                "reset_fraction_numerator": 1,
                "reset_fraction_denominator": 2,
                "required_materials": {},
            },
        },
        law_profile=law_profile(["process.maintenance_perform"]),
        authority_context=authority_context(["entitlement.control.admin"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(),
    )
    return {"result": result, "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "maintenance_perform must complete for valid asset inputs"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "maintenance_perform state hash anchor diverged"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "maintenance_perform mutated state non-deterministically"}

    rows = sorted(
        (dict(row) for row in list(first_state.get("asset_health_states") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("asset_id", "")),
    )
    if not rows:
        return {"status": "fail", "message": "maintenance_perform did not preserve asset health states"}
    row = dict(rows[0])
    backlog = int(row.get("maintenance_backlog", 0) or 0)
    wear = int((dict(row.get("accumulated_wear") or {})).get("failure.wear.general", 0) or 0)
    if backlog != 0:
        return {"status": "fail", "message": "maintenance_perform must clear backlog deterministically"}
    if wear >= 12_000:
        return {"status": "fail", "message": "maintenance_perform must reduce wear deterministically"}
    return {"status": "pass", "message": "maintenance backlog reduction determinism passed"}

